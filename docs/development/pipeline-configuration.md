# Pipeline Configuration Guide

This guide covers advanced configuration options for the RHOAI AI Feature Sizing pipeline, including stage-specific settings, Llama Stack agent configuration, and custom workflow creation.

## 📋 Overview

The pipeline configuration system provides multiple levels of customization:

- **Global Configuration** - System-wide settings for Jira, Llama Stack, and logging
- **Stage Configuration** - Specific settings for each pipeline stage
- **Agent Configuration** - Llama Stack agent behavior and parameters
- **Workflow Configuration** - Custom pipeline flows and stage combinations

## 🔧 Configuration File Structure

### Main Configuration File (`pipeline.yaml`)

```yaml
# Global system configuration
system:
  name: "RHOAI Feature Sizing Pipeline"
  version: "1.0.0"
  environment: "production"  # development, staging, production

# Jira integration settings
jira:
  url: "https://company.atlassian.net"
  username: "automation@company.com"
  timeout: 30
  max_retries: 3
  batch_size: 10
  rate_limit: 10  # requests per second
  default_project: "PROJ"
  fields:
    epic_link: "customfield_10014"
    story_points: "customfield_10016"
    components: "components"

# Llama Stack configuration
llama_stack:
  url: "http://localhost:8321"
  timeout: 60
  max_retries: 3
  default_model: "llama3.2:3b"
  temperature: 0.7
  max_tokens: 4096
  agent_config:
    session_timeout: 300
    max_concurrent_sessions: 5
    memory_limit: "2GB"

# Pipeline execution settings
pipeline:
  default_stages: ["epics", "jiras", "estimates", "output"]
  parallel_execution: true
  max_workers: 4
  batch_size: 5
  resume_on_failure: true
  checkpoint_interval: 10
  output_format: "json"
  output_compression: true

# Logging configuration
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  format: "structured"  # text, json, structured
  file: "logs/pipeline.log"
  max_size: "100MB"
  backup_count: 5
  console_output: true
  
# Performance tuning
performance:
  cache_enabled: true
  cache_ttl: 3600  # seconds
  memory_limit: "4GB"
  cpu_cores: 4
  gpu_enabled: false
```

### Stage Configuration File (`stages.yaml`)

```yaml
# Epic processing stage configuration
epics:
  enabled: true
  ai_model: "llama3.2:3b"
  temperature: 0.6
  max_tokens: 3000
  
  processing:
    max_stories_per_epic: 15
    min_stories_per_epic: 3
    story_estimation_threshold: 8  # auto-break stories larger than this
    dependency_analysis: true
    risk_assessment: true
    
  templates:
    story_template: "templates/story_template.json"
    epic_analysis_template: "prompts/epic_analysis.md"
    dependency_template: "prompts/dependency_analysis.md"
    
  validation:
    min_description_length: 50
    required_fields: ["summary", "description", "acceptance_criteria"]
    quality_checks: ["completeness", "clarity", "feasibility"]
    
  output:
    create_jira_stories: false  # set to true to auto-create in Jira
    export_formats: ["json", "csv"]
    include_dependency_graph: true

# Jira issue refinement stage
jiras:
  enabled: true
  ai_model: "llama3.2:3b"
  temperature: 0.5
  max_tokens: 2500
  
  processing:
    enhancement_level: "detailed"  # basic, detailed, comprehensive
    include_technical_requirements: true
    include_testing_criteria: true
    include_security_considerations: true
    analyze_dependencies: true
    
  filters:
    issue_types: ["Story", "Task", "Bug"]
    statuses: ["To Do", "In Progress", "In Review"]
    exclude_subtasks: false
    min_description_length: 10
    
  enhancement:
    acceptance_criteria_required: true
    technical_requirements_required: true
    definition_of_done_required: true
    examples_encouraged: true
    
  validation:
    rules:
      - name: "completeness"
        weight: 0.4
        checks: ["summary", "description", "acceptance_criteria"]
      - name: "clarity"
        weight: 0.3
        checks: ["language_clarity", "requirement_specificity"]
      - name: "technical_feasibility"
        weight: 0.3
        checks: ["technical_complexity", "dependency_availability"]
        
  templates:
    refinement_template: "prompts/issue_refinement.md"
    technical_template: "prompts/technical_requirements.md"
    testing_template: "prompts/testing_criteria.md"

# Estimation engine stage
estimates:
  enabled: true
  ai_model: "llama3.1:8b"  # Use larger model for estimation
  temperature: 0.3  # Lower temperature for consistency
  max_tokens: 2000
  
  methods:
    primary: "story_points"  # story_points, hours, t_shirt
    secondary: "hours"  # optional secondary estimation
    fibonacci_sequence: [1, 2, 3, 5, 8, 13, 21]
    max_story_points: 21
    
  analysis:
    complexity_factors:
      - name: "technical_complexity"
        weight: 0.4
        criteria: ["algorithms", "integration", "performance"]
      - name: "business_complexity"
        weight: 0.3
        criteria: ["requirements", "stakeholders", "compliance"]
      - name: "risk_complexity"
        weight: 0.3
        criteria: ["unknowns", "dependencies", "external_factors"]
        
    confidence_calculation:
      min_confidence: 0.5
      high_confidence_threshold: 0.8
      factors: ["requirement_clarity", "technical_certainty", "team_experience"]
      
  calibration:
    use_historical_data: true
    historical_data_file: "data/estimation_history.json"
    learning_rate: 0.1
    min_samples: 10
    
  templates:
    estimation_template: "prompts/estimation_analysis.md"
    complexity_template: "prompts/complexity_factors.md"
    risk_template: "prompts/risk_assessment.md"

# Output generation stage
output:
  enabled: true
  ai_model: "llama3.2:3b"
  temperature: 0.4
  
  formats:
    json:
      enabled: true
      pretty_print: true
      include_metadata: true
    csv:
      enabled: true
      include_headers: true
      delimiter: ","
    excel:
      enabled: false
      include_charts: true
    jira_import:
      enabled: false
      validate_format: true
      
  reports:
    executive_summary: true
    detailed_analysis: true
    estimation_breakdown: true
    risk_assessment: true
    recommendations: true
    
  templates:
    report_template: "templates/pipeline_report.md"
    summary_template: "templates/executive_summary.md"
    jira_template: "templates/jira_import.json"
```

