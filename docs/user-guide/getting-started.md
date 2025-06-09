# Getting Started

Welcome to RHOAI AI Feature Sizing! This guide will help you get up and running quickly.

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- UV package manager (recommended) or pip
- Access to LLaMA Stack or compatible AI service
- JIRA access (for JIRA integration features)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rhoai-ai-feature-sizing
   ```

2. **Install dependencies using UV (recommended)**
   ```bash
   uv sync
   ```
   
   Or using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```bash
   python main.py --help
   ```

### Basic Usage

#### Running the Tool

The tool is designed with a stage-based approach:

```bash
# Basic execution
python main.py

# With Fire CLI (auto-generated commands)
python main.py <stage> <options>
```

#### Feature Refinement

Refine and analyze features using AI:

```bash
python -m stages.refine_feature --input "feature description"
```

#### JIRA Integration

Work with JIRA tickets:

```bash
python -m tools.mcp_jira --action create --title "Feature Title"
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# AI Configuration
LLAMA_STACK_ENDPOINT=your_endpoint_here
LLAMA_STACK_API_KEY=your_api_key_here

# JIRA Configuration
JIRA_URL=your_jira_instance_url
JIRA_USERNAME=your_username
JIRA_API_TOKEN=your_api_token
JIRA_PROJECT_KEY=your_project_key
```

### AI Model Setup

1. Configure your LLaMA Stack endpoint
2. Ensure API access and authentication
3. Test connection with a simple prompt

### JIRA Setup

1. Generate a JIRA API token
2. Configure project access permissions
3. Test connection with basic API calls

## 🎯 Common Workflows

### 1. Feature Analysis Workflow

```bash
# Step 1: Refine feature description
python -m stages.refine_feature --input "Raw feature description"

# Step 2: Generate size estimates
python -m stages.estimate --feature "refined_feature.json"

# Step 3: Create JIRA tickets
python -m stages.draft_jiras --estimates "estimates.json"
```

### 2. JIRA-First Workflow

```bash
# Start with existing JIRA ticket
python -m tools.mcp_jira --fetch PROJ-123

# Analyze and refine
python -m stages.refine_feature --jira-input PROJ-123

# Update with estimates
python -m stages.estimate --update-jira PROJ-123
```

## 🆘 Troubleshooting

### Common Issues

**"Module not found" errors**
- Ensure you're in the correct directory
- Check Python path and virtual environment
- Reinstall dependencies

**AI service connection errors**
- Verify API credentials and endpoint
- Check network connectivity
- Review service status

**JIRA authentication failures**
- Verify API token and permissions
- Check JIRA URL format
- Test with simpler API calls

### Getting Help

- Check the [FAQ](./faq.md) for common questions
- Review [API Documentation](../api/endpoints.md) for detailed usage
- See [Development Setup](../development/setup.md) for advanced configuration

## 📚 Next Steps

- Read the [Architecture Overview](../architecture/overview.md) to understand the system
- Explore [AI Components](../ai/prompts.md) for prompt customization
- Check [JIRA Integration](../jira/configuration.md) for advanced JIRA features
- Review [Contributing Guidelines](../../CONTRIBUTING.md) to contribute to the project

---

*Need help? Check our [FAQ](./faq.md) or reach out to the development team.*