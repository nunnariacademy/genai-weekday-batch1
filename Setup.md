# Complete Development Environment Setup Guide

A streamlined guide for setting up Python, Git, VS Code, Jupyter, LangChain, and Ollama for AI/ML development.

---

## 📋 Quick Overview

This guide covers:
1. **Python** - Python installation
2. **Git & GitHub** - Version control and remote repository access
3. **VS Code** - Code editor with Jupyter extension
4. **Virtual Environments** - Project isolation with venv
5. **Jupyter** - Interactive notebooks
6. **LangChain** - LLM application framework
7. **Ollama** - Local LLM runtime

---

## 1. Python Installation

### Install Python

**Windows:**
```bash
# Download Python 3.14.3 installer:
https://www.python.org/ftp/python/3.14.3/python-3.14.3-amd64.exe

# During installation:
# ✅ CHECK "Add Python to PATH" (IMPORTANT!)
# ✅ CHECK "Install for all users" (optional)
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv -y
```

**Linux (Fedora):**
```bash
sudo dnf install python3 python3-pip -y
```

**macOS:**
```bash
# Using Homebrew (recommended):
brew install python

# Or download from: https://www.python.org/downloads/
```

### Verify Installation
```bash
python --version  # Should show Python 3.14.3
pip --version
```

---

## 2. Git & GitHub Setup

### Install Git

**Windows:**
```bash
# Download and install from:
https://git-scm.com/download/win
# Or use winget:
winget install Git.Git
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install git -y
```

**macOS:**
```bash
# Using Homebrew:
brew install git
# Or use Xcode Command Line Tools:
xcode-select --install
```

### Configure Git
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Setup GitHub

1. **Create account**: [github.com/signup](https://github.com/signup)

2. **That's it!** Git will prompt for credentials when you push/pull. Use HTTPS URLs for repositories.

---

## 3. VS Code Installation

**Windows:**
```bash
# Download from: https://code.visualstudio.com/
# Or use winget:
winget install Microsoft.VisualStudioCode
```

**Linux:**
```bash
# Using Snap (most distros):
sudo snap install code --classic

# Or download .deb/.rpm from: https://code.visualstudio.com/
```

**macOS:**
```bash
brew install --cask visual-studio-code
```

### Install Jupyter Extension

**Method 1: Via VS Code UI**
1. Open VS Code
2. Press `Ctrl+Shift+X` (Windows/Linux) or `Cmd+Shift+X` (macOS)
3. Search for "Jupyter"
4. Install "Jupyter" by Microsoft

---

## 4. Virtual Environment (venv)

### Create Virtual Environment

```bash
# Navigate to your project directory
cd /path/to/your/project

# Create venv
python -m venv venv
```

### Activate Virtual Environment

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
# If you get an error, run this once as admin:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### Verify Activation
```bash
# You should see (venv) in your prompt
# Check Python location:
which python  # Linux/macOS
where python  # Windows
```

### Deactivate
```bash
deactivate
```

---

## 5. Jupyter Installation

**Install globally (recommended for beginners):**
```bash
pip install jupyter jupyterlab
```

**Launch Jupyter:**
```bash
# Jupyter Notebook (classic):
jupyter notebook

# JupyterLab (modern):
jupyter lab
```

**Use Jupyter in VS Code:**
1. Create a `.ipynb` file in VS Code
2. VS Code will automatically use the Jupyter extension
3. Select your venv as the kernel (click kernel picker in top-right)

---

## 6. LangChain Setup

### Install LangChain

**Basic installation:**
```bash
pip install langchain langchain-community
```

**Install from requirements.txt (recommended):**
```bash
pip install -r requirements.txt
```

### Requirements.txt Contents

The included `requirements.txt` contains:
- **LangChain Core**: Framework and community integrations
- **LLM Providers**: OpenAI, Anthropic (Claude), Google Gemini, Ollama
- **Vector Stores**: ChromaDB, FAISS (for RAG applications)
- **Utilities**: Environment management, text processing

### Environment Variables

Create a `.env` file in your project root:
```bash
# .env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
```

**Load in Python:**
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 7. Ollama Installation

### Install Ollama

**Windows:**
```bash
# Download from: https://ollama.ai/download/windows
# Run the installer
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**macOS:**
```bash
# Download from: https://ollama.ai/download/mac
# Or use Homebrew:
brew install ollama
```

### Pull Models

```bash
# Popular models:
ollama pull "model-name"

# List installed models:
ollama list

# Run model:
ollama run llama3.2
```

### Use Ollama with LangChain

```python
from langchain_community.llms import Ollama

llm = Ollama(model="llama3.2")
response = llm.invoke("What is LangChain?")
print(response)
```

