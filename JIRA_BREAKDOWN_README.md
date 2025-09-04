# JIRA Feature Breakdown Workflow

This document describes the new JIRA breakdown endpoint that processes JIRA tickets and breaks them down into epics and stories using AI agent analysis.

## Overview

The JIRA breakdown workflow:
1. **Accepts** a JIRA identifier (e.g., `RHOAIENG-669`) and optional description
2. **Fetches** JIRA details using Atlassian MCP operations
3. **Analyzes** the feature using all available AI agents (15+ personas)
4. **Synthesizes** the analysis into structured epics and stories
5. **Optionally** creates new JIRA items based on the breakdown

## API Endpoint

### Quick Start

1. **Start LlamaDeploy services:**
```bash
# Terminal 1: Start API server
uv run -m llama_deploy.apiserver

# Terminal 2: Deploy workflows  
uv run llamactl deploy deployment.yml
```

2. **Test the endpoint:**
```bash
curl -X POST http://localhost:4501/deployments/rhoai-ai-feature-sizing/tasks/create \
  -H "Content-Type: application/json" \
  -d '{
    "input": "{\"jira_id\":\"RHOAIENG-669\",\"description\":\"Test feature breakdown\"}",
    "service_id": "jira-breakdown-workflow"
  }'
```

3. **Monitor progress:**
```bash
# Use task_id from response above
curl "http://localhost:4501/deployments/rhoai-ai-feature-sizing/tasks/{task_id}/events?raw_event=true"
```

### Request Format

**POST** `http://localhost:4501/deployments/rhoai-ai-feature-sizing/tasks/create`

**Headers:** `Content-Type: application/json`

**Request Body:**
```json
{
  "input": "{\"jira_id\":\"RHOAIENG-669\",\"description\":\"Optional additional context\",\"user_id\":\"user123\",\"create_jira_items\":false}",
  "service_id": "jira-breakdown-workflow"
}
```

### Immediate Response

The API returns a task ID immediately (workflow runs asynchronously):

```json
{
  "task_id": "abc123-def456-789",
  "session_id": "session789"
}
```

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `jira_id` | string | ✅ | JIRA identifier (e.g., "RHOAIENG-669") |
| `description` | string | ❌ | Additional feature description or context |
| `user_id` | string | ❌ | User identifier for tracking |
| `create_jira_items` | boolean | ❌ | Whether to create actual JIRA epics/stories (default: false) |

### Streaming Events

Monitor real-time progress via the events endpoint:

**GET** `http://localhost:4501/deployments/rhoai-ai-feature-sizing/tasks/{task_id}/events?raw_event=true`

**Progress Events:**
```json
{
  "type": "progress",
  "data": {
    "stage": "agent_analysis", 
    "progress": 65,
    "message": "Completed analysis: UX_RESEARCHER",
    "completed_agents": 5,
    "total_agents": 15
  }
}
```

### Final Response Format

The workflow returns a `JiraBreakdownResponse` containing:

```json
{
  "original_jira_id": "RHOAIENG-669",
  "original_summary": "Improve ML model deployment experience",
  "breakdown_summary": "Feature breakdown completed: 2 epic(s), 5 stories, 18 story points",
  "epics": [
    {
      "item_type": "epic",
      "title": "Core Deployment Infrastructure",
      "description": "Build core infrastructure for improved model deployment",
      "acceptance_criteria": ["Infrastructure is scalable", "Deployment time < 5 minutes"],
      "components": ["backend", "infrastructure"],
      "labels": ["deployment", "infrastructure"]
    }
  ],
  "stories": [
    {
      "item_type": "story", 
      "title": "API Endpoint for Model Registration",
      "description": "Create REST API for model registration workflow",
      "acceptance_criteria": ["API accepts model metadata", "Validation implemented"],
      "story_points": 5,
      "priority": "High",
      "components": ["backend", "api"],
      "labels": ["backend", "api"],
      "parent_epic": "Core Deployment Infrastructure"
    }
  ],
  "agent_analyses": {
    "ENGINEERING_MANAGER": { "analysis": "...", "concerns": [...] },
    "UX_RESEARCHER": { "analysis": "...", "researchPlan": {...} }
  },
  "created_jira_items": null,
  "processing_time": 45.2,
  "timestamp": "2024-09-04T14:30:00Z"
}
```

## Usage Examples

### 1. Using the Test Script (Recommended)

```bash
# Start LlamaDeploy services
uv run -m llama_deploy.apiserver
uv run llamactl deploy deployment.yml

# Run comprehensive test with progress monitoring
python test_jira_breakdown.py
```

### 2. Basic Analysis (No JIRA Creation)

```bash
# Step 1: Create task
RESPONSE=$(curl -s -X POST http://localhost:4501/deployments/rhoai-ai-feature-sizing/tasks/create \
  -H "Content-Type: application/json" \
  -d '{
    "input": "{\"jira_id\":\"RHOAIENG-669\",\"description\":\"Improve user onboarding flow\"}",
    "service_id": "jira-breakdown-workflow"
  }')

# Step 2: Extract task ID
TASK_ID=$(echo $RESPONSE | grep -o '"task_id":"[^"]*' | cut -d'"' -f4)
echo "Task ID: $TASK_ID"

# Step 3: Monitor progress
curl "http://localhost:4501/deployments/rhoai-ai-feature-sizing/tasks/$TASK_ID/events?raw_event=true"
```

