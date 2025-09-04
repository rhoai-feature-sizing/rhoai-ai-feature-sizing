"""
JIRA Feature Breakdown Workflow for LlamaDeploy

This workflow:
1. Takes a JIRA identifier and optional description
2. Fetches JIRA details using Atlassian MCP operations
3. Uses multi-agent analysis to break down features into epics and stories
4. Creates or updates JIRA epics and stories based on the breakdown
"""

import json
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)
from pydantic import BaseModel, Field

from src.settings import init_settings
from src.agents import RFEAgentManager, get_agent_personas


# Input Events
class JiraBreakdownEvent(Event):
    """Event for JIRA feature breakdown requests"""

    jira_id: str = Field(description="JIRA identifier (e.g., RHOAIENG-669)")
    description: Optional[str] = Field(
        default=None,
        description="Optional additional feature description"
    )
    user_id: Optional[str] = Field(default=None, description="User identifier")
    create_jira_items: bool = Field(
        default=False,
        description="Whether to create JIRA epics/stories or just analyze"
    )


# Progress Events
class JiraFetchProgressEvent(Event):
    """Event for JIRA fetching progress"""

    stage: str = Field(description="Current processing stage")
    progress: int = Field(description="Progress percentage")
    message: str = Field(description="Progress message")
    jira_id: str = Field(description="JIRA ID being processed")


class BreakdownProgressEvent(Event):
    """Event for feature breakdown progress"""

    stage: str = Field(description="Current breakdown stage")
    progress: int = Field(description="Progress percentage")
    message: str = Field(description="Progress message")
    completed_agents: int = Field(default=0, description="Number of agents completed")
    total_agents: int = Field(default=0, description="Total agents analyzing")


# Response Models
class JiraItem(BaseModel):
    """Represents a JIRA epic or story"""

    item_type: str = Field(description="'epic' or 'story'")
    title: str = Field(description="Title of the JIRA item")
    description: str = Field(description="Detailed description")
    acceptance_criteria: List[str] = Field(description="Acceptance criteria")
    story_points: Optional[int] = Field(default=None, description="Story points estimate")
    priority: str = Field(default="Medium", description="Priority level")
    components: List[str] = Field(default=[], description="Affected components")
    labels: List[str] = Field(default=[], description="JIRA labels")
    parent_epic: Optional[str] = Field(default=None, description="Parent epic for stories")


class JiraBreakdownResponse(BaseModel):
    """Response from JIRA feature breakdown"""

    original_jira_id: str = Field(description="Original JIRA identifier")
    original_summary: str = Field(description="Original JIRA summary")
    breakdown_summary: str = Field(description="AI-generated breakdown summary")
    epics: List[JiraItem] = Field(description="Generated epics")
    stories: List[JiraItem] = Field(description="Generated stories")
    agent_analyses: Dict[str, Any] = Field(description="Individual agent analyses")
    created_jira_items: Optional[List[str]] = Field(
        default=None,
        description="JIRA IDs of created items (if create_jira_items=True)"
    )
    processing_time: float = Field(description="Processing time in seconds")
    timestamp: str = Field(description="Processing timestamp")


