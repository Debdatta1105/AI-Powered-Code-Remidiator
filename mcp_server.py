"""
MCP Server for AI Compiler - Exposes Jenkins, GitHub, and File System tools
"""

import os
import json
from typing import Any
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jenkins import JenkinsClient
from generate_pr import create_auto_fix_pr

load_dotenv()

# ============================================================================
# Demo Mode Configuration
# ============================================================================

# Can be overridden at runtime via set_demo_mode()
_demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"

def set_demo_mode(enabled: bool):
    """Enable or disable demo mode at runtime"""
    global _demo_mode
    _demo_mode = enabled
    print(f"Demo mode: {'🎮 ENABLED' if enabled else '🔌 DISABLED'}")

def get_demo_mode() -> bool:
    """Get current demo mode status"""
    return _demo_mode

DEMO_MODE = _demo_mode

# Simulated Jenkins data
DEMO_JOBS = [
    {"name": "JavaCompileTest", "url": "http://localhost:8080/job/JavaCompileTest/"},
    {"name": "PythonUnitTests", "url": "http://localhost:8080/job/PythonUnitTests/"},
    {"name": "DeploymentPipeline", "url": "http://localhost:8080/job/DeploymentPipeline/"},
]

DEMO_FAILED_BUILD = {
    "number": 42,
    "result": "FAILURE",
    "timestamp": int((datetime.now() - timedelta(hours=2)).timestamp() * 1000),
    "duration": 125000,
    "url": "http://localhost:8080/job/JavaCompileTest/42/"
}

DEMO_BUILD_LOGS = """
Started by user Jenkins
Building on master in workspace /var/lib/jenkins/workspace/JavaCompileTest
...
[INFO] Building project v1.2.3
[INFO] Compiling sources
[ERROR] COMPILATION ERROR :
[ERROR] /var/lib/jenkins/workspace/JavaCompileTest/src/main/java/com/example/Calculator.java:[15,8] incompatible types: java.lang.String cannot be converted to int
[ERROR] The following errors occurred during build:
[ERROR] 1 error
[ERROR]
[ERROR] EXIT CODE 1

COMPILATION FAILED. Error at line 15:
public int add(String a, int b) {
           ^
Expected: public int add(int a, int b)
Reason: Parameter 'a' should be int, not String
"""

# Simulated files
DEMO_FILES = {
    "src/main/java/com/example/Calculator.java": """package com.example;

public class Calculator {
    public int add(String a, int b) {  // LINE 15: BUG - should be 'int a' not 'String a'
        return a + b;
    }
    
    public int subtract(int a, int b) {
        return a - b;
    }
}
""",
    "pom.xml": """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>calculator</artifactId>
    <version>1.2.3</version>
</project>
"""
}

# ============================================================================
# Tool Implementations
# ============================================================================

def get_secret(key, default=None):
    """Get secret from environment"""
    return os.getenv(key, default)


