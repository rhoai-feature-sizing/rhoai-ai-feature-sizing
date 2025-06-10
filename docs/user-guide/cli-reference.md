# CLI Reference Guide

Complete command-line interface reference for the RHOAI AI Feature Sizing tool. The CLI provides a comprehensive set of commands for managing the full Jira refinement pipeline.

## 📋 Overview

The RHOAI AI Feature Sizing CLI is built using Python Fire and provides unified access to all pipeline operations. All commands support comprehensive logging, configuration management, and error handling.

```bash
# Basic command structure
python main.py <command> [options] [arguments]

# Get help for any command
python main.py <command> --help

# Global options available for all commands
python main.py --log-level DEBUG <command>
python main.py --log-file pipeline.log <command>
```

## 🎯 Core Pipeline Commands

### `refine-issue` - Process Individual Issues

Refine and enhance individual Jira issues with AI-powered analysis.

```bash
# Basic issue refinement
python main.py refine-issue PROJ-123

# Refine with specific output format
python main.py refine-issue PROJ-123 --output-format json --output-file results.json

# Refine with custom model
python main.py refine-issue PROJ-123 --model llama3.1:8b --temperature 0.7

# Include estimation in refinement
python main.py refine-issue PROJ-123 --include-estimation --confidence-threshold 0.8
```

**Options:**
- `--output-format` - Output format: `json`, `yaml`, `csv`, `jira` (default: `json`)
- `--output-file` - File to save results to
- `--model` - Llama Stack model to use
- `--temperature` - AI model temperature (0.0-1.0)
- `--include-estimation` - Include story point estimation
- `--confidence-threshold` - Minimum confidence level for estimates
- `--dry-run` - Preview changes without applying

**Examples:**
```bash
# Refine multiple issues
python main.py refine-issue PROJ-123 PROJ-124 PROJ-125

# Refine with custom prompt template
python main.py refine-issue PROJ-123 --prompt-template custom_refinement.md

# Save detailed logs
python main.py --log-level DEBUG refine-issue PROJ-123 --log-file issue-123.log
```

### `process-epic` - Epic Processing and Decomposition

Process epics and break them down into manageable user stories.

```bash
# Basic epic processing
python main.py process-epic PROJ-100

# Process epic and create stories
python main.py process-epic PROJ-100 --create-stories --estimate-stories

# Process with custom story template
python main.py process-epic PROJ-100 --story-template templates/story.json

# Batch process multiple epics
python main.py process-epic PROJ-100 PROJ-101 PROJ-102 --parallel
```

**Options:**
- `--create-stories` - Create user stories from epic analysis
- `--estimate-stories` - Include story point estimation for generated stories
- `--story-template` - Custom template for story generation
- `--max-stories` - Maximum number of stories to generate per epic
- `--parallel` - Process multiple epics in parallel
- `--dependency-analysis` - Analyze dependencies between stories
- `--output-dir` - Directory to save epic and story outputs

**Examples:**
```bash
# Complete epic processing pipeline
python main.py process-epic PROJ-100 \
  --create-stories \
  --estimate-stories \
  --dependency-analysis \
  --output-dir epics/PROJ-100/

# Process epic with specific model settings
python main.py process-epic PROJ-100 \
  --model llama3.1:8b \
  --temperature 0.5 \
  --max-stories 12
```

### `estimate-batch` - Batch Issue Estimation

Perform estimation on multiple issues using JQL queries or issue lists.

```bash
# Estimate using JQL query
python main.py estimate-batch --jql "project=PROJ AND status='To Do'"

# Estimate specific issues
python main.py estimate-batch --issues PROJ-123,PROJ-124,PROJ-125

# Estimate with confidence analysis
python main.py estimate-batch \
  --jql "project=PROJ AND status='To Do'" \
  --confidence-analysis \
  --min-confidence 0.7

# Export estimation results
python main.py estimate-batch \
  --jql "project=PROJ" \
  --export-format csv \
  --export-file estimations.csv
```

**Options:**
- `--jql` - JQL query to select issues for estimation
- `--issues` - Comma-separated list of issue keys
- `--confidence-analysis` - Include confidence metrics
- `--min-confidence` - Minimum confidence threshold
- `--export-format` - Export format: `json`, `csv`, `excel`
- `--export-file` - File to export results to
- `--batch-size` - Number of issues to process in each batch
- `--parallel-batches` - Process batches in parallel

