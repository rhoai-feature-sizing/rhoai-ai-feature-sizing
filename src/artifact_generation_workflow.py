"""
Artifact Generation Workflow

Takes a completed RFE document and generates all supporting artifacts:
- Feature Refinement Document
- Architecture Document
- Epics and Stories Document
"""

import time
from typing import Any, Dict, List
from enum import Enum

from llama_index.core import Settings
from llama_index.core.llms import LLM
from llama_index.core.prompts import PromptTemplate
from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)
from llama_index.core.chat_ui.events import UIEvent
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from src.settings import init_settings


def create_artifact_generation_workflow() -> Workflow:
    load_dotenv()
    init_settings()
    return ArtifactGenerationWorkflow(timeout=120.0)


class ArtifactType(str, Enum):
    FEATURE_REFINEMENT = "feature_refinement"
    ARCHITECTURE = "architecture"
    EPICS_STORIES = "epics_stories"


class GenerationUIEventData(BaseModel):
    """UI event data for artifact generation"""

    stage: str = Field(description="Current generation stage")
    artifact_type: ArtifactType = Field(description="Artifact being generated")
    description: str = Field(description="Stage description")
    progress: int = Field(description="Progress percentage")


class ArtifactGenerationWorkflow(Workflow):
    """
    Workflow to generate supporting artifacts from a completed RFE document.

    Takes an RFE document as input and generates:
    1. Feature Refinement Document
    2. Architecture Document
    3. Epics and Stories Document
    """

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.llm: LLM = Settings.llm

    @step
    async def start_generation(self, ctx: Context, ev: StartEvent) -> StopEvent:
        """Generate all artifacts from the RFE document"""

        rfe_document = ev.get("rfe_document", "")
        if not rfe_document:
            raise ValueError("rfe_document is required for artifact generation")

        await ctx.set("rfe_document", rfe_document)

        ctx.write_event_to_stream(
            UIEvent(
                type="artifact_generation_progress",
                data=GenerationUIEventData(
                    stage="starting",
                    artifact_type=ArtifactType.FEATURE_REFINEMENT,
                    description="Starting artifact generation from your RFE...",
                    progress=5,
                ),
            )
        )

        artifacts = {}
        artifact_types = [
            (ArtifactType.FEATURE_REFINEMENT, "Feature Refinement Document"),
            (ArtifactType.ARCHITECTURE, "Architecture Document"),
            (ArtifactType.EPICS_STORIES, "Epics and Stories Document"),
        ]

        for i, (artifact_type, display_name) in enumerate(artifact_types):
            progress = 20 + ((i + 1) / len(artifact_types)) * 70

            ctx.write_event_to_stream(
                UIEvent(
                    type="artifact_generation_progress",
                    data=GenerationUIEventData(
                        stage="generating",
                        artifact_type=artifact_type,
                        description=f"Generating {display_name}...",
                        progress=int(progress),
                    ),
                )
            )

            # Generate the artifact content
            content = await self._generate_artifact_content(artifact_type, rfe_document)
            artifacts[artifact_type.value] = content

        # Emit the completed artifacts
        ctx.write_event_to_stream(
            UIEvent(
                type="rfe_artifacts",
                data={
                    "artifacts": artifacts,
                    "artifact_metadata": {
                        "feature_refinement": {
                            "title": "Feature Refinement",
                            "icon": "Workflow",
                        },
                        "architecture": {"title": "Architecture", "icon": "Building2"},
                        "epics_stories": {
                            "title": "Epics & Stories",
                            "icon": "ListChecks",
                        },
                    },
                },
            )
        )

        ctx.write_event_to_stream(
            UIEvent(
                type="artifact_generation_progress",
                data=GenerationUIEventData(
                    stage="completed",
                    artifact_type=ArtifactType.EPICS_STORIES,
                    description="All artifacts generated! You can now edit any document through chat.",
                    progress=100,
                ),
            )
        )

        return StopEvent(
            result={
                "artifacts": artifacts,
                "message": "All artifacts have been generated from your RFE. You can now edit any document by chatting!",
            }
        )

    async def _generate_artifact_content(
        self, artifact_type: ArtifactType, rfe_document: str
    ) -> str:
        """Generate content for a specific artifact type"""

        prompts = {
            ArtifactType.FEATURE_REFINEMENT: """
                Create a comprehensive feature refinement document in markdown format.
                Based on this RFE: {rfe}
                
                Include:
                - Feature Breakdown
                - User Stories with Acceptance Criteria
                - Edge Cases and Error Handling
                - Performance Requirements
                - Security Considerations
                - Testing Strategy
                - Dependencies and Integration Points
            """,
            ArtifactType.ARCHITECTURE: """
                Create a detailed architecture document in markdown format.
                Based on this RFE: {rfe}
                
                Include:
                - System Architecture Overview
                - Component Design and Responsibilities
                - Data Flow and Processing
                - Technology Stack Recommendations
                - API Design (if applicable)
                - Database Schema (if applicable)
                - Deployment Architecture
                - Scalability and Performance Considerations
                - Security Architecture
            """,
            ArtifactType.EPICS_STORIES: """
                Create an epics and user stories document in markdown format.
                Based on this RFE: {rfe}
                
                Include:
                - Epic Breakdown with clear themes
                - Detailed User Stories with Acceptance Criteria
                - Story Point Estimates (use Fibonacci: 1,2,3,5,8,13)
                - Dependencies between stories
                - Sprint/Release Planning suggestions
                - Definition of Done criteria
                - Risk Assessment for each epic
            """,
        }

        prompt = PromptTemplate(prompts[artifact_type]).format(rfe=rfe_document)
        response = await self.llm.acomplete(prompt)
        return response.text.strip()


# Export for LlamaDeploy
artifact_generation_workflow = create_artifact_generation_workflow()
