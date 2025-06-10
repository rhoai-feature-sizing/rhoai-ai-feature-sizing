# Getting Started Guide

Welcome to RHOAI AI Feature Sizing! This guide will help you set up and start using the comprehensive Jira refinement pipeline with Llama Stack agents for intelligent issue processing and estimation.

## 🎯 What is RHOAI AI Feature Sizing?

RHOAI AI Feature Sizing is an AI-powered tool that provides:

- **Complete Jira Refinement Pipeline** - Automated issue processing from epics to estimates
- **Epic Decomposition** - Break down large initiatives into manageable user stories
- **Intelligent Issue Enhancement** - AI-powered content refinement and requirement analysis
- **Automated Estimation** - Story point assignment with confidence metrics
- **Llama Stack Integration** - Advanced AI agents for sophisticated issue processing

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have:

- **Python 3.12+** installed
- **Access to a Jira instance** with API token
- **Ollama** installed for local AI models
- **Basic familiarity** with command-line interfaces

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd rhoai-ai-feature-sizing

# Install dependencies
pip install -e .

# Verify installation
python main.py --help
```

### 2. Set up Llama Stack with Ollama

```bash
# Pull and start the AI model
ollama pull llama3.2:3b
ollama run llama3.2:3b --keepalive 60m

# Set up Llama Stack server
INFERENCE_MODEL=llama3.2:3b uv run --with llama-stack llama stack build \
  --template ollama \
  --image-type venv \
  --run
```

The Llama Stack server will start on `http://localhost:8321` by default.

### 3. Configure Jira Connection

```bash
# Configure your Jira instance
python main.py configure jira \
  --url https://your-company.atlassian.net \
  --username your-email@company.com \
  --token YOUR_API_TOKEN

# Validate the connection
python main.py validate jira
```

**Getting a Jira API Token:**
1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Label it "RHOAI Feature Sizing"
4. Copy the generated token

### 4. Configure Llama Stack

```bash
# Configure Llama Stack connection
python main.py configure llama-stack \
  --url http://localhost:8321 \
  --model llama3.2:3b

# Validate the connection
python main.py validate llama-stack
```

### 5. Your First Issue Refinement

```bash
# Process a single issue
python main.py refine-issue PROJ-123

# View the results
cat results/PROJ-123-refined.json
```

## 🔄 Understanding the Pipeline

The RHOAI AI Feature Sizing pipeline consists of four main stages:

### Stage 1: Epic Processing (`stages/epics.py`)
- Analyzes epic scope and objectives
- Decomposes epics into constituent user stories
- Generates story templates with AI assistance
- Maps dependencies between stories

### Stage 2: Jira Issue Refinement (`stages/jiras.py`)
- Retrieves issues using intelligent Llama Stack agents
- Enhances descriptions and acceptance criteria
- Adds technical requirements and implementation details
- Validates content quality and completeness

### Stage 3: Estimation Engine (`stages/estimates.py`)
- Performs multi-dimensional complexity analysis
- Assigns story points using AI-driven estimation
- Calculates confidence levels for estimates
- Identifies potential implementation risks

### Stage 4: Output Generation (`stages/draft_jiras.py`)
- Creates enhanced Jira tickets with refined content
- Generates comprehensive estimation reports
- Exports results in multiple formats (JSON, CSV, Jira-ready)
- Prepares integration data for external systems

## 📋 Common Workflows

### Workflow 1: Process Individual Issues

Perfect for refining specific issues or testing the system.

```bash
# Basic issue refinement
python main.py refine-issue PROJ-123

# Include estimation in the refinement
python main.py refine-issue PROJ-123 --include-estimation

# Process multiple issues
python main.py refine-issue PROJ-123 PROJ-124 PROJ-125

# Save results to specific file
python main.py refine-issue PROJ-123 \
  --output-format json \
  --output-file refined-issue-123.json
```

### Workflow 2: Epic Decomposition

Break down large epics into manageable stories.

```bash
# Analyze an epic
python main.py process-epic PROJ-100

# Create user stories from epic
python main.py process-epic PROJ-100 \
  --create-stories \
  --estimate-stories \
  --output-dir epics/PROJ-100/

# Process multiple epics in parallel
python main.py process-epic PROJ-100 PROJ-101 PROJ-102 --parallel
```

### Workflow 3: Batch Estimation

Estimate multiple issues efficiently.

