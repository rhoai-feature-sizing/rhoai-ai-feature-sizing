# RHOAI AI Feature Sizing Documentation

Welcome to the comprehensive documentation for RHOAI AI Feature Sizing - an AI-powered tool for intelligent Jira issue refinement and estimation using [Llama Stack](https://llama-stack.readthedocs.io/en/latest/).

## 🎯 What's New

### 🚀 Latest Updates
- **Full Jira Refinement Pipeline** - Complete end-to-end processing from epics to estimates
- **Llama Stack Agent Integration** - Advanced AI agents for intelligent issue processing
- **Command-Line Interface** - Comprehensive CLI with pipeline orchestration
- **Logging and Monitoring** - Complete observability with structured logging
- **Removal of Deprecated Tools** - Replaced legacy Jira fetching with agent-based approach

### 🔄 Pipeline Stages
1. **Epic Processing** (`stages/epics.py`) - Epic analysis and story decomposition
2. **Jira Issue Refinement** (`stages/jiras.py`) - Intelligent issue enhancement
3. **Estimation Engine** (`stages/estimates.py`) - AI-powered story point estimation
4. **Output Generation** (`stages/draft_jiras.py`) - Multi-format result generation

## � Documentation Structure

### 🚀 Getting Started
- **[🎯 Quick Start](user-guide/getting-started.md)** - Get up and running in minutes
- **[🎮 CLI Reference](user-guide/cli-reference.md)** - Complete command-line interface guide
- **[❓ FAQ](user-guide/faq.md)** - Frequently asked questions and solutions

### 🏗️ Architecture & Design
- **[📖 System Overview](architecture/overview.md)** - Complete architecture with pipeline stages
- **[🎯 Design Decisions](architecture/decisions.md)** - Key architectural decisions and rationale

### �️ Development
- **[⚙️ Development Setup](development/setup.md)** - Development environment configuration
- **[📏 Coding Standards](development/standards.md)** - Code quality and style guidelines  
- **[🧪 Testing Guide](development/testing.md)** - Testing strategies and tools
- **[� Pipeline Configuration](development/pipeline-configuration.md)** - Advanced pipeline customization

### 🔌 API & Integration
- **[🌐 API Endpoints](api/endpoints.md)** - Complete API reference and examples
- **[🔐 Authentication](api/authentication.md)** - Authentication methods and security

### � Deployment
- **[📦 Installation Guide](deployment/installation.md)** - Production deployment strategies
- **[⚙️ Configuration](deployment/configuration.md)** - Environment and system configuration

## 🎮 Quick Navigation

### For New Users
1. 📖 **[Getting Started](user-guide/getting-started.md)** - Complete setup guide
2. 🎮 **[CLI Reference](user-guide/cli-reference.md)** - Learn the commands
3. ❓ **[FAQ](user-guide/faq.md)** - Common questions

### For Developers
1. ⚙️ **[Development Setup](development/setup.md)** - Set up development environment
2. 🏗️ **[Architecture Overview](architecture/overview.md)** - Understand the system
3. � **[Pipeline Configuration](development/pipeline-configuration.md)** - Customize the pipeline

### For Operators
1. 📦 **[Installation Guide](deployment/installation.md)** - Deploy in production
2. ⚙️ **[Configuration](deployment/configuration.md)** - Configure for your environment
3. 🔐 **[Authentication](api/authentication.md)** - Set up security

## 🎯 Core Features

### � Full Jira Refinement Pipeline
```bash
# Complete project processing
python main.py run-pipeline --project PROJ --include-epics --estimate-all
```

- **Epic Decomposition** - Break down large initiatives into manageable stories
- **Issue Enhancement** - AI-powered content refinement and requirement analysis
- **Automated Estimation** - Story point assignment with confidence metrics
- **Multi-format Output** - JSON, CSV, and Jira-ready exports

### 🎮 Command-Line Interface

#### Process Individual Issues
```bash
python main.py refine-issue PROJ-123 --include-estimation
```

#### Epic Processing
```bash
python main.py process-epic PROJ-100 --create-stories --estimate-stories
```

#### Batch Estimation
```bash
python main.py estimate-batch --jql "project=PROJ AND status='To Do'"
```

#### Full Pipeline
```bash
python main.py run-pipeline --project PROJ --parallel-stages --output-dir results/
```

### 🤖 Llama Stack Agent Integration

#### Specialized Agents
- **Jira Retrieval Agent** - Intelligent API integration and issue fetching
- **Content Analysis Agent** - Deep understanding and enhancement
- **Estimation Agent** - Multi-dimensional complexity assessment
- **Documentation Agent** - Comprehensive output generation

#### Agent Configuration
```yaml
# agents.yaml
jira_retrieval_agent:
  model: "llama3.2:3b"
  temperature: 0.3
  capabilities: ["jira_api_interaction", "issue_filtering", "batch_processing"]
```

### 📊 Comprehensive Logging
```bash
# Structured logging with monitoring
python main.py --log-level INFO --log-format json run-pipeline --project PROJ
```

## � Documentation Status

| Section | Status | Last Updated | Notes |
|---------|--------|--------------|-------|
| **User Guides** | ✅ Complete | 2024-01-15 | Updated with new CLI and pipeline |
| **Architecture** | ✅ Complete | 2024-01-15 | Reflects new agent-based design |
| **Development** | ✅ Complete | 2024-01-15 | Includes pipeline configuration |
| **API Reference** | ✅ Complete | 2024-01-15 | Updated for new endpoints |
| **Deployment** | ✅ Complete | 2024-01-15 | Production-ready guidance |

## 🎯 Common Workflows

### Daily Development Workflow
```bash
# 1. Process new issues
python main.py estimate-batch --jql "status='To Do' AND updated>='-1d'"

# 2. Refine specific issues
python main.py refine-issue PROJ-123 --include-estimation

# 3. Generate reports
python main.py generate-report estimation --project PROJ
```

### Sprint Planning Workflow
```bash
# 1. Process sprint backlog
python main.py run-pipeline --project PROJ --jql "sprint='Current Sprint'"

# 2. Export for planning session
python main.py estimate-batch \
  --jql "sprint='Current Sprint'" \
  --export-format csv \
  --export-file sprint-estimates.csv
```

### Epic Management Workflow
```bash
# 1. Decompose epic
python main.py process-epic PROJ-100 --create-stories --dependency-analysis

# 2. Estimate all stories
python main.py estimate-batch --issues $(cat epic-stories.txt)

# 3. Generate epic report
python main.py generate-report epic --epic-key PROJ-100
```

## � Configuration Examples

### Basic Pipeline Configuration
```yaml
# pipeline.yaml
jira:
  url: "https://company.atlassian.net"
  default_project: "PROJ"

llama_stack:
  url: "http://localhost:8321"
  default_model: "llama3.2:3b"

pipeline:
  default_stages: ["epics", "jiras", "estimates"]
  batch_size: 5
  parallel_execution: true
```

### Stage-Specific Configuration
```yaml
# stages.yaml
estimates:
  confidence_threshold: 0.7
  estimation_method: "story_points"
  complexity_factors:
    - technical_complexity: 0.4
    - business_complexity: 0.3
    - risk_complexity: 0.3
```

## 🆘 Quick Help

### Getting Help
```bash
# Command help
python main.py --help
python main.py <command> --help

# System validation
python main.py validate all

# Configuration check
python main.py configure show
```

### Common Issues
- **Llama Stack Connection**: Check `python main.py validate llama-stack`
- **Jira Authentication**: Verify `python main.py validate jira`
- **Performance**: Reduce batch size or use lighter models
- **Memory**: Enable caching and monitor resource usage

### Resources
- 📖 **[FAQ](user-guide/faq.md)** - Common questions and solutions
- 🔧 **[Troubleshooting](user-guide/troubleshooting.md)** - Issue resolution guide
- 💬 **[Contributing](../CONTRIBUTING.md)** - How to contribute to the project

## 🎯 Use Cases

### Individual Contributors
- Refine user stories before development
- Get AI-powered estimation assistance
- Enhance issue descriptions and acceptance criteria

### Team Leads
- Batch process sprint backlogs
- Generate estimation reports for planning
- Analyze epic complexity and dependencies

### Product Managers
- Decompose epics into deliverable stories
- Get effort estimates for roadmap planning
- Track estimation accuracy over time

### Engineering Managers
- Monitor team estimation patterns
- Identify process improvement opportunities
- Generate executive summary reports

## 🚀 Next Steps

### New to RHOAI AI Feature Sizing?
1. **[📖 Getting Started](user-guide/getting-started.md)** - Complete setup guide
2. **[🎮 CLI Reference](user-guide/cli-reference.md)** - Learn the commands
3. **[❓ FAQ](user-guide/faq.md)** - Get answers to common questions

### Ready to Develop?
1. **[⚙️ Development Setup](development/setup.md)** - Set up your environment
2. **[🏗️ Architecture Overview](architecture/overview.md)** - Understand the system
3. **[📏 Coding Standards](development/standards.md)** - Follow our guidelines

### Planning a Deployment?
1. **[📦 Installation Guide](deployment/installation.md)** - Production deployment
2. **[⚙️ Configuration](deployment/configuration.md)** - Environment setup
3. **[🔐 Authentication](api/authentication.md)** - Security configuration

## 📈 Performance & Scaling

### Optimization Tips
- Use appropriate batch sizes for your system
- Leverage parallel processing for large datasets
- Configure caching for repeated operations
- Monitor resource usage and adjust accordingly

### Scaling Considerations
- Horizontal scaling with multiple Llama Stack instances
- Load balancing for high-volume processing
- Database optimization for historical data
- Monitoring and alerting for production systems

## 🔄 Updates & Maintenance

### Documentation Updates
This documentation is actively maintained and updated with:
- New feature releases
- Pipeline improvements
- Best practice guidance
- Community contributions

### Version Compatibility
- **Current Version**: 1.0.0
- **Llama Stack**: Compatible with latest stable releases
- **Python**: Requires 3.12+
- **Dependencies**: See `pyproject.toml` for current versions

---

## 📞 Support & Community

### Getting Support
- 📖 **Documentation**: Comprehensive guides and references
- ❓ **FAQ**: Common questions and solutions
- 🐛 **Issues**: Report bugs and request features
- 💬 **Contributing**: Join the development community

### Contributing
We welcome contributions! See our **[Contributing Guide](../CONTRIBUTING.md)** for:
- Development setup and workflow
- Coding standards and guidelines
- Testing requirements and practices
- Documentation contribution guidelines

---

*Thank you for using RHOAI AI Feature Sizing! This documentation reflects the latest pipeline architecture with full Jira refinement capabilities, Llama Stack agent integration, and comprehensive CLI interface.*