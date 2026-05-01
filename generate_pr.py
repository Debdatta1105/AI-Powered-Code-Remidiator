import os
from github import Github
import streamlit as st

def get_secret(key, default=None):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)

def create_auto_fix_pr(fix):
    # Check demo mode
    demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"

    if not fix.get("can_auto_fix", False):
        print("No safe auto-fix possible.")
        return {
            "success": False,
            "error": "can_auto_fix is False or not provided"
        }

    if demo_mode:
        print("[DEMO MODE] Simulating PR creation...")
        return {
            "success": True,
            "message": "[DEMO] PR would be created with the provided fix",
            "pr_url": "https://github.com/Debdatta1105/Simple-Chat/pull/999",
            "branch": "auto-fix-jenkins-build",
            "fix_summary": fix
        }

    g = Github(
        get_secret("GITHUB_TOKEN")
    )

    repo = g.get_repo(
        "Debdatta1105/Simple-Chat"
    )

    # ----------------------------
    # Create branch
    # ----------------------------

    base_branch = "main"

    source = repo.get_branch(base_branch)

    branch_name = "auto-fix-jenkins-build"

    try:
        repo.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=source.commit.sha
        )

    except Exception:
        print("Branch may already exist, continuing...")

    # ----------------------------
    # Read file to modify
    # ----------------------------

    target_file = fix.get("target_file")
    if not target_file:
        print("No target file provided")
        return {
            "success": False,
            "error": "No target file provided"
        }

    try:
        file = repo.get_contents(target_file, ref=branch_name)
    except Exception as e:
        print("File not found")
        return {
            "success": False,
            "error": f"File not found: {str(e)}"
        }

    old_content = file.decoded_content.decode()
    lines = old_content.split("\n")

    # ----------------------------
    # Parse inputs safely
    # ----------------------------
    try:
        start = int(fix.get("target_line", 1)) - 1
    except:
        start = 0

    try:
        end = int(fix.get("end_line", start + 1))
    except:
        end = start + 1

    start = max(0, min(start, len(lines)))
    end = max(start, min(end, len(lines)))

    operation = fix.get("operation", "insert")
    patch = fix.get("code_patch", "")
    patch_lines = patch.split("\n")

    match_text = fix.get("match_text", "").strip()
    before = fix.get("match_context_before", "")
    after = fix.get("match_context_after", "")

    # ----------------------------
    # Context-based matching
    # ----------------------------
    def find_match_index():
        for i in range(len(lines)):
            if match_text and match_text == lines[i].strip():

                before_ok = True
                after_ok = True

                if before:
                    before_ok = any(before in lines[j] for j in range(max(0, i-5), i))

                if after:
                    after_ok = any(after in lines[j] for j in range(i+1, min(len(lines), i+6)))

                if before_ok and after_ok:
                    return i
        return None

    match_index = find_match_index()

    # ----------------------------
    # APPLY PATCH
    # ----------------------------

    if operation == "modify":
        if match_index is not None:
            lines[match_index] = patch
        else:
            # fallback to line number
            lines[start] = patch

    elif operation == "replace":
        if match_index is not None:
            lines[match_index:match_index+1] = patch_lines
        else:
            lines[start:end] = patch_lines

    elif operation == "delete":
        if match_index is not None:
            del lines[match_index]
        else:
            del lines[start:end]

    else:  # insert
        if match_index is not None:
            lines.insert(match_index, patch)
        else:
            lines[start:start] = patch_lines

    new_content = "\n".join(lines)

    # ----------------------------
    # Commit
    # ----------------------------
    try:
        repo.update_file(
            path=target_file,
            message=fix.get("pr_title", "Auto fix"),
            content=new_content,
            sha=file.sha,
            branch=branch_name
        )
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to update file: {str(e)}"
        }

    # ----------------------------
    # Create PR
    # ----------------------------
    try:
        pr = repo.create_pull(
            title=fix.get("pr_title", "Auto Fix"),
            body=fix.get("pr_body", ""),
            head=branch_name,
            base=base_branch
        )

        print("PR Created:", pr.html_url)
        return {
            "success": True,
            "pr_url": pr.html_url,
            "message": f"PR created successfully: {pr.html_url}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to create PR: {str(e)}"
        }