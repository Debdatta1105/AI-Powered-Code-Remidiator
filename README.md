# 🚀 AI-Powered-Code-Remidiator — Autonomous Jenkins Failure Remediation Agent

> **An Agentic AI system that analyzes failed Jenkins jobs, diagnoses root causes using LLMs, proposes code fixes, and can automatically raise GitHub Pull Requests for remediation.**

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Jenkins](https://img.shields.io/badge/Jenkins-CI-red)
![LangChain](https://img.shields.io/badge/LangChain-Agent-green)
![Groq](https://img.shields.io/badge/LLM-Groq-orange)
![GitHub](https://img.shields.io/badge/GitHub-PR_Automation-black)

---

## 🔥 Why This Project Matters

CI/CD failures cost engineering teams time.

Developers spend hours:

* Reading Jenkins console logs
* Diagnosing root causes
* Applying repetitive fixes
* Creating remediation PRs manually

**AICompiler automates that workflow.**

It acts like an autonomous remediation agent:

**Failed Job → Root Cause Analysis → Suggested Fix → Auto PR**

---

## ✨ Core Features

### 🧠 AI Failure Analysis

* Connects to Jenkins
* Reads failed job console output
* Uses LLMs to explain build failures
* Identifies probable root causes

### 🔧 Auto-Fix Generation

Generates safe automated fixes for issues like:

✅ Missing imports
✅ Compilation errors
✅ Dependency issues
✅ Syntax errors
✅ Test failures
✅ Basic CI misconfigurations

---

### 🤖 Automated Pull Request Creation

If a fix is safe:

* Creates code patch
* Commits remediation
* Opens GitHub PR automatically
* Can assign reviewers (extensible)

---

### 📊 Streamlit Dashboard

Simple UI to:

* Select failed jobs
* View console logs
* Get AI diagnosis
* Review proposed fixes
* Trigger PR creation

---

## 🏗 Architecture

```text
                +----------------+
                | Jenkins Server  |
                +--------+-------+
                         |
               Read Failed Build Logs
                         |
                         v
                +----------------+
                | MCP / AI Agent  |
                +----------------+
                    |         |
            Root Cause       Fix Generation
                    |         |
                    v         v
                +----------------+
                | GitHub PR Bot   |
                +----------------+
                         |
                   Auto Fix PR
```

---

## ⚙️ Tech Stack

| Layer           | Tech                 |
| --------------- | -------------------- |
| Language        | Python               |
| Agent Framework | LangChain            |
| LLM             | Groq (Llama 3.3 70B) |
| CI Integration  | Jenkins API          |
| SCM Automation  | GitHub API           |
| UI              | Streamlit            |
| Environment     | python-dotenv        |

---

## 📂 Project Structure

```bash
AICompiler/
│
├── app.py                # Streamlit UI
├── llm.py                # Failure analysis + fix generation
├── jenkins.py            # Jenkins integration client
├── github_pr.py          # Auto PR creation logic
├── .env                  # Secrets
└── README.md
```

---

## 🚀 Example Workflow

### Failed Jenkins Job

```bash
javac Main.java
error: cannot find symbol
```

---

## AI Diagnosis

```json
{
  "failure_type": "Compilation Error",
  "root_cause": "Missing import statement",
  "can_auto_fix": true
}
```

---

## Auto-Generated Fix

```java
import java.util.List;
```

---

## Auto-Created Pull Request

```text
Fix Jenkins build failure caused by missing import
```

---

## 🛠 Installation

### Clone

```bash
git clone https://github.com/Debdatta1105/AICompiler.git
cd AICompiler
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment

Create:

```bash
.env
```

```env
GROQ_API_KEY=xxx
JENKINS_URL=http://localhost:8080
JENKINS_USERNAME=your_user
API_TOKEN=your_jenkins_token
GITHUB_TOKEN=your_github_token
```

---

## Run UI

```bash
python -m streamlit run app.py
```

---

## 🔍 Future Roadmap

Planned:

* [ ] Multi-agent remediation orchestration
* [ ] GitHub Actions support
* [ ] Kubernetes deployment diagnostics
* [ ] PR auto-review agent
* [ ] Vulnerability fix remediation (Black Duck/SCA)
* [ ] Self-healing CI pipelines

---

## 💡 Interesting Use Cases

* Autonomous DevOps Copilot
* Self-Healing CI/CD
* AI SRE Assistant
* Failure Triage Automation
* Remediation Bots for Platform Engineering

---

## 🧪 Potential Research Extensions

This can evolve into:

* Agentic Software Repair
* CI Failure Pattern Learning
* Multi-Agent DevOps Systems

---

## ⭐ What Makes This Interesting

This is not another chatbot.

This combines:

* LLM reasoning
* Jenkins integration
* GitHub automation
* Agentic remediation workflows

It moves from:

**AI as assistant → AI as autonomous engineering agent**

---

## 🤝 Contributing

PRs, ideas, and improvements are welcome.

Especially interested in:

* New auto-fix patterns
* More failure detectors
* Multi-agent extensions

---

## 👨‍💻 Author

**Debdatta Ray**

Building at the intersection of:

* Agentic AI
* DevOps Automation
* Autonomous Software Systems

GitHub:

[https://github.com/Debdatta1105](https://github.com/Debdatta1105)

---

## 🌟 If you like this project

Give it a star.

If you think autonomous remediation is the future of DevOps,

**let’s build it.**
