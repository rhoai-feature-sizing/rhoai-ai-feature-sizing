# RHOAI AI Feature Sizing

A Python tool for AI-powered feature sizing and estimation with full Jira integration pipeline, designed to help teams better estimate development effort for features and projects using [Llama Stack](https://llama-stack.readthedocs.io/en/latest/).

## 🚀 Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd rhoai-ai-feature-sizing

# Install dependencies (requires Python 3.12+)
pip install -e .

# Set up Llama Stack with Ollama
ollama run llama3.2:3b --keepalive 60m
INFERENCE_MODEL=llama3.2:3b uv run --with llama-stack llama stack build --template ollama --image-type venv --run

# Run the full Jira refinement pipeline
python main.py refine-jira-issues --project PROJ --output results/
```

## 📋 Overview

This project provides a comprehensive AI-powered pipeline for:
- **Jira Issue Refinement** - Automatic retrieval and enhancement of Jira issues
- **Epic and Story Analysis** - Structured breakdown of large initiatives  
- **AI-powered Estimation** - Intelligent story point and effort estimation
- **Full Pipeline Automation** - End-to-end processing with logging and monitoring
- **Llama Stack Integration** - Advanced AI agents for issue processing

## 🏗️ Project Structure

```
├── docs/                   # 📚 Comprehensive project documentation
├── stages/                 # � Processing pipeline stages
│   ├── epics.py           # Epic processing and breakdown
│   ├── jiras.py           # Jira issue refinement
│   ├── estimates.py       # Estimation and sizing
│   └── draft_jiras.py     # JIRA ticket generation
├── tools/                  # �️ Llama Stack agent integrations
├── prompts/                # 💬 AI prompt templates
├── main.py                 # 🎯 Main CLI application
└── pyproject.toml          # 📦 Project configuration
```

## 🎯 Key Features

### Full Jira Refinement Pipeline
- **Automated Issue Retrieval** - Llama Stack agents fetch and process Jira issues
- **Epic Decomposition** - Break down large epics into manageable stories
- **Story Enhancement** - AI-powered refinement of acceptance criteria and requirements
- **Effort Estimation** - Intelligent story point assignment with confidence levels

### Command Line Interface
```bash
# Process individual issues
python main.py refine-issue --issue-key PROJ-123

# Process entire epics
python main.py process-epic --epic-key PROJ-100 --create-stories

# Batch estimation
python main.py estimate-batch --jql "project=PROJ AND status='To Do'"

# Full pipeline execution
python main.py run-pipeline --project PROJ --output-dir results/
```

### Llama Stack Agent Integration
- **Issue Retrieval Agent** - Intelligent Jira API integration
- **Content Analysis Agent** - Deep understanding of issue context
- **Estimation Agent** - AI-driven effort calculation
- **Documentation Agent** - Automatic documentation generation

## 📚 Documentation

For comprehensive documentation, visit the [/docs](./docs/) directory:

- **[📖 Full Documentation](./docs/README.md)** - Complete documentation hub
- **[🚀 Getting Started](./docs/user-guide/getting-started.md)** - Quick start guide with new pipeline
- **[🏗️ Architecture](./docs/architecture/overview.md)** - Updated system architecture
- **[🎮 CLI Reference](./docs/user-guide/cli-reference.md)** - Command-line interface guide
- **[🔧 Pipeline Configuration](./docs/development/pipeline-configuration.md)** - Stage configuration
- **[❓ FAQ](./docs/user-guide/faq.md)** - Frequently asked questions

## 🔄 Pipeline Stages

### 1. Epic Processing (`stages/epics.py`)
- Analyze epic scope and complexity
- Decompose into constituent stories
- Generate story templates with AI assistance

### 2. Jira Issue Refinement (`stages/jiras.py`)
- Retrieve issues using Llama Stack agents
- Enhance descriptions and acceptance criteria
- Add technical requirements and dependencies

### 3. Estimation Engine (`stages/estimates.py`)
- AI-powered story point estimation
- Confidence level calculation
- Risk factor identification

### 4. Output Generation (`stages/draft_jiras.py`)
- Create refined Jira tickets
- Generate estimation reports
- Export results in multiple formats

## 🎮 Command Line Usage

### Basic Commands
```bash
# Show available commands
python main.py --help

# Process a single issue
python main.py refine-issue PROJ-123

# Process an epic with story creation
python main.py process-epic PROJ-100 --create-stories --estimate

# Estimate existing issues
python main.py estimate-issues --jql "project=PROJ AND status='To Do'"
```

### Pipeline Execution
```bash
# Full pipeline with logging
python main.py run-pipeline \
  --project PROJ \
  --include-epics \
  --estimate-all \
  --output-dir results/ \
  --log-level INFO

# Batch processing
python main.py batch-process \
  --input issues.json \
  --stages epics,jiras,estimates \
  --parallel
```

### Configuration
```bash
# Configure Jira connection
python main.py configure jira \
  --url https://company.atlassian.net \
  --username user@company.com \
  --token <api-token>

# Configure Llama Stack
python main.py configure llama-stack \
  --url http://localhost:8321 \
  --model llama3.1:8b
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./CONTRIBUTING.md) for details on:
- How to set up the development environment
- New pipeline stage development
- Coding standards and testing
- Documentation guidelines

## 🔧 Requirements

- Python 3.12+
- [Llama Stack](https://llama-stack.readthedocs.io/en/latest/) with Ollama
- Jira API access (for issue retrieval)
- Dependencies listed in `pyproject.toml`

## � Logging and Monitoring

The pipeline includes comprehensive logging:
```bash
# Enable debug logging
python main.py --log-level DEBUG run-pipeline --project PROJ

# Log to file
python main.py --log-file pipeline.log run-pipeline --project PROJ

# JSON structured logging
python main.py --log-format json run-pipeline --project PROJ
```

## 🆘 Support

- 📖 Check the [documentation](./docs/)
- ❓ Review the [FAQ](./docs/user-guide/faq.md)
- 🐛 Report issues in the repository
- 💬 See [Contributing Guide](./CONTRIBUTING.md) for help contributing

## 📄 License

[Add license information here]

---

*For detailed information about the pipeline stages, CLI commands, and Llama Stack integration, please refer to the comprehensive documentation in the [/docs](./docs/) directory.*