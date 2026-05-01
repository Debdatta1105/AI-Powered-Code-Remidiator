import os
import json
from dotenv import load_dotenv
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.exceptions import OutputParserException
from langchain_core.tools import tool

import mcp_server

load_dotenv()

# Check demo mode
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

def get_secret(key, default=None):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)

# Initialize LLM
llm = ChatGroq(
    temperature=0, 
    groq_api_key=get_secret("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile"
)

# ============================================================================
# MCP Tools as LangChain Tools
# ============================================================================

@tool
def list_jenkins_jobs() -> str:
    """List all available Jenkins jobs"""
    result = mcp_server.call_tool("list_jenkins_jobs", {})
    return json.dumps(result)

@tool
def get_jenkins_logs(job_name: str, build_number: int) -> str:
    """Fetch Jenkins build console logs for analysis"""
    result = mcp_server.call_tool("get_jenkins_logs", {
        "job_name": job_name,
        "build_number": build_number
    })
    return json.dumps(result)

@tool
def get_last_failed_build(job_name: str) -> str:
    """Get the last failed build for a job"""
    result = mcp_server.call_tool("get_last_failed_build", {"job_name": job_name})
    return json.dumps(result)

@tool
def trigger_jenkins_build(job_name: str) -> str:
    """Trigger a new Jenkins build"""
    result = mcp_server.call_tool("trigger_jenkins_build", {"job_name": job_name})
    return json.dumps(result)

@tool
def read_file(path: str) -> str:
    """Read contents of a file from local repository"""
    result = mcp_server.call_tool("read_file", {"path": path})
    return json.dumps(result)

@tool
def write_file(path: str, content: str) -> str:
    """Write or modify a file"""
    result = mcp_server.call_tool("write_file", {"path": path, "content": content})
    return json.dumps(result)

@tool
def create_pr_with_fix(fix_data: dict) -> str:
    """Create a GitHub PR with the auto fix"""
    result = mcp_server.call_tool("create_pr_with_fix", {"fix_data": fix_data})
    return json.dumps(result)

# Tools list for agent
tools = [
    list_jenkins_jobs,
    get_jenkins_logs,
    get_last_failed_build,
    trigger_jenkins_build,
    read_file,
    write_file,
    create_pr_with_fix
]

# Create agent prompt
system_prompt = """You are an autonomous CI/CD remediation agent. Your goal is to:
1. Analyze Jenkins build failures
2. Identify root causes
3. Generate and apply fixes
4. Create GitHub Pull Requests automatically

When given a job to fix:
- First, get the last failed build info
- Fetch the console logs
- Analyze the failure type (compile error, test failure, dependency issue, etc.)
- Determine the fix by reading relevant source files
- Apply the fix
- Create a PR with the changes

Always be thorough and methodical. Use tools to gather information before making decisions.

Available tools:
- list_jenkins_jobs: List all available Jenkins jobs
- get_jenkins_logs(job_name, build_number): Fetch Jenkins build console logs
- get_last_failed_build(job_name): Get the last failed build for a job
- trigger_jenkins_build(job_name): Trigger a new Jenkins build
- read_file(path): Read file from local repository
- write_file(path, content): Write file to local repository
- create_pr_with_fix(fix_data): Create GitHub PR with fix"""

# ============================================================================
# Simplified Agent Loop
# ============================================================================

def run_agent(instruction: str) -> dict:
    """Run agent with manual tool calling loop"""
    from langchain_core.messages import HumanMessage, AIMessage
    
    messages = [
        HumanMessage(content=system_prompt),
        HumanMessage(content=instruction)
    ]
    
    max_iterations = 10
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        # Get LLM response
        response = llm.invoke(messages)
        messages.append(AIMessage(content=response.content))
        
        # Check if we're done
        if "final result" in response.content.lower() or "complete" in response.content.lower():
            return {
                "status": "complete",
                "result": response.content,
                "iterations": iteration
            }
        
        # Simple tool detection (if needed in future)
        # For now, just return the response
        if iteration >= 3:
            break
    
    return {
        "status": "complete",
        "result": response.content,
        "iterations": iteration
    }

# ============================================================================
# Fix Generation Helper
# ============================================================================

def generate_fix_from_logs(logs: str) -> dict:
    """Generate properly structured fix data from build logs"""
    prompt = f"""Analyze this Jenkins build failure and generate a fix.

JENKINS BUILD LOGS:
{logs[:5000]}

Return ONLY valid JSON with this exact structure (no markdown, no extra text):

{{
"failure_type": "compilation error|test failure|dependency issue|configuration error|other",
"root_cause": "clear explanation of why this failed",
"can_auto_fix": true,
"target_file": "path/to/file/that/needs/fixing.java",
"target_line": 42,
"operation": "insert|replace|delete|modify",
"match_text": "the exact line or text to find",
"code_patch": "the corrected code",
"pr_title": "Fix: Brief title of the fix",
"pr_body": "Detailed explanation of what was wrong and how this fixes it"
}}

RULES:
- ALWAYS set "can_auto_fix" to true if you can confidently suggest a fix
- Determine the correct operation:
  - "insert" → adding new code line
  - "replace" → modifying existing code line
  - "delete" → removing incorrect code line
  - "modify"  → update part of an existing line (preferred for small fixes)
- match_text must be something that will actually appear in the file
- code_patch should be the corrected version
- Be specific and precise"""
    
    try:
        response = llm.invoke(prompt)
        response_text = response.content.strip()
        
        # Remove markdown code blocks if present
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        # Parse as JSON
        fix_data = json.loads(response_text)
        
        # Ensure can_auto_fix is boolean
        if "can_auto_fix" not in fix_data:
            fix_data["can_auto_fix"] = True
        
        return fix_data
    except json.JSONDecodeError as e:
        return {
            "failure_type": "unknown",
            "root_cause": "Could not parse LLM response",
            "can_auto_fix": False,
            "error": str(e),
            "raw_response": response_text if 'response_text' in locals() else ""
        }
    except Exception as e:
        return {
            "failure_type": "unknown",
            "root_cause": str(e),
            "can_auto_fix": False,
            "error": str(e)
        }

# ============================================================================
# High-level Agent Functions
# ============================================================================

def explain_build_failure(job_name: str, build_number: int) -> dict:
    """Explain why a build failed using the agent"""
    
    # Get the build logs
    logs_result = mcp_server.call_tool("get_jenkins_logs", {
        "job_name": job_name,
        "build_number": build_number
    })
    
    if not logs_result.get("success"):
        return {
            "analysis": f"Could not fetch logs: {logs_result.get('error')}"
        }
    
    logs = logs_result.get("logs", "")
    
    # Analyze with LLM
    prompt = f"""Analyze this Jenkins build failure and explain what went wrong.

BUILD LOGS:
{logs[:5000]}

Provide a clear, concise explanation of:
1. What the error is
2. Why it occurred
3. What needs to be fixed"""
    
    response = llm.invoke(prompt)
    
    return {
        "analysis": response.content
    }

def suggest_and_apply_fix(job_name: str, build_number: int) -> dict:
    """Full autonomous fix generation and PR creation"""
    
    # First, get the build logs
    logs_result = mcp_server.call_tool("get_jenkins_logs", {
        "job_name": job_name,
        "build_number": build_number
    })
    
    if not logs_result.get("success"):
        return {
            "success": False,
            "error": f"Could not fetch logs: {logs_result.get('error')}"
        }
    
    logs = logs_result.get("logs", "")
    
    # Generate fix from logs
    fix_data = generate_fix_from_logs(logs)
    
    return fix_data

def auto_fix_job(job_name: str) -> dict:
    """One-shot: fix the last failed build and trigger a new build"""
    
    # Get last failed build
    build_result = mcp_server.call_tool("get_last_failed_build", {"job_name": job_name})
    
    if not build_result.get("success"):
        return {
            "success": False,
            "error": f"No failed build found: {build_result.get('error')}"
        }
    
    build_number = build_result.get("build", {}).get("number")
    
    # Get logs
    logs_result = mcp_server.call_tool("get_jenkins_logs", {
        "job_name": job_name,
        "build_number": build_number
    })
    
    if not logs_result.get("success"):
        return {
            "success": False,
            "error": f"Could not fetch logs: {logs_result.get('error')}"
        }
    
    logs = logs_result.get("logs", "")
    
    # Generate fix
    fix_data = generate_fix_from_logs(logs)
    
    if not fix_data.get("can_auto_fix"):
        return {
            "success": False,
            "message": "Could not auto-fix this build",
            "root_cause": fix_data.get("root_cause"),
            "error": fix_data.get("error")
        }
    
    # Create PR
    pr_result = mcp_server.call_tool("create_pr_with_fix", {"fix_data": fix_data})
    
    if not pr_result.get("success"):
        return {
            "success": False,
            "error": f"PR creation failed: {pr_result.get('error')}"
        }
    
    # Trigger new build
    trigger_result = mcp_server.call_tool("trigger_jenkins_build", {"job_name": job_name})
    
    return {
        "success": True,
        "build_number": build_number,
        "fix": fix_data,
        "pr_result": pr_result,
        "build_triggered": trigger_result.get("success", False)
    }


if __name__ == "__main__":
    # Example: Auto-fix a failed build
    print("=" * 80)
    print("Starting autonomous CI/CD fix agent...")
    print("=" * 80)
    
    job_name = "JavaCompileTest"
    
    # One-shot fix: Get last failed build, analyze, fix, and trigger new build
    result = auto_fix_job(job_name)
    
    print("\n" + "=" * 80)
    print("Agent completed. Result:")
    print("=" * 80)
    print(json.dumps(result, indent=2))

