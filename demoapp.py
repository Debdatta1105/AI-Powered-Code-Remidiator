import os
import json
import streamlit as st
from dotenv import load_dotenv

from jenkins import JenkinsClient
from llm import explain_build_failure, suggest_fix
from generate_pr import create_auto_fix_pr

# ------------------------
# Setup
# ------------------------

load_dotenv()

st.set_page_config(
    page_title="AICompiler — CI Auto Fix Agent",
    layout="wide"
)

st.title("🚀 AICompiler — Autonomous CI Failure Remediation")

# ------------------------
# Mode Toggle
# ------------------------

mode = st.sidebar.radio("Mode", ["Demo", "Live Jenkins"])
USE_MOCK = mode == "Demo"

# ------------------------
# Mock Data (Demo Mode)
# ------------------------

MOCK_JOBS = [
    "JavaCompileTest",
    "TestFailureJob",
    "DependencyFailureJob"
]

MOCK_LOGS = {
    "JavaCompileTest": """
Server.java:5: error: cannot find symbol
List<String> list = new ArrayList<>();
symbol: class List
""",
    "TestFailureJob": """
AssertionError: expected 200 but got 500
""",
    "DependencyFailureJob": """
Could not resolve dependency:
org.springframework.boot:spring-boot-starter-web
"""
}

# ------------------------
# Jenkins Client (only if needed)
# ------------------------

jenkins_client = None

if not USE_MOCK:
    try:
        jenkins_client = JenkinsClient(
            url=os.getenv("JENKINS_URL"),
            username=os.getenv("JENKINS_USERNAME"),
            token=os.getenv("API_TOKEN")
        )
    except Exception as e:
        st.error(f"Failed to initialize Jenkins client: {e}")

# ------------------------
# Load Jobs
# ------------------------

jobs = []
job_error = None

if USE_MOCK:
    jobs = MOCK_JOBS
    st.warning("⚡ Demo Mode: Using simulated Jenkins failures")
else:
    try:
        jobs = [job["name"] for job in jenkins_client.get_jobs()]
    except Exception as exc:
        job_error = f"Unable to load Jenkins jobs: {exc}"

if job_error:
    st.error(job_error)

# ------------------------
# Job Selection
# ------------------------

job_name = st.selectbox(
    "Select Jenkins Job",
    options=["Select a job"] + jobs
)

# ------------------------
# Load Failed Build
# ------------------------

if st.button("📥 Load Last Failed Build"):

    if job_name == "Select a job":
        st.error("Please select a job first.")
    else:
        try:
            if USE_MOCK:
                console_text = MOCK_LOGS.get(job_name, "")
                build_number = 1
            else:
                failed_build = jenkins_client.get_last_failed_build(job_name)

                if failed_build is None:
                    st.warning("No failed build found.")
                    console_text = ""
                else:
                    build_number = failed_build.get("number")
                    console_text = jenkins_client.get_console_output(
                        job_name,
                        build_number
                    )

            st.session_state["console_output"] = console_text
            st.session_state["job_name"] = job_name
            st.session_state["build_number"] = build_number

            st.success(f"Loaded build #{build_number}")

        except Exception as e:
            st.error(f"Error loading build: {e}")

# ------------------------
# Console Output
# ------------------------

console_output = st.text_area(
    "📜 Jenkins Console Output",
    value=st.session_state.get("console_output", ""),
    height=300
)

col1, col2, col3, col4 = st.columns(4)

# ------------------------
# Analyze Failure
# ------------------------

with col1:
    if st.button("🧠 Analyze Failure"):

        if console_output:
            with st.spinner("Analyzing failure..."):
                explanation = explain_build_failure(console_output)

            st.subheader("Failure Analysis")
            st.write(explanation)
        else:
            st.error("No console output available.")

# ------------------------
# Generate Fix
# ------------------------

with col2:
    if st.button("🔧 Generate Fix"):

        if console_output:
            with st.spinner("Generating fix..."):
                raw_fix = suggest_fix(console_output)

            try:
                clean = raw_fix.strip()
                clean = clean.replace("```json", "")
                clean = clean.replace("```", "")

                fix_data = json.loads(clean)

                st.subheader("Suggested Fix")
                st.json(fix_data)

                # Confidence bar (optional)
                confidence = fix_data.get("confidence", 0.8)
                st.progress(confidence)

                st.session_state["fix_data"] = fix_data

            except Exception as e:
                st.error("Failed to parse LLM response")
                st.code(raw_fix)

        else:
            st.error("No console output available.")

# ------------------------
# Create PR
# ------------------------

with col3:
    if st.button("🚀 Create Auto PR"):

        if "fix_data" not in st.session_state:
            st.error("Generate fix first.")
        else:
            try:
                with st.spinner("Creating PR..."):
                    pr_url = create_auto_fix_pr(
                        st.session_state["fix_data"]
                    )

                st.success("✅ Pull Request created!")
                st.session_state["pr_created"] = True

                if pr_url:
                    st.markdown(f"🔗 [View PR]({pr_url})")

            except Exception as e:
                st.error(f"PR creation failed: {e}")
                st.session_state["pr_created"] = False

# ------------------------
# Retrigger Build
# ------------------------

with col4:
    if st.button("♻️ Retrigger Build"):

        if not st.session_state.get("pr_created", False):
            st.error("Create a PR first before retriggering the build.")
        else:
            job = st.session_state.get("job_name", "")
            if not job or job == "Select a job":
                st.error("Please select a job first.")
            else:
                try:
                    if USE_MOCK:
                        st.success("✅ Build triggered (Demo Mode)")
                    else:
                        with st.spinner("Triggering build..."):
                            result = jenkins_client.trigger_build(job)
                        st.success(f"✅ {result}")

                except Exception as e:
                    st.error(f"Failed to trigger build: {e}")