### 3. Full Breakdown with JIRA Creation

```bash
curl -X POST http://localhost:4501/deployments/rhoai-ai-feature-sizing/tasks/create \
  -H "Content-Type: application/json" \
  -d '{
    "input": "{\"jira_id\":\"RHOAIENG-669\",\"create_jira_items\":true}",
    "service_id": "jira-breakdown-workflow"
  }'
```

### 4. Postman/Insomnia Setup

**Method:** POST
**URL:** `http://localhost:4501/deployments/rhoai-ai-feature-sizing/tasks/create`
**Headers:**
- `Content-Type: application/json`

**Body (raw JSON):**
```json
{
  "input": "{\"jira_id\":\"RHOAIENG-669\",\"description\":\"Feature improvement for ML model deployment\",\"user_id\":\"developer123\"}",
  "service_id": "jira-breakdown-workflow"
}
```

## Implementation Status

### ✅ Completed
- [x] Workflow structure and event definitions
- [x] Multi-agent integration (uses existing 15+ agent personas)
- [x] Progress tracking and event streaming
- [x] Response data models and validation
- [x] LlamaDeploy service configuration
- [x] Test script and documentation

### 🚧 TODO: Atlassian MCP Integration

The following methods need to be implemented with actual Atlassian MCP operations:

#### 1. `_fetch_jira_via_mcp()`
```python
async def _fetch_jira_via_mcp(self, jira_id: str) -> Dict[str, Any]:
    """
    TODO: Replace placeholder with actual MCP integration
    
    Should use Atlassian MCP to:
    - Fetch JIRA issue details (summary, description, status)
    - Get related issues and epics
    - Retrieve comments and attachments
    - Get project context and metadata
    """
```

#### 2. `_create_jira_items()`
```python
async def _create_jira_items(self, epics: List[JiraItem], stories: List[JiraItem]) -> List[str]:
    """
    TODO: Replace placeholder with actual MCP integration
    
    Should use Atlassian MCP to:
    - Create epics in the same project as original JIRA
    - Create stories linked to appropriate epics
    - Set proper issue types, priorities, and components
    - Return actual JIRA IDs of created items
    """
```

### 🔧 TODO: Enhanced Synthesis

#### 3. `_synthesize_epics_and_stories()`
```python
async def _synthesize_epics_and_stories(self, jira_details, agent_analyses) -> tuple[List[JiraItem], List[JiraItem]]:
    """
    TODO: Implement LLM-based synthesis
    
    Should:
    - Analyze all agent perspectives and recommendations
    - Identify major feature areas (epics) 
    - Break down implementation tasks (stories)
    - Assign realistic story points based on complexity
    - Create detailed acceptance criteria
    - Determine appropriate priorities and components
    """
```

## Agent Integration

The workflow leverages all available agent personas:

### Core Analysis Agents
- **Engineering Manager** - Capacity planning, timeline estimation
- **Staff Engineer** - Technical implementation approach  
- **UX Researcher** - User research needs and validation
- **UX Architect** - Strategic UX and journey planning
- **Product Manager** - Business value and market impact
- **Backend Engineer** - System architecture and APIs
- **Frontend Engineer** - UI implementation and components

### Process & Coordination Agents  
- **Scrum Master** - Sprint planning and impediment identification
- **Delivery Owner** - Cross-team dependencies and milestones
- **Team Lead** - Technical coordination and resource planning
- **PXE** - Customer impact and upgrade considerations

### Specialized Agents
- **Technical Writer** - Documentation requirements
- **UX Feature Lead** - Component design and accessibility
- **Content Strategist** - Information architecture needs

## Next Steps

1. **Implement Atlassian MCP Integration**
   - Set up MCP connection to Atlassian/JIRA
   - Implement `_fetch_jira_via_mcp()` method
   - Implement `_create_jira_items()` method

2. **Enhance Synthesis Logic** 
   - Create LLM-based synthesis prompt
   - Implement smart epic/story breakdown logic
   - Add story point estimation algorithm

3. **Add Configuration Options**
   - Configurable agent selection
   - Custom epic/story templates
   - Project-specific settings

4. **Testing & Validation**
   - Test with real JIRA instances
   - Validate agent analysis quality
   - Verify created JIRA items structure

## API Status Codes

| Status | Meaning | Response |
|--------|---------|----------|
| 200 | Success | Task created successfully |
| 400 | Bad Request | Invalid input format or missing jira_id |
| 500 | Server Error | LlamaDeploy or workflow error |

## Error Handling

The workflow includes comprehensive error handling:
- **Invalid JIRA IDs:** Caught early with clear error messages
- **Agent failures:** Individual agent failures don't stop the entire process
- **MCP connection issues:** Logged and reported, workflow continues with placeholder data
- **Partial results:** Returned even if some steps fail
- **Timeout handling:** Long-running operations have appropriate timeouts

### Common Error Responses

**Missing JIRA ID:**
```json
{
  "error": "jira_id is required",
  "status": "failed"
}
```

**Invalid input format:**
```json
{
  "error": "Invalid JSON in input field",
  "status": "failed"  
}
```

## Performance Considerations

- Agent analyses run in parallel for faster processing
- Progress events provide real-time feedback
- Large JIRA descriptions are truncated appropriately
- Timeout handling for long-running MCP operations