class ToolImplementations:
    """Tool implementations for MCP server"""

    def __init__(self):
        self.demo_mode = get_demo_mode()  # Get current demo mode status
        self.jenkins_client = None  # Lazy initialization
        self._init_jenkins_client()

    def _init_jenkins_client(self):
        """Initialize Jenkins client if needed"""
        if not self.demo_mode and self.jenkins_client is None:
            try:
                self.jenkins_client = JenkinsClient(
                    url=get_secret("JENKINS_URL", "http://localhost:8080"),
                    username=get_secret("JENKINS_USERNAME"),
                    token=get_secret("API_TOKEN")
                )
            except Exception as e:
                print(f"[ERROR] Failed to initialize Jenkins client: {e}")
                self.jenkins_client = None

    def _check_demo_mode(self):
        """Update demo mode status and reinitialize Jenkins client if needed"""
        old_demo_mode = self.demo_mode
        self.demo_mode = get_demo_mode()
        
        # If mode changed, update Jenkins client
        if old_demo_mode != self.demo_mode:
            if not self.demo_mode:
                # Switched to production mode
                self._init_jenkins_client()
            else:
                # Switched to demo mode
                self.jenkins_client = None

    # ========================================================================
    # Jenkins Tools
    # ========================================================================

    def list_jenkins_jobs(self) -> dict:
        """List all Jenkins jobs"""
        self._check_demo_mode()
        if self.demo_mode:
            return {
                "success": True,
                "jobs": DEMO_JOBS
            }
        if not self.jenkins_client:
            return {
                "success": False,
                "error": "Jenkins client not initialized. Check your configuration."
            }
        try:
            jobs = self.jenkins_client.get_jobs()
            return {
                "success": True,
                "jobs": jobs
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_jenkins_logs(self, job_name: str, build_number: int) -> dict:
        """Fetch Jenkins build console logs"""
        self._check_demo_mode()
        if self.demo_mode:
            return {
                "success": True,
                "logs": DEMO_BUILD_LOGS
            }
        if not self.jenkins_client:
            return {
                "success": False,
                "error": "Jenkins client not initialized. Check your configuration."
            }
        try:
            logs = self.jenkins_client.get_console_output(job_name, build_number)
            return {
                "success": True,
                "logs": logs
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_last_failed_build(self, job_name: str) -> dict:
        """Get last failed build for a job"""
        self._check_demo_mode()
        if self.demo_mode:
            return {
                "success": True,
                "build": DEMO_FAILED_BUILD
            }
        if not self.jenkins_client:
            return {
                "success": False,
                "error": "Jenkins client not initialized. Check your configuration."
            }
        try:
            build_info = self.jenkins_client.get_last_failed_build(job_name)
            if build_info:
                return {
                    "success": True,
                    "build": build_info
                }
            else:
                return {
                    "success": False,
                    "error": "No failed builds found"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def trigger_jenkins_build(self, job_name: str) -> dict:
        """Trigger a Jenkins build"""
        self._check_demo_mode()
        if self.demo_mode:
            return {
                "success": True,
                "message": f"[DEMO] Build triggered for {job_name}",
                "build_number": 43
            }
        if not self.jenkins_client:
            return {
                "success": False,
                "error": "Jenkins client not initialized. Check your configuration."
            }
        try:
            result = self.jenkins_client.trigger_build(job_name)
            return {
                "success": True,
                "message": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # ========================================================================
    # File System Tools
    # ========================================================================

    def read_file(self, path: str) -> dict:
        """Read a local file"""
        # Check demo files first
        if path in DEMO_FILES:
            return {
                "success": True,
                "content": DEMO_FILES[path]
            }
        
        try:
            if not os.path.exists(path):
                return {
                    "success": False,
                    "error": f"File not found: {path}"
                }
            with open(path, "r") as f:
                content = f.read()
            return {
                "success": True,
                "content": content
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def write_file(self, path: str, content: str) -> dict:
        """Write to a local file"""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return {
                "success": True,
                "message": f"File written: {path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # ========================================================================
    # GitHub/PR Tools
    # ========================================================================

    def create_pr_with_fix(self, fix_data: dict) -> dict:
        """Create a GitHub PR with auto fix"""
        self._check_demo_mode()
        if self.demo_mode:
            return {
                "success": True,
                "message": "[DEMO] PR would be created",
                "pr_url": "https://github.com/Debdatta1105/Simple-Chat/pull/999",
                "fix_data": fix_data
            }
        try:
            result = create_auto_fix_pr(fix_data)
            # If result is None or dict, handle both cases
            if result is None:
                return {
                    "success": True,
                    "message": "PR created successfully (legacy)"
                }
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# ============================================================================
# MCP Server Setup
# ============================================================================

tools_impl = ToolImplementations()


def get_tools() -> list:
    """Return list of available tools for MCP"""
    return [
        {
            "name": "list_jenkins_jobs",
            "description": "List all available Jenkins jobs",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "get_jenkins_logs",
            "description": "Fetch Jenkins build console logs for analysis",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "job_name": {
                        "type": "string",
                        "description": "Name of the Jenkins job"
                    },
                    "build_number": {
                        "type": "integer",
                        "description": "Build number"
                    }
                },
                "required": ["job_name", "build_number"]
            }
        },
        {
            "name": "get_last_failed_build",
            "description": "Get the last failed build for a job",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "job_name": {
                        "type": "string",
                        "description": "Name of the Jenkins job"
                    }
                },
                "required": ["job_name"]
            }
        },
        {
            "name": "trigger_jenkins_build",
            "description": "Trigger a new Jenkins build",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "job_name": {
                        "type": "string",
                        "description": "Name of the Jenkins job to trigger"
                    }
                },
                "required": ["job_name"]
            }
        },
        {
            "name": "read_file",
            "description": "Read contents of a file from local repository",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Full path to the file"
                    }
                },
                "required": ["path"]
            }
        },
        {
            "name": "write_file",
            "description": "Write or modify a file",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Full path to the file"
                    },
                    "content": {
                        "type": "string",
                        "description": "File content"
                    }
                },
                "required": ["path", "content"]
            }
        },
        {
            "name": "create_pr_with_fix",
            "description": "Create a GitHub PR with the auto fix",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "fix_data": {
                        "type": "object",
                        "description": "Fix data containing target file, operation, and code patch"
                    }
                },
                "required": ["fix_data"]
            }
        }
    ]