### Agent Configuration File (`agents.yaml`)

```yaml
# Jira Retrieval Agent
jira_retrieval_agent:
  name: "JiraRetrieverAgent"
  model: "llama3.2:3b"
  temperature: 0.3
  max_tokens: 1500
  
  capabilities:
    - "jira_api_interaction"
    - "issue_filtering"
    - "batch_processing"
    - "error_handling"
    
  configuration:
    batch_size: 20
    retry_attempts: 3
    rate_limiting: true
    cache_results: true
    
  prompts:
    system_prompt: "prompts/agents/jira_retrieval_system.md"
    query_prompt: "prompts/agents/jira_query.md"
    filter_prompt: "prompts/agents/jira_filter.md"

# Content Analysis Agent  
content_analysis_agent:
  name: "ContentAnalysisAgent"
  model: "llama3.2:3b"
  temperature: 0.5
  max_tokens: 3000
  
  capabilities:
    - "natural_language_understanding"
    - "content_enhancement"
    - "gap_analysis"
    - "requirement_extraction"
    
  configuration:
    analysis_depth: "comprehensive"  # basic, standard, comprehensive
    include_sentiment: false
    include_complexity_hints: true
    
  prompts:
    system_prompt: "prompts/agents/content_analysis_system.md"
    enhancement_prompt: "prompts/agents/content_enhancement.md"
    gap_analysis_prompt: "prompts/agents/gap_analysis.md"

# Estimation Agent
estimation_agent:
  name: "EstimationAgent"
  model: "llama3.1:8b"
  temperature: 0.2
  max_tokens: 2000
  
  capabilities:
    - "complexity_assessment"
    - "story_point_calculation"
    - "confidence_analysis"
    - "risk_identification"
    
  configuration:
    estimation_method: "multi_factor"
    confidence_weighting: true
    historical_learning: true
    
  prompts:
    system_prompt: "prompts/agents/estimation_system.md"
    complexity_prompt: "prompts/agents/complexity_analysis.md"
    estimation_prompt: "prompts/agents/story_point_estimation.md"

# Documentation Agent
documentation_agent:
  name: "DocumentationAgent"
  model: "llama3.2:3b"
  temperature: 0.4
  max_tokens: 2500
  
  capabilities:
    - "template_application"
    - "content_generation"
    - "cross_referencing"
    - "format_conversion"
    
  configuration:
    output_style: "professional"
    include_metadata: true
    cross_reference_links: true
    
  prompts:
    system_prompt: "prompts/agents/documentation_system.md"
    template_prompt: "prompts/agents/template_application.md"
    generation_prompt: "prompts/agents/content_generation.md"
```

## 🎯 Workflow Configuration

### Custom Workflow Definition (`workflows.yaml`)

