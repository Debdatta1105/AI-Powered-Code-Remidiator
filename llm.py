import os
from urllib import response
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv
from generate_pr import create_auto_fix_pr
from jenkins import JenkinsClient
import json
from generate_pr import create_auto_fix_pr
import streamlit as st

load_dotenv()

def get_secret(key, default=None):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)

print(os.getenv("JENKINS_USERNAME"))
print(os.getenv("API_TOKEN"))
llm = ChatGroq(
            temperature=0, 
            groq_api_key=get_secret("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile")
def explain_build_failure(console_output):
    prompt = PromptTemplate(
        input_variables=["console_output"],
        template=(
            "You are a helpful assistant that explains why a Jenkins build failed based on the console output.\n"
            "Here is the console output:\n"
            "{console_output}\n"
            "Please provide a concise explanation of the failure."
        )
    )

    formatted_prompt = prompt.format(console_output=console_output)

    try:
        response = llm.invoke(formatted_prompt)
        return response.content
    except OutputParserException as e:
        return f"Error parsing LLM output: {str(e)}"

def suggest_fix(console_output):

    prompt = PromptTemplate(
        input_variables=["console_output"],
        template="""
You are an expert CI/CD remediation agent.

Analyze the Jenkins build failure console output.

Return ONLY valid JSON.

Rules:
- Suggest only safe automated fixes
- Identify the exact file and line number from the logs if available
- If line number is not present, infer best possible location
- Determine the correct operation:
  - "insert" → adding new code line
  - "replace" → modifying existing code line
  - "delete" → removing incorrect code line
  - "modify"  → update part of an existing line (preferred for small fixes)
FOR MODIFY OPERATION:
- Provide "match_text" → exact line from file
- Provide "code_patch" → corrected version of that line
- Do NOT include explanations
- Keep change minimal (only what is required)
DISAMBIGUATION (VERY IMPORTANT):
- If the same line may appear multiple times:
  - Provide "match_context_before" and/or "match_context_after"
  - These should be nearby lines to uniquely identify the location

- Prefer precise fixes over generic ones
- If no safe fix exists, set can_auto_fix to false
- Do not return explanations outside JSON

Return format:

{{
"failure_type":"",
"root_cause":"",
"can_auto_fix":true,
"target_file":"",
"target_line":"",
"operation": "insert | replace | delete",
"end_line": 0,
"match_context_before": "",
"match_text": "",
"match_context_after": "",
"fix_description":"",
"code_patch":"",
"pr_title":"",
"pr_body":""
}}

Console Output:
{console_output}
"""
    )

    formatted_prompt = prompt.format(
        console_output=console_output[:8000]
    )

    response = llm.invoke(formatted_prompt)

    return response.content
    
if __name__ == "__main__":
    

    client = JenkinsClient(
        url=os.getenv("JENKINS_URL"),
        username=os.getenv("JENKINS_USERNAME"),
        token=os.getenv("API_TOKEN")
    )

    # 1. List jobs
    jobs = client.get_jobs()
    job_name = "JavaCompileTest"
    failed_job = client.get_last_failed_build(job_name)
    if failed_job:
        build_number = failed_job["number"]

        print(f"\nLast failed build: {build_number}")

        logs = client.get_console_output(
            job_name,
            build_number
        )
        print(explain_build_failure(logs))
        fix = suggest_fix(logs)
        print(fix)
        import json

        clean = fix.strip()

        clean = clean.replace("```json","")
        clean = clean.replace("```","")

        fix_data = json.loads(clean)

        create_auto_fix_pr(fix_data)
    else:
        print("No failed builds found.")
    client.trigger_build(job_name)
