# Architectural Decision Records (ADRs)

This document tracks major architectural decisions made in the RHOAI AI Feature Sizing project.

## ADR-001: Python as Primary Language

**Date**: 2024-01-01  
**Status**: Accepted

### Context
Need to choose a primary programming language for the feature sizing tool.

### Decision
Python 3.12+ was chosen as the primary language.

### Rationale
- Excellent AI/ML ecosystem with libraries like LLaMA Stack
- Strong JIRA API integration capabilities
- Fire framework provides simple CLI generation
- UV package manager offers fast dependency management
- Team expertise and rapid development capabilities

### Consequences
- **Positive**: Fast development, rich AI ecosystem, good tooling
- **Negative**: Runtime performance considerations for large-scale processing

---

## ADR-002: Stage-Based Processing Architecture

**Date**: 2024-01-01  
**Status**: Accepted

### Context
Need to organize the feature sizing workflow into manageable components.

### Decision
Implement a stage-based processing architecture with distinct phases:
- Draft JIRAs
- Feature Refinement  
- Estimation

### Rationale
- Clear separation of concerns
- Enables independent development and testing
- Supports iterative workflows
- Allows for easy extension with new stages

### Consequences
- **Positive**: Modular, testable, extensible
- **Negative**: Potential overhead for simple workflows

---

## ADR-003: LLaMA Stack for AI Integration

**Date**: 2024-01-01  
**Status**: Accepted

### Context
Need to integrate AI capabilities for feature analysis and sizing.

### Decision
Use LLaMA Stack Client for AI model integration.

### Rationale
- Standardized interface for LLM interactions
- Support for multiple model backends
- Active development and community support
- Good integration with Python ecosystem

### Consequences
- **Positive**: Flexible model support, standardized API
- **Negative**: Dependency on external service/models

---

## ADR-004: MCP Protocol for JIRA Integration

**Date**: 2024-01-01  
**Status**: Accepted

### Context
Need reliable JIRA integration for workflow automation.

### Decision
Implement JIRA integration using MCP (Model Context Protocol) patterns.

### Rationale
- Structured communication protocols
- Better error handling and retry logic
- Separation of integration concerns
- Extensible for other tool integrations

### Consequences
- **Positive**: Robust integration, reusable patterns
- **Negative**: Additional abstraction layer complexity

---

## ADR-005: Fire Framework for CLI

**Date**: 2024-01-01  
**Status**: Accepted

### Context
Need a command-line interface for the tool.

### Decision
Use Python Fire framework for CLI generation.

### Rationale
- Automatic CLI generation from Python functions
- Minimal boilerplate code
- Good debugging and introspection capabilities
- Familiar Python-based configuration

### Consequences
- **Positive**: Rapid CLI development, Python-native
- **Negative**: Less control over CLI design compared to Click/ArgParse

---

## Template for New ADRs

```markdown
## ADR-XXX: [Title]

**Date**: YYYY-MM-DD  
**Status**: [Proposed | Accepted | Deprecated | Superseded]

### Context
[Description of the forces at play, including technological, political, social, and project local]

### Decision
[Description of the chosen option]

### Rationale
[Why this decision was made]

### Consequences
- **Positive**: [Benefits of this decision]
- **Negative**: [Drawbacks or risks]