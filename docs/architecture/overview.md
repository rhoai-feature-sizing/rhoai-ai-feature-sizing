# Architecture Overview

## System Architecture

RHOAI AI Feature Sizing is a Python-based tool designed to leverage AI for intelligent feature sizing and estimation, with integrated JIRA workflow support.

## High-Level Components

### 🎯 Core Stages
The system is organized into distinct processing stages:

- **Draft JIRAs** (`stages/draft_jiras.py`) - Initial JIRA ticket creation and management
- **Feature Refinement** (`stages/refine_feature.py`) - AI-powered feature analysis and refinement
- **Estimation** (`stages/estimate.py`) - Intelligent sizing and effort estimation

### 🔧 Tools Layer
- **MCP JIRA** (`tools/mcp_jira.py`) - JIRA integration and communication layer
- Extensible tool framework for additional integrations

### 🤖 AI Integration
- **Prompt Management** (`prompts/`) - Structured AI prompt templates
- **LLaMA Stack Client** - AI model integration for feature analysis
- Context-aware feature refinement and sizing

### 🏗️ Project Structure
```
rhoai-ai-feature-sizing/
├── main.py              # Entry point
├── stages/              # Processing stages
├── tools/               # Integration tools
├── prompts/             # AI prompt templates
└── docs/                # Documentation
```

## Design Principles

1. **Modular Architecture** - Separation of concerns with distinct stages
2. **AI-First Approach** - Leverages AI for intelligent feature analysis
3. **JIRA Integration** - Seamless workflow integration with existing tools
4. **Extensibility** - Plugin-based architecture for new tools and stages

## Technology Stack

- **Language**: Python 3.12+
- **AI Framework**: LLaMA Stack Client
- **CLI Framework**: Fire
- **Integration**: JIRA API, MCP protocols
- **Package Management**: UV

## Data Flow

1. **Input**: Feature specifications or JIRA tickets
2. **Processing**: AI-powered analysis through defined stages
3. **Refinement**: Iterative improvement with human feedback
4. **Output**: Sized features with effort estimates
5. **Integration**: Updated JIRA tickets with sizing information

---

*For detailed architectural decisions, see [Decisions](./decisions.md)*