```bash
# Estimate all open issues in a project
python main.py estimate-batch \
  --jql "project=PROJ AND status='To Do'"

# Estimate specific issues
python main.py estimate-batch \
  --issues PROJ-123,PROJ-124,PROJ-125

# Export estimation results
python main.py estimate-batch \
  --jql "project=PROJ AND status='To Do'" \
  --export-format csv \
  --export-file sprint-estimates.csv
```

### Workflow 4: Full Pipeline Execution

Run the complete end-to-end pipeline.

```bash
# Process entire project
python main.py run-pipeline --project PROJ

# Selective stage execution
python main.py run-pipeline \
  --project PROJ \
  --stages epics,jiras,estimates \
  --output-dir results/

# Full pipeline with all options
python main.py run-pipeline \
  --project PROJ \
  --include-epics \
  --estimate-all \
  --parallel-stages \
  --output-dir results/PROJ-$(date +%Y%m%d)/ \
  --log-level INFO
```

## 🛠️ Configuration

### Project Configuration

Create a `pipeline.yaml` file for project-specific settings:

```yaml
# pipeline.yaml
jira:
  url: "https://company.atlassian.net"
  username: "user@company.com"
  timeout: 30
  default_project: "PROJ"

llama_stack:
  url: "http://localhost:8321"
  default_model: "llama3.2:3b"
  temperature: 0.7
  timeout: 60

pipeline:
  default_stages: ["epics", "jiras", "estimates"]
  batch_size: 5
  parallel_workers: 2
  output_format: "json"

logging:
  level: "INFO"
  format: "structured"
  file: "pipeline.log"
```

Use the configuration file:
```bash
python main.py run-pipeline --config pipeline.yaml --project PROJ
```

### Stage-Specific Configuration

Create a `stages.yaml` file for detailed stage configuration:

```yaml
# stages.yaml
epics:
  max_stories_per_epic: 10
  story_template: "templates/story.json"
  dependency_analysis: true
  ai_temperature: 0.6

jiras:
  enhancement_level: "detailed"  # basic, detailed, comprehensive
  include_technical_requirements: true
  validation_rules: 
    - "completeness"
    - "clarity"
    - "technical_feasibility"
  ai_temperature: 0.5

estimates:
  confidence_threshold: 0.7
  estimation_method: "story_points"  # story_points, hours, t_shirt
  include_risk_analysis: true
  calibration_data: "historical_estimates.json"
  ai_temperature: 0.3

output:
  formats: ["json", "csv"]
  include_metadata: true
  compress_large_outputs: true
```

## 📊 Understanding Output

### Refined Issue Output

When you process an issue, you'll get structured output like this:

```json
{
  "issue_key": "PROJ-123",
  "original": {
    "summary": "User login feature",
    "description": "Users need to log in"
  },
  "refined": {
    "summary": "Implement secure user authentication system",
    "description": "As a user, I want to securely log into the system...",
    "acceptance_criteria": [
      "User can log in with email and password",
      "System validates credentials against database",
      "Failed login attempts are logged and limited"
    ],
    "technical_requirements": [
      "Implement password hashing with bcrypt",
      "Add rate limiting for login attempts",
      "Integrate with OAuth2 providers"
    ]
  },
  "estimation": {
    "story_points": 5,
    "confidence": 0.85,
    "reasoning": "Standard authentication implementation with modern security practices",
    "risk_factors": ["Third-party OAuth integration complexity"]
  },
  "metadata": {
    "processed_at": "2024-01-15T10:30:00Z",
    "model_used": "llama3.2:3b",
    "processing_time": 12.5
  }
}
```

### Pipeline Execution Report

Full pipeline runs generate comprehensive reports:

```json
{
  "pipeline_execution": {
    "project": "PROJ",
    "started_at": "2024-01-15T09:00:00Z",
    "completed_at": "2024-01-15T09:45:00Z",
    "duration_seconds": 2700,
    "status": "completed"
  },
  "stages": {
    "epics": {
      "processed": 3,
      "stories_created": 24,
      "duration_seconds": 480
    },
    "jiras": {
      "processed": 45,
      "enhanced": 43,
      "skipped": 2,
      "duration_seconds": 1200
    },
    "estimates": {
      "processed": 43,
      "estimated": 41,
      "confidence_avg": 0.78,
      "duration_seconds": 600
    }
  },
  "summary": {
    "total_issues_processed": 45,
    "total_story_points": 234,
    "avg_confidence": 0.78,
    "epics_decomposed": 3,
    "stories_created": 24
  }
}
```

