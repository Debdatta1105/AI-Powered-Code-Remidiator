# 🚀 AI-Powered Code Remediator — Jenkins Failure Auto-Fix Agent

🔗 **Live Demo:** https://debdatta-ai-powered-code-generator.streamlit.app/

> An AI-driven system that analyzes Jenkins build failures, identifies root causes using LLMs, generates fixes, and can create GitHub Pull Requests automatically.

---

## ⚡ What This Does

CI/CD failures slow down development.

This system automates the workflow:

**Failed Build → Root Cause → Suggested Fix → PR Creation -> Re-trigger Job**

---

## 🧠 Key Capabilities

### 1. Failure Analysis

* Reads Jenkins console logs
* Uses LLMs (Groq LLaMA 3.3 70B) to explain failures
* Identifies root causes (compilation, dependency, test errors)

---

### 2. Fix Generation

Automatically suggests fixes such as:

* Missing imports
* Syntax errors
* Dependency issues
* Test failures
* Basic CI misconfigurations

---

### 3. PR Automation

* Generates patch
* Creates commit
* Opens GitHub Pull Request
* (Extensible for reviewers/approval)

---

### 4. Interactive UI

Built with Streamlit:

* Select job / load failure
* View logs
* Analyze failure
* Generate fix
* Trigger PR (Validation)

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
                         |
            Trigger Jenkins Rebuild
```

---

## ⚙️ Tech Stack

| Layer     | Tech                 |
| --------- | -------------------- |
| Language  | Python               |
| LLM       | Groq (LLaMA 3.3 70B) |
| Framework | LangChain            |
| CI        | Jenkins API          |
| SCM       | GitHub API           |
| UI        | Streamlit            |

---

## 🎮 Demo Mode vs Live Mode

### ⚡ Demo Mode (Default - Cloud)

* Uses simulated Jenkins failures
* PR creation is mocked
* Ensures reliable public demo

### 🔌 Live Mode (Local)

* Connects to real Jenkins
* Creates real GitHub PRs
* Requires credentials

---

## 🚀 Example

### Failure

```
error: cannot find symbol
```

### AI Output

```json
{
  "failure_type": "Compilation Error",
  "root_cause": "Missing import statement",
  "can_auto_fix": true
}
```

### Fix

```java
import java.util.List;
```

---

## 🛠 Setup

### 1. Clone

```
git clone https://github.com/Debdatta1105/AICompiler.git
cd AICompiler
```

### 2. Install

```
pip install -r requirements.txt
```

### 3. Configure

Create `.env`:

```
GROQ_API_KEY=xxx
GITHUB_TOKEN=xxx
JENKINS_URL=http://localhost:8080
JENKINS_USERNAME=xxx
API_TOKEN=xxx
```

---

### 4. Run

```
python -m streamlit run app.py
```

---

## 🔐 Deployment Notes

* Uses Streamlit secrets in cloud
* Jenkins integration works locally
* Public demo runs in **safe simulated mode**

---

## 💡 Why This Project Stands Out

* Combines **LLM reasoning + DevOps automation**
* Moves beyond chatbots → **actionable systems**
* Demonstrates **end-to-end engineering workflow**
* Designed for **real-world extensibility**

---

## 🚧 Limitations

* Fixes are heuristic (not formally verified)
* Limited to common failure patterns
* Jenkins live mode requires local setup

---

## 🔮 Future Work

* Multi-agent orchestration
* CI retry + validation loop
* PR auto-review agent
* GitHub Actions support

---

## 👨‍💻 Author

**Debdatta Ray**
GitHub: https://github.com/Debdatta1105

---

## ⭐ If you found this interesting

Give it a star — and feel free to contribute.
