"""
RFE Investigation Workflow

Interactive workflow for building RFE documents through human-agent collaboration.
This workflow focuses solely on creating a comprehensive RFE document through conversation.
"""

import re
import time
from typing import Any, Dict, List, Optional, Union

from llama_index.core import Settings
from llama_index.core.llms import LLM, ChatMessage
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.prompts import PromptTemplate
from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)
from llama_index.core.chat_ui.models.artifact import (
    Artifact,
    ArtifactType,
    DocumentArtifactData,
)
from llama_index.core.chat_ui.events import (
    UIEvent,
    ArtifactEvent,
)

from src.settings import init_settings
from src.agents import RFEAgentManager, get_agent_personas
from pydantic import BaseModel, Field
from dotenv import load_dotenv


def create_rfe_investigation_workflow() -> Workflow:
    load_dotenv()
    init_settings()
    return RFEInvestigationWorkflow(timeout=300.0)


class InvestigationUIEventData(BaseModel):
    """UI event data for investigation workflow"""

    stage: str = Field(description="Current investigation stage")
    description: Optional[str] = Field(default=None, description="Stage description")
    agent_persona: Optional[str] = Field(
        default=None, description="Current agent providing insights"
    )
    streaming_type: Optional[str] = Field(
        default=None, description="Type of streaming content"
    )


class AgentInsightEvent(Event):
    """Event containing agent insights for the user"""

    agent_persona: str
    insights: str
    questions: List[str]
    current_rfe_draft: Optional[str] = None


class UserResponseEvent(Event):
    """Event containing user's response to agent insights"""

    user_response: str
    agent_persona: str
    current_rfe_draft: Optional[str] = None


