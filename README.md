# 🚀 AICompiler — MCP-Driven CI/CD Auto-Fix Agent

> An autonomous, LLM-powered system that analyzes Jenkins build failures, generates fixes, and creates GitHub Pull Requests—all orchestrated through the **Model Context Protocol (MCP)**.
>
> 🔗 **Live Demo:** https://ai-powered-code-remidiator-testmode.streamlit.app/

**Status:** ✅ Fully MCP-driven | 🤖 Autonomous agents | 🔌 Tool-agnostic architecture

---

## ⚡ What This Does

Jenkins builds fail. You fix them manually. **AICompiler automates it.**

**End-to-end workflow:**
```
Failed Build → Analyze Logs → Generate Fix → Create PR → Trigger New Build
```

### Key Features

✅ **Autonomous Fix Generation** - LLM analyzes failures and generates structured fixes  
✅ **MCP-Driven Tools** - Extensible tool framework for Jenkins, GitHub, file system  
✅ **Dual Modes** - Autonomous (one-click) or Interactive (step-by-step)  
✅ **Real PR Creation** - Commits fixes directly to GitHub  
✅ **Auto Retrigger** - Optionally triggers new build after fix  
✅ **Streamlit UI** - Visual dashboard for easy interaction  

---

## 🏗 Architecture

### MCP-Based Design

```
┌─────────────────────────────────────────────────────┐
│                  LLM Agent (Tool Calling)           │
│              (Groq LLaMA 3.3 70B)                   │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
     ┌───────────────────────┐
     │    MCP Server         │
     │  (Tool Orchestration) │
     └────────┬──────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
┌────────┐ ┌──────┐ ┌───────┐
│Jenkins │ │GitHub│ │ Files │
│  API   │ │ API  │ │System │
└────────┘ └──────┘ └───────┘
```

### Data Flow

```
1. MCP Server exposes tools:
   - list_jenkins_jobs()
   - get_jenkins_logs(job, build)
   - get_last_failed_build(job)
   - trigger_jenkins_build(job)
   - read_file(path)
   - write_file(path, content)
   - create_pr_with_fix(fix_data)

2. LLM Agent decides tool sequence:
   - Get build info → Fetch logs → Analyze failure
   - Generate fix JSON → Create PR → Trigger build

3. Results flow back to UI or CLI
```

---

## 🎯 Usage Modes

### 1. **Autonomous Mode** (Recommended)

One-click fix with no user intervention:

```bash
# Streamlit UI
streamlit run demoapp.py
# Then select "Autonomous Agent" mode and click "🚀 Start Autonomous Fix"
```

**What happens:**
- Agent gets last failed build
- Analyzes logs
- Generates fix
- Creates PR
- Triggers new build
- Shows full result

### 2. **Interactive Mode**

Step-by-step manual control:

```bash
streamlit run demoapp.py
# Then select "Interactive Analysis" mode
```

**Steps:**
1. Load last failed build → 📥
2. Analyze failure → 🧠
3. Generate fix → 🔧
4. Review fix JSON
5. Create PR → ✅
6. Trigger build → ♻️

### 3. **CLI Mode**

Pure Python, no UI:

```bash
python llm.py
```

Fixes the last failed build of `JavaCompileTest` and triggers a new build.

---

## 🧠 Fix Generation

The LLM generates structured fix data:

```json
{
  "failure_type": "compilation error",
  "root_cause": "Missing import statement for List class",
  "can_auto_fix": true,
  "target_file": "src/main/java/Server.java",
  "target_line": 5,
  "operation": "insert",
  "match_text": "import java.util.*;",
  "code_patch": "import java.util.List;",
  "pr_title": "Fix: Add missing import for List class",
  "pr_body": "Fixes compilation error in Server.java by importing List class."
}
```

---

## ⚙️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.8+ |
| **LLM** | Groq (LLaMA 3.3 70B) |
| **Framework** | LangChain |
| **Architecture** | Model Context Protocol (MCP) |
| **CI** | Jenkins API |
| **SCM** | GitHub API |
| **UI** | Streamlit |
| **Config** | python-dotenv |

---

## 🛠 Setup

### Prerequisites

- Python 3.8+
- Git
- Jenkins instance (or use demo mode)
- GitHub account with repo
- Groq API key

### Installation

```bash
# 1. Clone repository
git clone https://github.com/Debdatta1105/AICompiler.git
cd AICompiler

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cat > .env << EOF
GROQ_API_KEY=your_groq_api_key
GITHUB_TOKEN=your_github_token
JENKINS_URL=http://localhost:8080
JENKINS_USERNAME=your_username
API_TOKEN=your_jenkins_api_token
EOF
```

### Run

**Streamlit UI (Recommended):**
```bash
streamlit run demoapp.py
```
Then open http://localhost:8501

**CLI:**
```bash
python llm.py
```