```yaml
# Define custom pipeline workflows
workflows:
  
  # Quick estimation workflow
  quick_estimate:
    name: "Quick Estimation"
    description: "Fast estimation for well-defined issues"
    stages: ["jiras", "estimates"]
    config:
      jiras:
        enhancement_level: "basic"
        temperature: 0.4
      estimates:
        analysis_depth: "standard"
        confidence_threshold: 0.6
        
  # Comprehensive analysis workflow  
  full_analysis:
    name: "Full Analysis"
    description: "Complete analysis including epic decomposition"
    stages: ["epics", "jiras", "estimates", "output"]
    config:
      epics:
        dependency_analysis: true
        risk_assessment: true
      jiras:
        enhancement_level: "comprehensive"
        include_security_considerations: true
      estimates:
        use_historical_data: true
        confidence_threshold: 0.8
        
  # Security-focused workflow
  security_review:
    name: "Security Review"
    description: "Security-focused issue analysis"
    stages: ["jiras", "estimates"]
    config:
      jiras:
        templates:
          refinement_template: "prompts/security_refinement.md"
        include_security_considerations: true
        include_compliance_checks: true
      estimates:
        complexity_factors:
          security_complexity:
            weight: 0.5
            criteria: ["threat_modeling", "compliance", "audit_requirements"]
            
  # Sprint planning workflow
  sprint_planning:
    name: "Sprint Planning"
    description: "Optimized for sprint planning activities"
    stages: ["jiras", "estimates", "output"]
    config:
      jiras:
        filters:
          statuses: ["To Do", "Selected for Development"]
        enhancement_level: "detailed"
      estimates:
        methods:
          primary: "story_points"
          max_story_points: 13
        confidence_threshold: 0.7
      output:
        reports:
          sprint_capacity: true
          velocity_prediction: true
```

## 🔗 Environment-Specific Configuration

### Development Environment (`config/development.yaml`)

```yaml
system:
  environment: "development"
  debug_mode: true

llama_stack:
  url: "http://localhost:8321"
  model: "llama3.2:1b"  # Lighter model for dev
  timeout: 30

pipeline:
  batch_size: 2
  parallel_execution: false
  max_workers: 1

logging:
  level: "DEBUG"
  console_output: true
  file: "logs/dev-pipeline.log"

performance:
  cache_enabled: false  # Disable cache for testing
  memory_limit: "1GB"
```

### Production Environment (`config/production.yaml`)

```yaml
system:
  environment: "production"
  debug_mode: false

llama_stack:
  url: "http://llama-stack-prod:8321"
  model: "llama3.1:8b"
  timeout: 120
  
pipeline:
  batch_size: 10
  parallel_execution: true
  max_workers: 8
  resume_on_failure: true

logging:
  level: "INFO"
  console_output: false
  file: "/var/log/rhoai/pipeline.log"

performance:
  cache_enabled: true
  memory_limit: "8GB"
  cpu_cores: 8
```

## 🎮 Using Configuration Files

### Basic Usage

```bash
# Use specific configuration file
python main.py run-pipeline --config config/production.yaml --project PROJ

# Use configuration with overrides
python main.py run-pipeline \
  --config pipeline.yaml \
  --stages-config stages.yaml \
  --agents-config agents.yaml \
  --project PROJ

# Use workflow configuration
python main.py run-workflow quick_estimate \
  --workflow-config workflows.yaml \
  --project PROJ
```

### Environment-Specific Configuration

```bash
# Development environment
python main.py run-pipeline \
  --config config/development.yaml \
  --project PROJ

# Production environment
python main.py run-pipeline \
  --config config/production.yaml \
  --project PROJ

# Staging with custom overrides
python main.py run-pipeline \
  --config config/staging.yaml \
  --override llama_stack.model=llama3.1:8b \
  --override pipeline.batch_size=5 \
  --project PROJ
```

### Configuration Validation

```bash
# Validate configuration files
python main.py validate config --config pipeline.yaml

# Validate all configuration files
python main.py validate config \
  --config pipeline.yaml \
  --stages-config stages.yaml \
  --agents-config agents.yaml

# Test configuration against live systems
python main.py validate all --config config/production.yaml
```

## 🔧 Advanced Configuration Options

### Model-Specific Configuration

```yaml
# Different models for different stages
stage_models:
  epics:
    model: "llama3.1:8b"
    temperature: 0.6
    reasoning: "Larger model for complex epic analysis"
    
  jiras:
    model: "llama3.2:3b"
    temperature: 0.5
    reasoning: "Balanced model for content enhancement"
    
  estimates:
    model: "llama3.1:70b"  # Large model for estimation
    temperature: 0.2
    reasoning: "Most accurate model for estimation"
    
  output:
    model: "llama3.2:3b"
    temperature: 0.4
    reasoning: "Good model for document generation"
```

### Dynamic Configuration

```yaml
# Configuration that adapts based on conditions
dynamic_config:
  rules:
    - condition: "issue_count > 100"
      action: 
        pipeline.batch_size: 20
        pipeline.max_workers: 8
        
    - condition: "avg_complexity > 0.8"
      action:
        estimates.ai_model: "llama3.1:8b"
        estimates.temperature: 0.1
        
    - condition: "time_constraint == 'urgent'"
      action:
        jiras.enhancement_level: "basic"
        estimates.confidence_threshold: 0.6
```