def call_tool(name: str, arguments: dict) -> Any:
    """Execute a tool by name"""
    if name == "list_jenkins_jobs":
        return tools_impl.list_jenkins_jobs()
    elif name == "get_jenkins_logs":
        return tools_impl.get_jenkins_logs(
            arguments["job_name"],
            arguments["build_number"]
        )
    elif name == "get_last_failed_build":
        return tools_impl.get_last_failed_build(arguments["job_name"])
    elif name == "trigger_jenkins_build":
        return tools_impl.trigger_jenkins_build(arguments["job_name"])
    elif name == "read_file":
        return tools_impl.read_file(arguments["path"])
    elif name == "write_file":
        return tools_impl.write_file(arguments["path"], arguments["content"])
    elif name == "create_pr_with_fix":
        return tools_impl.create_pr_with_fix(arguments["fix_data"])
    else:
        return {"success": False, "error": f"Unknown tool: {name}"}


if __name__ == "__main__":
    # Test tools
    print("=" * 80)
    if DEMO_MODE:
        print("🎮 DEMO MODE ENABLED - Using simulated data")
    else:
        print("🔌 PRODUCTION MODE - Using real Jenkins API")
    print("=" * 80)
    
    print("\n✅ Available tools:")
    for tool in get_tools():
        print(f"  - {tool['name']}")
    
    print("\n" + "=" * 80)
    print("Testing list_jenkins_jobs:")
    print("=" * 80)
    result = call_tool("list_jenkins_jobs", {})
    print(json.dumps(result, indent=2))
    
    print("\n" + "=" * 80)
    print("Testing get_last_failed_build:")
    print("=" * 80)
    result = call_tool("get_last_failed_build", {"job_name": "JavaCompileTest"})
    print(json.dumps(result, indent=2))
    
    print("\n" + "=" * 80)
    print("Testing get_jenkins_logs:")
    print("=" * 80)
    result = call_tool("get_jenkins_logs", {"job_name": "JavaCompileTest", "build_number": 42})
    if result.get("success"):
        logs = result.get("logs", "")
        print(logs[:500] + "..." if len(logs) > 500 else logs)
    else:
        print(json.dumps(result, indent=2))
    
    print("\n" + "=" * 80)
    print("Testing read_file (demo file):")
    print("=" * 80)
    result = call_tool("read_file", {"path": "src/main/java/com/example/Calculator.java"})
    if result.get("success"):
        print(result.get("content"))
    else:
        print(json.dumps(result, indent=2))