**Verify MCP Server:**
```bash
python mcp_server.py
```

---

## 📁 Project Structure

```
.
├── mcp_server.py           # MCP server with tool implementations
├── llm.py                  # LLM agent and fix generation
├── demoapp.py              # Streamlit UI (autonomous + interactive)
├── jenkins.py              # Jenkins API client
├── generate_pr.py          # GitHub PR creation logic
├── requirements.txt        # Python dependencies
├── .env                    # Configuration (create this)
└── SETUP.md               # Detailed setup guide
```

---

## 🔐 Configuration

### Environment Variables

```env
# Groq LLM
GROQ_API_KEY=gsk_xxx

# GitHub
GITHUB_TOKEN=ghp_xxx
GITHUB_REPO=owner/repo

# Jenkins
JENKINS_URL=http://localhost:8080
JENKINS_USERNAME=username
API_TOKEN=api_token_from_jenkins
```

### Getting Credentials

**Groq API Key:**
- Go to https://console.groq.com
- Create API key
- Copy to .env

**GitHub Token:**
- Settings → Developer Settings → Personal Access Tokens
- Create token with `repo` + `workflow` scopes
- Copy to .env

**Jenkins Credentials:**
- Jenkins → Your User → Configure
- Generate new API token
- Copy username and token to .env

---

## 🚀 Examples

### Example 1: Fix Compilation Error

**Failure:**
```
Server.java:5: error: cannot find symbol
List<String> list = new ArrayList<>();
symbol: class List
```

**Agent Output:**
```json
{
  "failure_type": "compilation error",
  "root_cause": "Missing import for List",
  "can_auto_fix": true,
  "target_file": "src/Server.java",
  "operation": "insert",
  "code_patch": "import java.util.List;"
}
```

**Result:** PR created, merged, build retriggered ✅

### Example 2: Test Failure

**Failure:**
```
AssertionError: expected <200> but was <500>
```

**Analysis:** Tests pass locally but fail in CI due to configuration

**Action:** Creates PR with fix, retriggers build

---

## 🔧 Extending MCP Server

Add new tools by editing `mcp_server.py`:

```python
def my_custom_tool(self, param: str) -> dict:
    """Your custom tool"""
    try:
        # Your logic here
        return {"success": True, "result": data}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Register in get_tools()
{
    "name": "my_custom_tool",
    "description": "Does something awesome",
    "inputSchema": {
        "type": "object",
        "properties": {"param": {"type": "string"}},
        "required": ["param"]
    }
}
```

Tools automatically become available to the LLM agent!

---

## 🎓 How It Works

### 1. **Build Failure Detected**
- Jenkins build fails
- Logs are stored

### 2. **Log Analysis**
- Agent fetches logs from Jenkins
- LLM analyzes root cause
- Identifies fix strategy

### 3. **Fix Generation**
- LLM generates structured fix JSON
- Specifies file, line, operation, patch
- Calculates context for matching

### 4. **PR Creation**
- Clone repo → Create branch
- Read target file
- Apply patch (insert/replace/delete/modify)
- Commit changes
- Create GitHub PR

### 5. **Auto Retrigger** (Optional)
- Trigger Jenkins build with new branch
- Waits for results
- Reports success/failure

---

## 🔮 Future Enhancements

- [ ] Multi-language support (Python, Go, Rust)
- [ ] Slack notifications
- [ ] PR review automation
- [ ] Test coverage analysis
- [ ] Performance regression detection
- [ ] Distributed MCP server for scale
- [ ] Custom LLM model fine-tuning
- [ ] Historical fix tracking

---

## ⚠️ Limitations & Caveats

⚠️ **Auto-fixes are heuristic-based** - Not formally verified, may have edge cases  
⚠️ **Common patterns only** - Works best for compilation, import, and simple config errors  
⚠️ **Requires valid credentials** - Jenkins, GitHub, Groq API keys must be valid  
⚠️ **Rate limits** - Groq API has rate limits (check docs)  
⚠️ **File system access** - Requires read/write access to target repository  

---

## 📊 Status

| Component | Status | Notes |
|-----------|--------|-------|
| MCP Server | ✅ Working | All tools operational |
| LLM Agent | ✅ Working | Using Groq LLaMA 3.3 |
| Jenkins Integration | ✅ Working | API v2 compatible |
| GitHub Integration | ✅ Working | REST API v3 |
| Streamlit UI | ✅ Working | Autonomous + Interactive modes |
| CLI | ✅ Working | Single-shot fix mode |

---

## 💬 Support

- Check [SETUP.md](SETUP.md) for detailed setup
- Review [requirements.txt](requirements.txt) for dependencies
- Inspect `.env` for correct configuration
- Run `python mcp_server.py` to verify MCP server

---

## 📜 License

MIT License - See LICENSE file for details

---

**Made with ❤️ for faster CI/CD iteration**

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