### Integration Configuration

```yaml
# External system integrations
integrations:
  slack:
    enabled: true
    webhook_url: "${SLACK_WEBHOOK_URL}"
    channels:
      progress: "#feature-sizing"
      errors: "#alerts"
      
  confluence:
    enabled: false
    base_url: "https://company.atlassian.net/wiki"
    space_key: "ENG"
    
  github:
    enabled: false
    token: "${GITHUB_TOKEN}"
    repository: "company/feature-specs"
    
  metrics:
    prometheus:
      enabled: true
      port: 9090
      metrics_prefix: "rhoai_pipeline"
```

## 📊 Configuration Management

### Configuration Hierarchy

The system uses the following configuration precedence (highest to lowest):

1. **Command-line overrides** - `--override key=value`
2. **Environment variables** - `RHOAI_CONFIG_KEY=value`
3. **Workflow-specific config** - Values in workflow definition
4. **Stage-specific config** - Values in stages.yaml
5. **Main config file** - Values in pipeline.yaml
6. **Default values** - Built-in defaults

### Environment Variable Support

```bash
# Override any configuration value using environment variables
export RHOAI_JIRA_URL="https://company.atlassian.net"
export RHOAI_LLAMA_STACK_MODEL="llama3.1:8b"
export RHOAI_PIPELINE_BATCH_SIZE="15"

# Run with environment overrides
python main.py run-pipeline --project PROJ
```

### Configuration Templates

Create reusable configuration templates:

```bash
# Generate configuration template
python main.py generate-config-template \
  --type production \
  --output config/production-template.yaml

# Generate stage-specific template
python main.py generate-config-template \
  --type stages \
  --focus estimation \
  --output config/estimation-stages-template.yaml
```

## 🛠️ Custom Stage Development

### Creating Custom Stages

```yaml
# Custom stage configuration
custom_stages:
  quality_assurance:
    name: "Quality Assurance Analysis"
    class: "stages.QualityAssuranceStage"
    dependencies: ["jiras"]
    config:
      ai_model: "llama3.2:3b"
      temperature: 0.4
      checks:
        - "testability"
        - "maintainability" 
        - "performance_impact"
        
  compliance_check:
    name: "Compliance Validation"
    class: "stages.ComplianceStage"
    dependencies: ["jiras", "estimates"]
    config:
      frameworks: ["SOC2", "GDPR", "HIPAA"]
      severity_threshold: "medium"
```

### Stage Registration

```python
# Register custom stages in Python
from pipeline.stage_registry import register_stage
from stages.custom import QualityAssuranceStage

register_stage("quality_assurance", QualityAssuranceStage)
```

## 📝 Configuration Examples

### Team-Specific Configuration

```yaml
# Mobile team configuration
mobile_team:
  jira:
    default_project: "MOB"
    filters:
      components: ["iOS", "Android", "React Native"]
      
  stages:
    jiras:
      templates:
        refinement_template: "prompts/mobile_refinement.md"
      enhancement:
        include_platform_considerations: true
        include_performance_requirements: true
        
    estimates:
      complexity_factors:
        platform_complexity:
          weight: 0.3
          criteria: ["cross_platform", "native_features", "app_store"]
```

### Project-Specific Configuration

```yaml
# E-commerce project configuration  
ecommerce_project:
  pipeline:
    default_stages: ["epics", "jiras", "estimates", "security_review", "output"]
    
  custom_fields:
    payment_complexity: "customfield_10050"
    compliance_level: "customfield_10051"
    
  validation:
    required_labels: ["payment", "security", "pci-compliance"]
    
  templates:
    epic_template: "templates/ecommerce_epic.json"
    story_template: "templates/ecommerce_story.json"
```

## 🔍 Configuration Debugging

### Debug Configuration Loading

```bash
# Show loaded configuration
python main.py debug config --config pipeline.yaml

# Show configuration resolution
python main.py debug config-resolution \
  --config pipeline.yaml \
  --stages-config stages.yaml \
  --override pipeline.batch_size=10

# Validate configuration schema
python main.py validate config-schema --config pipeline.yaml
```

### Configuration Testing

```bash
# Test configuration with dry run
python main.py run-pipeline \
  --config config/test.yaml \
  --project PROJ \
  --dry-run

# Test specific stage configuration
python main.py test-stage estimates \
  --stages-config stages.yaml \
  --sample-issue PROJ-123
```

## 📚 Related Resources

- [CLI Reference](../user-guide/cli-reference.md) - Command-line usage
- [Architecture Overview](../architecture/overview.md) - System design
- [Development Setup](setup.md) - Development environment
- [API Documentation](../api/endpoints.md) - Programmatic access

---

*This configuration guide provides comprehensive control over the RHOAI AI Feature Sizing pipeline. Start with basic configuration and gradually add advanced features as needed.*