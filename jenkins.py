import requests
from requests.auth import HTTPBasicAuth


JENKINS_URL = "http://localhost:8080"
USERNAME = "Deb"
API_TOKEN = "11ad4ee59065ac093ab7fc49a723e640ab"


class JenkinsClient:

    def __init__(self, url, username, token):
        self.url = url.rstrip("/")
        self.auth = HTTPBasicAuth(username, token)

    # -----------------------------
    # Get all jobs
    # -----------------------------
    def get_jobs(self):
        url = f"{self.url}/api/json"

        r = requests.get(url, auth=self.auth)
        r.raise_for_status()

        data = r.json()

        jobs = []
        for job in data.get("jobs", []):
            jobs.append({
                "name": job["name"],
                "url": job["url"]
            })

        return jobs


    # -----------------------------
    # Get last failed build info
    # -----------------------------
    def get_last_failed_build(self, job_name):
        url = f"{self.url}/job/{job_name}/lastFailedBuild/api/json"

        r = requests.get(url, auth=self.auth)

        if r.status_code == 404:
            return None

        r.raise_for_status()

        return r.json()


    # -----------------------------
    # Get console output
    # -----------------------------
    def get_console_output(self, job_name, build_number):
        url = (
            f"{self.url}/job/{job_name}/"
            f"{build_number}/consoleText"
        )

        r = requests.get(url, auth=self.auth)
        r.raise_for_status()

        return r.text


    # -----------------------------
    # Trigger rebuild
    # -----------------------------
    def trigger_build(self, job_name):
        url = f"{self.url}/job/{job_name}/buildWithParameters"

        params = {
            "REPO_URL": "https://github.com/Debdatta1105/Simple-Chat.git",
            "BRANCH_NAME": "auto-fix-jenkins-build"
        }

        r = requests.post(url, auth=self.auth, params=params)

        r.raise_for_status()

        return "Build triggered"


# -----------------------------------
# Example usage
# -----------------------------------

if __name__ == "__main__":

    client = JenkinsClient(
        JENKINS_URL,
        USERNAME,
        API_TOKEN
    )

    # 1. List jobs
    print("\nJobs:")
    jobs = client.get_jobs()

    for j in jobs:
        print(j["name"])

    # 2. Read last failed build
    job_name = "JavaCompileTest"

    failed = client.get_last_failed_build(job_name)

    if failed:
        build_number = failed["number"]

        print(f"\nLast failed build: {build_number}")

        logs = client.get_console_output(
            job_name,
            build_number
        )

        print("\n--- Console Output ---")
        print(logs[:3000])   # print first 3000 chars

    else:
        print("\nNo failed build found.")