class RFEInvestigationWorkflow(Workflow):
    """
    Interactive RFE investigation workflow.

    This workflow facilitates back-and-forth conversation between the user and AI agents
    to thoroughly investigate and refine an RFE idea into a comprehensive document.
    """

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.llm: LLM = Settings.llm
        self.agent_manager = RFEAgentManager()
        self.conversation_history: List[ChatMessage] = []
        self.current_rfe_draft: Optional[str] = None

    @step
    async def start_investigation(
        self, ctx: Context, ev: StartEvent
    ) -> AgentInsightEvent:
        """Start the RFE investigation process"""
        user_msg = ev.get("user_msg", "")
        chat_history = ev.get("chat_history", [])

        await ctx.set("original_idea", user_msg)
        await ctx.set("chat_history", chat_history)

        # Initialize conversation history
        self.conversation_history = [ChatMessage(role="user", content=user_msg)]

        ctx.write_event_to_stream(
            UIEvent(
                type="investigation_progress",
                data=InvestigationUIEventData(
                    stage="starting",
                    description="Starting RFE investigation with AI agents...",
                ),
            )
        )

        # Get first agent for investigation
        agent_personas = await get_agent_personas()
        if not agent_personas:
            # Fallback without agents
            return await self._handle_no_agents(ctx, user_msg)

        # Use product owner or first available agent
        persona_key = self._select_investigation_agent(agent_personas)
        persona_config = (
            agent_personas.get(persona_key)
            if isinstance(agent_personas, dict)
            else None
        )

        ctx.write_event_to_stream(
            UIEvent(
                type="investigation_progress",
                data=InvestigationUIEventData(
                    stage="analyzing",
                    description=f"Agent {persona_key} is analyzing your idea...",
                    agent_persona=persona_key,
                    streaming_type="reasoning",
                ),
            )
        )

        # Get initial insights from agent
        insights, questions = await self._get_agent_investigation(
            persona_key, user_msg, None, persona_config
        )

        return AgentInsightEvent(
            agent_persona=persona_key,
            insights=insights,
            questions=questions,
            current_rfe_draft=None,
        )

    @step
    async def present_agent_insights(
        self, ctx: Context, ev: AgentInsightEvent
    ) -> UserResponseEvent:
        """Present agent insights to user and wait for response"""

        ctx.write_event_to_stream(
            UIEvent(
                type="investigation_progress",
                data=InvestigationUIEventData(
                    stage="waiting_for_user",
                    description=f"Agent {ev.agent_persona} has provided insights. Please respond to continue the investigation.",
                    agent_persona=ev.agent_persona,
                ),
            )
        )

        # Create a formatted response to show the user
        formatted_response = f"""**{ev.agent_persona} Agent Analysis:**

{ev.insights}

**Questions to help refine your RFE:**
"""
        for i, question in enumerate(ev.questions, 1):
            formatted_response += f"\n{i}. {question}"

        formatted_response += "\n\n*Please respond with your thoughts, answers, or additional details to continue refining your RFE.*"

        # This would typically wait for user input in an interactive system
        # For now, we'll simulate getting the next message from chat_history
        # In a real implementation, this step would pause and wait for user input

        return UserResponseEvent(
            user_response="Please continue the investigation based on my input",
            agent_persona=ev.agent_persona,
            current_rfe_draft=ev.current_rfe_draft,
        )

    @step
    async def process_user_response(
        self, ctx: Context, ev: UserResponseEvent
    ) -> Union[AgentInsightEvent, StopEvent]:
        """Process user response and decide next steps"""

        # Add user response to conversation history
        self.conversation_history.append(
            ChatMessage(role="user", content=ev.user_response)
        )

        ctx.write_event_to_stream(
            UIEvent(
                type="investigation_progress",
                data=InvestigationUIEventData(
                    stage="processing",
                    description="Processing your response and updating RFE draft...",
                    streaming_type="writing",
                ),
            )
        )

        # Update RFE draft based on conversation
        updated_rfe = await self._update_rfe_draft(
            self.conversation_history, ev.current_rfe_draft
        )
        self.current_rfe_draft = updated_rfe

        # Determine if we need more investigation or can finalize
        needs_more_investigation = await self._assess_rfe_completeness(updated_rfe)

        if not needs_more_investigation:
            # RFE is complete, finalize it
            return await self._finalize_rfe(ctx, updated_rfe)
        else:
            # Continue investigation with next agent or more questions
            return await self._continue_investigation(
                ctx, updated_rfe, ev.agent_persona
            )

    async def _get_agent_investigation(
        self,
        persona_key: str,
        user_input: str,
        current_rfe: Optional[str],
        persona_config: Optional[Dict],
    ) -> tuple[str, List[str]]:
        """Get agent insights and questions for investigation"""

        context = f"""
        User's idea: {user_input}
        Current RFE draft: {current_rfe or 'None - this is the initial investigation'}
        
        As a {persona_key}, analyze this idea and provide:
        1. Your insights about the technical/business aspects
        2. Specific questions to help the user flesh out the requirements
        """

        if persona_config:
            try:
                analysis = await self.agent_manager.analyze_rfe(
                    persona_key, context, persona_config
                )
                insights = analysis.get("analysis", "No insights provided")

                # Extract or generate questions
                questions = self._extract_questions_from_analysis(analysis, persona_key)
                return insights, questions

            except Exception as e:
                print(f"Agent analysis error: {e}")

        # Fallback to direct LLM
        return await self._fallback_investigation(persona_key, context)

    async def _fallback_investigation(
        self, persona_key: str, context: str
    ) -> tuple[str, List[str]]:
        """Fallback investigation without agent manager"""
        prompt = f"""
        You are a {persona_key} expert. {context}
        
        Provide:
        1. Your professional insights (2-3 sentences)
        2. 3-5 specific questions to help refine this into a complete RFE
        
        Format:
        INSIGHTS: [your insights]
        QUESTIONS:
        1. [question 1]
        2. [question 2]
        ...
        """

        response = await self.llm.acomplete(prompt)
        text = response.text

        # Parse response
        insights = ""
        questions = []

        if "INSIGHTS:" in text and "QUESTIONS:" in text:
            parts = text.split("QUESTIONS:")
            insights = parts[0].replace("INSIGHTS:", "").strip()
            questions_text = parts[1].strip()
            questions = [
                q.strip()
                for q in questions_text.split("\n")
                if q.strip() and any(c.isdigit() for c in q[:5])
            ]

        return insights, questions

    def _extract_questions_from_analysis(
        self, analysis: Dict, persona_key: str
    ) -> List[str]:
        """Extract questions from agent analysis"""
        # Try to find questions in the analysis
        questions = []

        # Look for common question indicators
        text = str(analysis)
        question_patterns = [
            r"\?\s*(?:\n|$)",  # Lines ending with ?
            r"(?:question|ask|clarify|understand).*?\?",  # Question-like phrases
        ]

        for pattern in question_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract the sentence containing the question
                start = max(0, text.rfind(".", 0, match.start()) + 1)
                end = min(len(text), text.find(".", match.end()))
                if end == -1:
                    end = len(text)
                question = text[start:end].strip()
                if question and "?" in question and len(question) > 10:
                    questions.append(question)

        # If no questions found, generate some based on persona
        if not questions:
            questions = self._generate_default_questions(persona_key)

        return questions[:5]  # Limit to 5 questions

    def _generate_default_questions(self, persona_key: str) -> List[str]:
        """Generate default questions based on agent persona"""
        default_questions = {
            "product_owner": [
                "What specific business value will this provide to users?",
                "What are the key success metrics for this feature?",
                "Are there any regulatory or compliance considerations?",
            ],
            "backend_eng": [
                "What are the expected performance requirements?",
                "How should this integrate with existing systems?",
                "What are the scalability considerations?",
            ],
            "frontend_eng": [
                "What should the user experience look like?",
                "Are there any accessibility requirements?",
                "How should this work on mobile devices?",
            ],
        }

        return default_questions.get(
            persona_key,
            [
                "What are the main requirements for this feature?",
                "What constraints should we consider?",
                "How will success be measured?",
            ],
        )

    async def _update_rfe_draft(
        self, conversation_history: List[ChatMessage], current_draft: Optional[str]
    ) -> str:
        """Update RFE draft based on conversation history"""

        conversation_text = "\n".join(
            [f"{msg.role}: {msg.content}" for msg in conversation_history]
        )

        prompt = f"""
        Based on this conversation, create or update an RFE document:
        
        Conversation:
        {conversation_text}
        
        Current draft: {current_draft or 'None - create initial draft'}
        
        Create a comprehensive RFE document with:
        - Problem Statement
        - Proposed Solution
        - Requirements
        - Constraints
        - Success Criteria
        
        Return only the RFE document content.
        """

        response = await self.llm.acomplete(prompt)
        return response.text.strip()

    async def _assess_rfe_completeness(self, rfe_draft: str) -> bool:
        """Assess if the RFE needs more investigation"""

        prompt = f"""
        Assess if this RFE draft is complete enough for implementation planning:
        
        {rfe_draft}
        
        Consider:
        - Are requirements clearly defined?
        - Are constraints identified?
        - Are success criteria specified?
        - Are there obvious gaps or ambiguities?
        
        Respond with only: COMPLETE or NEEDS_MORE_INVESTIGATION
        """

        response = await self.llm.acomplete(prompt)
        return "NEEDS_MORE_INVESTIGATION" in response.text.upper()

    async def _continue_investigation(
        self, ctx: Context, updated_rfe: str, current_agent: str
    ) -> AgentInsightEvent:
        """Continue investigation with more questions"""

        # For now, continue with the same agent for follow-up questions
        # In a more complex implementation, we might switch agents

        insights, questions = await self._get_follow_up_investigation(
            current_agent, updated_rfe
        )

        return AgentInsightEvent(
            agent_persona=current_agent,
            insights=insights,
            questions=questions,
            current_rfe_draft=updated_rfe,
        )

    async def _get_follow_up_investigation(
        self, persona_key: str, current_rfe: str
    ) -> tuple[str, List[str]]:
        """Get follow-up investigation questions"""

        prompt = f"""
        As a {persona_key} expert, review this RFE draft and identify what's still missing:
        
        {current_rfe}
        
        Provide:
        INSIGHTS: What looks good and what needs more detail
        QUESTIONS: 
        1. [specific question about missing details]
        2. [specific question about unclear aspects]
        3. [specific question about implementation concerns]
        """

        response = await self.llm.acomplete(prompt)
        return await self._fallback_investigation(
            persona_key, f"Review and refine: {current_rfe}"
        )

    async def _finalize_rfe(self, ctx: Context, rfe_draft: str) -> StopEvent:
        """Finalize the RFE document"""

        ctx.write_event_to_stream(
            UIEvent(
                type="investigation_progress",
                data=InvestigationUIEventData(
                    stage="finalizing",
                    description="Finalizing your RFE document...",
                    streaming_type="writing",
                ),
            )
        )

        # Create the final RFE artifact
        ctx.write_event_to_stream(
            ArtifactEvent(
                data=Artifact(
                    type=ArtifactType.DOCUMENT,
                    created_at=int(time.time()),
                    data=DocumentArtifactData(
                        title="RFE Document",
                        content=rfe_draft,
                        type="markdown",
                        sources=[],
                    ),
                ),
            )
        )

        ctx.write_event_to_stream(
            UIEvent(
                type="investigation_progress",
                data=InvestigationUIEventData(
                    stage="completed",
                    description="RFE investigation complete! You can now generate additional artifacts or continue chatting to refine.",
                ),
            )
        )

        return StopEvent(
            result={
                "rfe_document": rfe_draft,
                "phase": "investigation_complete",
                "message": "RFE document ready! You can now generate additional artifacts (Feature Refinement, Architecture, Epics & Stories) or continue refining this RFE.",
            }
        )

    def _select_investigation_agent(self, agent_personas) -> str:
        """Select the best agent for initial investigation"""
        if isinstance(agent_personas, dict):
            # Prefer product owner for initial investigation
            if "product_owner" in agent_personas:
                return "product_owner"
            return list(agent_personas.keys())[0]
        elif isinstance(agent_personas, list):
            return agent_personas[0]
        return "default"

    async def _handle_no_agents(self, ctx: Context, user_msg: str) -> AgentInsightEvent:
        """Handle investigation when no agents are available"""
        insights = "I'll help you develop this RFE through direct conversation."
        questions = [
            "Can you describe the problem this feature would solve?",
            "Who are the main users of this feature?",
            "What would success look like for this feature?",
        ]

        return AgentInsightEvent(
            agent_persona="Assistant",
            insights=insights,
            questions=questions,
            current_rfe_draft=None,
        )


# Export for LlamaDeploy
rfe_investigation_workflow = create_rfe_investigation_workflow()
