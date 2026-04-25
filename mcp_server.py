"""
MCP Server for AI Compiler - Exposes Jenkins, GitHub, and File System tools
"""

import os
import json
from typing import Any
from dotenv import load_dotenv
from jenkins import JenkinsClient
from generate_pr import create_auto_fix_pr

load_dotenv()

# ============================================================================
# Tool Implementations
# ============================================================================

def get_secret(key, default=None):
    """Get secret from environment"""
    return os.getenv(key, default)


class ToolImplementations:
    """Tool implementations for MCP server"""

    def __init__(self):
        self.jenkins_client = JenkinsClient(
            url=get_secret("JENKINS_URL", "http://localhost:8080"),
            username=get_secret("JENKINS_USERNAME"),
            token=get_secret("API_TOKEN")
        )

    # ========================================================================
    # Jenkins Tools
    # ========================================================================

    def list_jenkins_jobs(self) -> dict:
        """List all Jenkins jobs"""
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
    print("Available tools:")
    for tool in get_tools():
        print(f"  - {tool['name']}")
    
    print("\nTesting list_jenkins_jobs:")
    result = call_tool("list_jenkins_jobs", {})
    print(json.dumps(result, indent=2))