# Workflow Implementation
class JiraBreakdownWorkflow(Workflow):
    """Workflow for breaking down JIRA features into epics and stories"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        init_settings()
        self.agent_manager = RFEAgentManager()

    @step
    async def start_jira_breakdown(
        self, ctx: Context, ev: StartEvent
    ) -> JiraBreakdownEvent:
        """Parse the input and start the JIRA breakdown process"""

        # Extract input data
        input_data = ev.get("input", {})
        if isinstance(input_data, str):
            input_data = json.loads(input_data)

        jira_id = input_data.get("jira_id", "")
        description = input_data.get("description")
        user_id = input_data.get("user_id")
        create_jira_items = input_data.get("create_jira_items", False)

        if not jira_id:
            raise ValueError("jira_id is required")

        return JiraBreakdownEvent(
            jira_id=jira_id,
            description=description,
            user_id=user_id,
            create_jira_items=create_jira_items
        )

    @step
    async def fetch_jira_details(
        self, ctx: Context, ev: JiraBreakdownEvent
    ) -> JiraFetchProgressEvent:
        """Fetch JIRA details using Atlassian MCP operations"""

        # Emit progress event
        await ctx.send_event(
            JiraFetchProgressEvent(
                stage="fetching_jira",
                progress=10,
                message=f"Fetching details for {ev.jira_id}",
                jira_id=ev.jira_id
            )
        )

        # TODO: Implement Atlassian MCP integration
        # This is a placeholder for the Atlassian MCP operation
        jira_details = await self._fetch_jira_via_mcp(ev.jira_id)

        # Store JIRA details in context
        await ctx.set("jira_details", jira_details)
        await ctx.set("original_event", ev)

        return JiraFetchProgressEvent(
            stage="jira_fetched",
            progress=25,
            message=f"Successfully fetched {ev.jira_id}",
            jira_id=ev.jira_id
        )

    @step
    async def analyze_with_agents(
        self, ctx: Context, ev: JiraFetchProgressEvent
    ) -> BreakdownProgressEvent:
        """Use multi-agent analysis to understand the feature"""

        jira_details = await ctx.get("jira_details")
        original_event = await ctx.get("original_event")

        # Prepare the feature description for agent analysis
        feature_description = self._prepare_feature_description(
            jira_details, original_event.description
        )

        # Get agent personas
        agent_personas = get_agent_personas()
        total_agents = len(agent_personas)

        # Emit initial progress
        await ctx.send_event(
            BreakdownProgressEvent(
                stage="agent_analysis",
                progress=30,
                message="Starting multi-agent analysis",
                completed_agents=0,
                total_agents=total_agents
            )
        )

        # Run agent analyses in parallel
        agent_analyses = {}
        completed = 0

        # TODO: Implement parallel agent analysis similar to rfe_builder_workflow.py
        for persona, config in agent_personas.items():
            try:
                analysis = await self.agent_manager.analyze_rfe(
                    persona, feature_description, config
                )
                agent_analyses[persona] = analysis
                completed += 1

                # Emit progress update
                progress = 30 + int((completed / total_agents) * 40)
                await ctx.send_event(
                    BreakdownProgressEvent(
                        stage="agent_analysis",
                        progress=progress,
                        message=f"Completed analysis: {persona}",
                        completed_agents=completed,
                        total_agents=total_agents
                    )
                )

            except Exception as e:
                print(f"Error analyzing with {persona}: {e}")
                # Continue with other agents
                continue

        # Store analyses in context
        await ctx.set("agent_analyses", agent_analyses)

        return BreakdownProgressEvent(
            stage="analysis_complete",
            progress=70,
            message="Multi-agent analysis completed",
            completed_agents=completed,
            total_agents=total_agents
        )

    @step
    async def synthesize_breakdown(
        self, ctx: Context, ev: BreakdownProgressEvent
    ) -> StopEvent:
        """Synthesize agent analyses into epics and stories breakdown"""

        start_time = await ctx.get("start_time", asyncio.get_event_loop().time())
        jira_details = await ctx.get("jira_details")
        agent_analyses = await ctx.get("agent_analyses")
        original_event = await ctx.get("original_event")

        # TODO: Implement synthesis logic to convert agent analyses into epics/stories
        epics, stories = await self._synthesize_epics_and_stories(
            jira_details, agent_analyses
        )

        # TODO: Optionally create JIRA items if requested
        created_jira_items = None
        if original_event.create_jira_items:
            created_jira_items = await self._create_jira_items(epics, stories)

        processing_time = asyncio.get_event_loop().time() - start_time

        response = JiraBreakdownResponse(
            original_jira_id=original_event.jira_id,
            original_summary=jira_details.get("summary", ""),
            breakdown_summary=self._generate_breakdown_summary(epics, stories),
            epics=epics,
            stories=stories,
            agent_analyses=agent_analyses,
            created_jira_items=created_jira_items,
            processing_time=processing_time,
            timestamp=datetime.now().isoformat()
        )

        return StopEvent(result=response)

    # Placeholder methods for MCP and JIRA integration

    async def _fetch_jira_via_mcp(self, jira_id: str) -> Dict[str, Any]:
        """
        Placeholder for Atlassian MCP integration

        TODO: Implement actual MCP call to fetch JIRA details
        This should use the Atlassian MCP operation to:
        - Fetch JIRA issue details
        - Get related issues/epics
        - Retrieve comments and attachments
        - Get project context
        """
        # Placeholder implementation
        return {
            "id": jira_id,
            "summary": f"Feature from {jira_id}",
            "description": "Placeholder JIRA description",
            "status": "Open",
            "project": "RHOAIENG",
            "issue_type": "Story",
            "priority": "Medium",
            "assignee": None,
            "reporter": "system",
            "labels": [],
            "components": []
        }

    def _prepare_feature_description(
        self, jira_details: Dict[str, Any], additional_description: Optional[str]
    ) -> str:
        """Prepare feature description for agent analysis"""

        description_parts = [
            f"JIRA ID: {jira_details['id']}",
            f"Summary: {jira_details['summary']}",
            f"Description: {jira_details.get('description', 'No description')}",
        ]

        if additional_description:
            description_parts.append(f"Additional Context: {additional_description}")

        return "\n\n".join(description_parts)

    async def _synthesize_epics_and_stories(
        self, jira_details: Dict[str, Any], agent_analyses: Dict[str, Any]
    ) -> tuple[List[JiraItem], List[JiraItem]]:
        """
        Synthesize agent analyses into epics and stories

        TODO: Implement LLM-based synthesis that:
        - Analyzes all agent perspectives
        - Identifies major feature areas (epics)
        - Breaks down implementation tasks (stories)
        - Assigns story points and priorities
        - Creates acceptance criteria
        """
        # Placeholder implementation
        epics = [
            JiraItem(
                item_type="epic",
                title="Core Feature Implementation",
                description="Main feature implementation based on agent analysis",
                acceptance_criteria=["Feature works as expected", "Passes all tests"],
                components=["backend", "frontend"],
                labels=["feature", "ai-generated"]
            )
        ]

        stories = [
            JiraItem(
                item_type="story",
                title="Backend API Development",
                description="Develop backend APIs for the feature",
                acceptance_criteria=["API endpoints created", "Tests pass"],
                story_points=5,
                components=["backend"],
                labels=["backend", "api"],
                parent_epic="Core Feature Implementation"
            ),
            JiraItem(
                item_type="story",
                title="Frontend UI Implementation",
                description="Create frontend user interface",
                acceptance_criteria=["UI components created", "UX requirements met"],
                story_points=3,
                components=["frontend"],
                labels=["frontend", "ui"],
                parent_epic="Core Feature Implementation"
            )
        ]

        return epics, stories

    async def _create_jira_items(
        self, epics: List[JiraItem], stories: List[JiraItem]
    ) -> List[str]:
        """
        Create JIRA epics and stories

        TODO: Implement MCP calls to create actual JIRA items
        """
        # Placeholder implementation
        created_items = []

        for epic in epics:
            # TODO: Use Atlassian MCP to create epic
            epic_id = f"RHOAIENG-{1000 + len(created_items)}"
            created_items.append(epic_id)

        for story in stories:
            # TODO: Use Atlassian MCP to create story
            story_id = f"RHOAIENG-{1000 + len(created_items)}"
            created_items.append(story_id)

        return created_items

    def _generate_breakdown_summary(
        self, epics: List[JiraItem], stories: List[JiraItem]
    ) -> str:
        """Generate a summary of the breakdown"""

        total_story_points = sum(
            story.story_points for story in stories if story.story_points
        )

        return f"""
Feature breakdown completed:
- {len(epics)} epic(s) identified
- {len(stories)} story/stories created
- Total estimated story points: {total_story_points}
- Components involved: {list(set(comp for item in epics + stories for comp in item.components))}
""".strip()


# Export the workflow
jira_breakdown_workflow = JiraBreakdownWorkflow()
