import os
import json
import streamlit as st
from dotenv import load_dotenv

from llm import explain_build_failure, suggest_and_apply_fix, auto_fix_job
import mcp_server

# ------------------------
# Setup
# ------------------------

load_dotenv()

st.set_page_config(
    page_title="AICompiler — MCP-Driven CI Auto Fix Agent",
    layout="wide"
)

st.title("🚀 AICompiler — MCP-Driven Autonomous CI Remediation")

st.markdown("""
> AI agent powered by **Model Context Protocol (MCP)** for fully autonomous CI/CD failure remediation.
> Uses LLM tool-calling to orchestrate Jenkins, GitHub, and file system operations.
""")

# ------------------------
# Mode Toggle
# ------------------------

mode = st.sidebar.radio("Mode", ["Autonomous Agent", "Interactive Analysis"])
IS_AUTONOMOUS = mode == "Autonomous Agent"

# ------------------------
# Sidebar: Job Selection
# ------------------------

st.sidebar.header("Configuration")

# Get available jobs via MCP
try:
    jobs_result = mcp_server.call_tool("list_jenkins_jobs", {})
    if jobs_result.get("success"):
        jobs = [j["name"] for j in jobs_result.get("jobs", [])]
    else:
        jobs = []
        st.sidebar.error(f"Could not load jobs: {jobs_result.get('error')}")
except Exception as e:
    jobs = []
    st.sidebar.error(f"Error fetching jobs: {e}")

job_name = st.sidebar.selectbox(
    "Select Jenkins Job",
    options=["Select a job"] + jobs if jobs else ["No jobs available"]
)

# ============================================================================
# MODE 1: Autonomous Agent Mode
# ============================================================================

if IS_AUTONOMOUS:
    st.header("🤖 Autonomous Fix Mode")
    st.write("The agent will autonomously fix the last failed build and create a PR.")
    
    if st.button("🚀 Start Autonomous Fix", type="primary"):
        if job_name == "Select a job" or not jobs:
            st.error("Please select a valid job.")
        else:
            with st.spinner("🤔 Agent is analyzing and fixing the build..."):
                result = auto_fix_job(job_name)
            
            st.subheader("Agent Result")
            st.json(result)
            
            if result.get("success"):
                st.success("✅ Build fixed and PR created!")
            else:
                st.error(f"❌ Agent failed: {result.get('error', 'Unknown error')}")

# ============================================================================
# MODE 2: Interactive Analysis Mode
# ============================================================================

else:
    st.header("🔍 Interactive Analysis Mode")
    st.write("Manually analyze a build and review the fix before creating a PR.")
    
    col1, col2, col3 = st.columns(3)
    
    # Load last failed build
    with col1:
        if st.button("📥 Load Last Failed Build"):
            if job_name == "Select a job" or not jobs:
                st.error("Please select a valid job.")
            else:
                with st.spinner("Fetching last failed build..."):
                    build_result = mcp_server.call_tool("get_last_failed_build", {"job_name": job_name})
                
                if build_result.get("success"):
                    build_info = build_result.get("build", {})
                    build_number = build_info.get("number")
                    
                    # Fetch logs
                    logs_result = mcp_server.call_tool("get_jenkins_logs", {
                        "job_name": job_name,
                        "build_number": build_number
                    })
                    
                    if logs_result.get("success"):
                        st.session_state["console_output"] = logs_result.get("logs", "")
                        st.session_state["job_name"] = job_name
                        st.session_state["build_number"] = build_number
                        st.success(f"✅ Loaded build #{build_number}")
                    else:
                        st.error(f"Could not fetch logs: {logs_result.get('error')}")
                else:
                    st.warning(f"No failed build found: {build_result.get('error')}")
    
    # Analyze failure
    with col2:
        if st.button("🧠 Analyze Failure"):
            console_output = st.session_state.get("console_output", "")
            job = st.session_state.get("job_name", "")
            build_num = st.session_state.get("build_number", 0)
            
            if not console_output or job == "Select a job":
                st.error("Load a build first.")
            else:
                with st.spinner("Analyzing failure..."):
                    analysis = explain_build_failure(job, build_num)
                
                st.session_state["analysis"] = analysis
                st.success("✅ Analysis complete")
    
    # Generate fix
    with col3:
        if st.button("🔧 Generate Fix"):
            job = st.session_state.get("job_name", "")
            build_num = st.session_state.get("build_number", 0)
            
            if job == "Select a job" or build_num == 0:
                st.error("Load a build first.")
            else:
                with st.spinner("Generating fix..."):
                    fix_result = suggest_and_apply_fix(job, build_num)
                
                st.session_state["fix_result"] = fix_result
                st.success("✅ Fix generated")
    
    # Display sections
    if "console_output" in st.session_state:
        st.subheader("📜 Console Output")
        st.text_area(
            "Build logs",
            value=st.session_state.get("console_output", ""),
            height=200,
            disabled=True
        )
    
    if "analysis" in st.session_state:
        st.subheader("🧠 Failure Analysis")
        analysis_data = st.session_state["analysis"]
        if isinstance(analysis_data, dict):
            st.write(analysis_data.get("analysis", str(analysis_data)))
        else:
            st.write(analysis_data)
    
    if "fix_result" in st.session_state:
        st.subheader("🔧 Suggested Fix")
        fix_data = st.session_state["fix_result"]
        st.json(fix_data)
        
        if not fix_data.get("can_auto_fix"):
            st.warning(f"⚠️ This fix cannot be automatically applied: {fix_data.get('root_cause', 'Unknown reason')}")
        else:
            col_apply, col_trigger = st.columns(2)
            
            with col_apply:
                if st.button("✅ Apply Fix & Create PR"):
                    try:
                        with st.spinner("Creating PR..."):
                            pr_result = mcp_server.call_tool("create_pr_with_fix", {"fix_data": fix_data})
                        
                        if pr_result.get("success"):
                            st.success("✅ Pull Request created!")
                            st.session_state["pr_created"] = True
                            if pr_result.get("pr_url"):
                                st.markdown(f"🔗 [View PR]({pr_result['pr_url']})")
                        else:
                            st.error(f"PR creation failed: {pr_result.get('error')}")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            with col_trigger:
                if st.button("♻️ Trigger Build"):
                    job = st.session_state.get("job_name", "")
                    if job and job != "Select a job":
                        with st.spinner("Triggering build..."):
                            trigger_result = mcp_server.call_tool("trigger_jenkins_build", {"job_name": job})
                        
                        if trigger_result.get("success"):
                            st.success("✅ Build triggered!")
                        else:
                            st.error(f"Build trigger failed: {trigger_result.get('error')}")
                    else:
                        st.error("No job selected")

# ============================================================================
# Footer
# ============================================================================

st.divider()
st.markdown("""
**Architecture:**
- 🔌 **MCP Server** - Exposes Jenkins, GitHub, and file system tools
- 🤖 **LLM Agent** - Uses LangChain tool-calling to orchestrate operations autonomously  
- 🧠 **Model** - Groq LLaMA 3.3 70B
- 💾 **Storage** - GitHub + Local filesystem
""")