### `run-pipeline` - Full Pipeline Execution

Execute the complete Jira refinement pipeline with all stages.

```bash
# Full pipeline for a project
python main.py run-pipeline --project PROJ

# Pipeline with specific stages
python main.py run-pipeline \
  --project PROJ \
  --stages epics,jiras,estimates \
  --output-dir results/

# Pipeline with custom configuration
python main.py run-pipeline \
  --project PROJ \
  --config pipeline.yaml \
  --include-epics \
  --estimate-all

# Parallel pipeline execution
python main.py run-pipeline \
  --project PROJ \
  --parallel-stages \
  --max-workers 4 \
  --batch-size 10
```

**Options:**
- `--project` - Jira project key to process
- `--stages` - Comma-separated list of stages to run
- `--output-dir` - Directory for pipeline outputs
- `--config` - Configuration file for pipeline settings
- `--include-epics` - Include epic processing in pipeline
- `--estimate-all` - Estimate all processed issues
- `--parallel-stages` - Run compatible stages in parallel
- `--max-workers` - Maximum number of parallel workers
- `--batch-size` - Batch size for processing
- `--resume-from` - Resume pipeline from specific stage

**Examples:**
```bash
# Complete project processing
python main.py run-pipeline \
  --project PROJ \
  --include-epics \
  --estimate-all \
  --output-dir results/PROJ/ \
  --log-level INFO

# Selective stage execution
python main.py run-pipeline \
  --project PROJ \
  --stages jiras,estimates \
  --jql "status='To Do' AND assignee=currentUser()"
```

## ⚙️ Configuration Commands

### `configure` - System Configuration

Manage system configuration for Jira, Llama Stack, and pipeline settings.

```bash
# Configure Jira connection
python main.py configure jira \
  --url https://company.atlassian.net \
  --username user@company.com \
  --token <api-token>

# Configure Llama Stack
python main.py configure llama-stack \
  --url http://localhost:8321 \
  --model llama3.2:3b \
  --timeout 30

# Configure pipeline defaults
python main.py configure pipeline \
  --default-stages epics,jiras,estimates \
  --batch-size 5 \
  --parallel-workers 2

# Show current configuration
python main.py configure show
```

**Subcommands:**
- `jira` - Configure Jira API connection
- `llama-stack` - Configure Llama Stack settings
- `pipeline` - Configure pipeline defaults
- `show` - Display current configuration
- `validate` - Validate configuration settings
- `reset` - Reset to default configuration

### `configure jira` Options:
- `--url` - Jira instance URL
- `--username` - Jira username/email
- `--token` - Jira API token
- `--verify-ssl` - Verify SSL certificates (default: true)
- `--timeout` - API request timeout (seconds)

### `configure llama-stack` Options:
- `--url` - Llama Stack server URL
- `--model` - Default model to use
- `--timeout` - Request timeout (seconds)
- `--max-retries` - Maximum retry attempts
- `--temperature` - Default temperature setting

## 🔍 Query and Information Commands

### `list-projects` - List Available Projects

```bash
# List all accessible projects
python main.py list-projects

# List projects with issue counts
python main.py list-projects --include-counts

# Filter projects by name
python main.py list-projects --filter "PROJ*"
```

### `list-issues` - List Project Issues

```bash
# List issues in project
python main.py list-issues --project PROJ

# List with JQL filter
python main.py list-issues --jql "project=PROJ AND status='To Do'"

# List with issue details
python main.py list-issues --project PROJ --include-details
```

### `show-issue` - Display Issue Details

```bash
# Show issue details
python main.py show-issue PROJ-123

# Show with estimation history
python main.py show-issue PROJ-123 --include-history

# Show in specific format
python main.py show-issue PROJ-123 --format yaml
```

## 📊 Reporting and Analysis Commands

### `generate-report` - Generate Analysis Reports

```bash
# Generate project estimation report
python main.py generate-report estimation \
  --project PROJ \
  --output estimation-report.html

# Generate pipeline execution report
python main.py generate-report pipeline \
  --execution-id 12345 \
  --format pdf

# Generate trend analysis
python main.py generate-report trends \
  --project PROJ \
  --date-range "2024-01-01,2024-12-31"
```

### `analyze-performance` - Performance Analysis

