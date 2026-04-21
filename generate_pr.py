import os
from github import Github


def create_auto_fix_pr(fix):

    if not fix["can_auto_fix"]:
        print("No safe auto-fix possible.")
        return

    g = Github(
        os.getenv("GITHUB_TOKEN")
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

    target_file = fix["target_file"]

    file = repo.get_contents(
        target_file,
        ref=branch_name
    )

    old_content = file.decoded_content.decode()

    # VERY SIMPLE PATCH EXAMPLE:
    # prepend generated code patch

    new_content = (
        fix["code_patch"]
        + "\n"
        + old_content
    )

    # ----------------------------
    # Commit fix
    # ----------------------------

    repo.update_file(
        path=target_file,
        message=fix["pr_title"],
        content=new_content,
        sha=file.sha,
        branch=branch_name
    )

    # ----------------------------
    # Open PR
    # ----------------------------

    pr = repo.create_pull(
        title=fix["pr_title"],
        body=fix["pr_body"],
        head=branch_name,
        base=base_branch
    )

    print("PR Created:")
    print(pr.html_url)