## 🎮 Advanced Usage

### Custom Prompt Templates

Create custom prompts for specific domains:

```bash
# Create custom refinement prompt
cat > prompts/security_refinement.md << EOF
# Security Feature Refinement

You are refining a security-related feature. Focus on:
- Security requirements and compliance
- Threat modeling considerations
- Authentication and authorization
- Data protection requirements

Original Issue: {issue_description}

Please enhance this issue with security-focused requirements.
EOF

# Use custom prompt
python main.py refine-issue PROJ-123 \
  --prompt-template prompts/security_refinement.md
```

### Parallel Processing

For large projects, use parallel processing:

```bash
# Process with parallel stages
python main.py run-pipeline \
  --project PROJ \
  --parallel-stages \
  --max-workers 4 \
  --batch-size 10

# Parallel batch estimation
python main.py estimate-batch \
  --jql "project=PROJ" \
  --parallel-batches \
  --batch-size 20
```

### Logging and Monitoring

Enable comprehensive logging:

```bash
# Debug logging to file
python main.py --log-level DEBUG \
  --log-file debug.log \
  run-pipeline --project PROJ

# Structured JSON logging
python main.py --log-format json \
  run-pipeline --project PROJ > pipeline.jsonl
```

Monitor real-time progress:
```bash
# In another terminal
tail -f pipeline.log | grep "PROGRESS"
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Llama Stack Connection Failed

```bash
# Check if Ollama is running
ollama list

# Restart Llama Stack
pkill -f "llama stack"
INFERENCE_MODEL=llama3.2:3b uv run --with llama-stack llama stack build \
  --template ollama --image-type venv --run

# Validate connection
python main.py validate llama-stack
```

#### 2. Jira Authentication Error

```bash
# Test Jira connection
python main.py validate jira

# Check configuration
python main.py configure show

# Reconfigure if needed
python main.py configure jira --url https://company.atlassian.net
```

#### 3. Performance Issues

```bash
# Reduce batch size
python main.py run-pipeline --project PROJ --batch-size 3

# Use lighter model
python main.py configure llama-stack --model llama3.2:1b

# Enable caching
python main.py run-pipeline --project PROJ --cache
```

#### 4. Memory Issues

```bash
# Process in smaller batches
python main.py estimate-batch \
  --jql "project=PROJ" \
  --batch-size 5 \
  --max-workers 2

# Clear cache periodically
python main.py cleanup cache
```

### Getting Help

```bash
# Command help
python main.py <command> --help

# Validate system
python main.py validate all

# Check configuration
python main.py configure show

# View logs
python main.py --log-level DEBUG <command>
```

## 📈 Best Practices

### 1. Start Small
Begin with individual issues before running full pipelines:
```bash
# Test with one issue first
python main.py refine-issue PROJ-123
```

### 2. Use Appropriate Batch Sizes
```bash
# For development/testing
python main.py run-pipeline --project PROJ --batch-size 3

# For production
python main.py run-pipeline --project PROJ --batch-size 10
```

### 3. Configure Logging
```bash
# Always use appropriate logging
python main.py --log-level INFO --log-file pipeline.log \
  run-pipeline --project PROJ
```

### 4. Validate Before Processing
```bash
# Always validate system health
python main.py validate all
```

### 5. Use Configuration Files
Create project-specific configuration files for consistent results.

### 6. Monitor Resource Usage
```bash
# Monitor system resources during processing
top -p $(pgrep -f "python main.py")
```

## 🎯 Next Steps

Now that you're set up, explore these advanced features:

1. **[CLI Reference](cli-reference.md)** - Complete command documentation
2. **[Pipeline Configuration](../development/pipeline-configuration.md)** - Advanced configuration options
3. **[Architecture Overview](../architecture/overview.md)** - Understanding the system design
4. **[API Documentation](../api/endpoints.md)** - Programmatic access options

## 🆘 Need Help?

- 📖 Check the [FAQ](faq.md) for common questions
- 🔧 Review [Troubleshooting](troubleshooting.md) for solutions
- 🏗️ See [Architecture Overview](../architecture/overview.md) for system design
- 💬 Refer to [Contributing Guide](../../CONTRIBUTING.md) for development help

---

*Congratulations! You're now ready to use RHOAI AI Feature Sizing. Start with individual issue refinement and gradually explore the full pipeline capabilities.*