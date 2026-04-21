import os
import streamlit as st
import json
from dotenv import load_dotenv

from jenkins import JenkinsClient
from llm import explain_build_failure
from llm import suggest_fix

from generate_pr import create_auto_fix_pr

load_dotenv()

jenkins_client = JenkinsClient(
        url=os.getenv("JENKINS_URL"),
        username=os.getenv("JENKINS_USERNAME"),
        token=os.getenv("API_TOKEN")
)

# ------------------------
# Page
# ------------------------

st.set_page_config(
    page_title="AI Jenkins Auto-Fix Agent",
    layout="wide"
)

st.title("AI Jenkins Auto-Fix Agent")

# ------------------------
# Inputs
# ------------------------

jobs = []
job_error = None
try:
    jobs = [job["name"] for job in jenkins_client.get_jobs()]
except Exception as exc:
    job_error = f"Unable to load Jenkins jobs: {exc}"

if job_error:
    st.error(job_error)

default_job = st.session_state.get("selected_job", "Select a job")
job_options = ["Select a job"] + jobs
job_index = job_options.index(default_job) if default_job in job_options else 0
job_name = st.selectbox(
    "Select Jenkins Job",
    options=job_options,
    index=job_index,
)

if st.button("Load last failed build"):
    if job_name and job_name != "Select a job":
        try:
            failed_build = jenkins_client.get_last_failed_build(job_name)
            if failed_build is None:
                st.warning("No failed build found for the selected job.")
            else:
                build_number = failed_build.get("number")
                console_text = jenkins_client.get_console_output(job_name, build_number)
                st.session_state["console_output"] = console_text
                st.session_state["selected_job"] = job_name
                st.session_state["build_number"] = build_number
                st.success(f"Loaded last failed build #{build_number} for {job_name}.")
        except Exception as exc:
            st.error(f"Failed to fetch build output: {exc}")
    else:
        st.error("Please select a Jenkins job before loading the build.")

console_output = st.text_area(
    "Jenkins Console Output",
    value=st.session_state.get("console_output", ""),
    height=300,
)

col1, col2, col3 = st.columns(3)

# ------------------------
# Analyze Failure
# ------------------------

with col1:

    if st.button("Analyze Failure"):

        if console_output:

            explanation = explain_build_failure(
                console_output
            )

            st.subheader(
                "Failure Analysis"
            )

            st.write(explanation)

# ------------------------
# Generate Fix
# ------------------------

with col2:

    if st.button("Generate Fix"):

        if console_output:

            raw_fix = suggest_fix(
                console_output
            )

            clean = raw_fix.strip()

            clean = clean.replace(
                "```json",
                ""
            )

            clean = clean.replace(
                "```",
                ""
            )

            fix_data = json.loads(clean)

            st.subheader(
                "Suggested Auto Fix"
            )

            st.json(fix_data)

            st.session_state["fix_data"] = fix_data

# ------------------------
# Create PR
# ------------------------

with col3:

    if st.button("Create Auto PR"):

        if "fix_data" in st.session_state:

            create_auto_fix_pr(
                st.session_state["fix_data"]
            )

            st.success(
                "Pull Request created."
            )

        else:
            st.error(
                "Generate fix first."
            )