```bash
# Analyze estimation accuracy
python main.py analyze-performance estimation \
  --project PROJ \
  --confidence-threshold 0.8

# Analyze pipeline performance
python main.py analyze-performance pipeline \
  --execution-logs logs/
```

## 🛠️ Utility Commands

### `validate` - Validation Commands

```bash
# Validate configuration
python main.py validate config

# Validate Jira connection
python main.py validate jira

# Validate Llama Stack connection
python main.py validate llama-stack

# Validate all systems
python main.py validate all
```

### `cleanup` - Cleanup Operations

```bash
# Clean temporary files
python main.py cleanup temp

# Clean old logs
python main.py cleanup logs --older-than 30d

# Clean cached data
python main.py cleanup cache
```

### `export` - Data Export

```bash
# Export project data
python main.py export project PROJ --format json

# Export estimation data
python main.py export estimations \
  --project PROJ \
  --format csv \
  --output estimations.csv

# Export configuration
python main.py export config --output config-backup.yaml
```

## 🔧 Global Options

All commands support these global options:

### Logging Options
- `--log-level` - Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- `--log-file` - File to write logs to
- `--log-format` - Log format: `text`, `json`, `structured`
- `--quiet` - Suppress output except errors
- `--verbose` - Enable verbose output

### Configuration Options
- `--config-file` - Configuration file to use
- `--profile` - Configuration profile to use
- `--dry-run` - Preview operations without execution

### Performance Options
- `--timeout` - Global timeout for operations
- `--max-retries` - Maximum retry attempts
- `--parallel` - Enable parallel processing where available
- `--cache` - Enable/disable caching

## 📝 Configuration Files

### Pipeline Configuration (`pipeline.yaml`)
```yaml
jira:
  url: "https://company.atlassian.net"
  username: "user@company.com"
  timeout: 30

llama_stack:
  url: "http://localhost:8321"
  default_model: "llama3.2:3b"
  temperature: 0.7

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

### Stage Configuration (`stages.yaml`)
```yaml
epics:
  max_stories_per_epic: 10
  story_template: "templates/story.json"
  dependency_analysis: true

jiras:
  enhancement_level: "detailed"
  include_technical_requirements: true
  validation_rules: ["completeness", "clarity"]

estimates:
  confidence_threshold: 0.7
  estimation_method: "story_points"
  include_risk_analysis: true
```

## 🚀 Quick Start Examples

### First-Time Setup
```bash
# Configure system
python main.py configure jira --url https://company.atlassian.net
python main.py configure llama-stack --url http://localhost:8321

# Validate configuration
python main.py validate all

# Process first issue
python main.py refine-issue PROJ-123
```

### Daily Workflow
```bash
# Process new issues
python main.py estimate-batch --jql "status='To Do' AND updated>='-1d'"

# Run full pipeline for sprint
python main.py run-pipeline --project PROJ --jql "sprint='Current Sprint'"

# Generate daily report
python main.py generate-report estimation --project PROJ --format html
```

### Bulk Processing
```bash
# Process entire project
python main.py run-pipeline \
  --project PROJ \
  --include-epics \
  --estimate-all \
  --parallel-stages \
  --output-dir results/bulk-$(date +%Y%m%d)/

# Generate comprehensive report
python main.py generate-report project \
  --project PROJ \
  --include-trends \
  --format pdf \
  --output PROJ-analysis.pdf
```

## ❗ Error Handling

The CLI provides comprehensive error handling with:

- **Detailed error messages** - Clear descriptions of what went wrong
- **Retry mechanisms** - Automatic retry for transient failures
- **Graceful degradation** - Continue processing when possible
- **Recovery suggestions** - Actionable steps to resolve issues

Common error resolution:
```bash
# Connection issues
python main.py validate jira  # Check Jira connectivity
python main.py validate llama-stack  # Check Llama Stack

# Configuration issues
python main.py configure show  # Review current settings
python main.py configure validate  # Validate configuration

# Permission issues
python main.py list-projects  # Test project access
```

## 📚 Additional Resources

- [Getting Started Guide](getting-started.md) - Complete setup and first steps
- [Pipeline Configuration](../development/pipeline-configuration.md) - Advanced configuration
- [Troubleshooting](../user-guide/troubleshooting.md) - Common issues and solutions
- [API Reference](../api/endpoints.md) - Programmatic access options

---

*This CLI reference covers all available commands and options. For examples of common workflows, see the [Getting Started Guide](getting-started.md).*