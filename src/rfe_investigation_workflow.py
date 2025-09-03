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


class QuestionEvent(Event):
    """Event to present questions to the user"""

    agent_persona: str
    insights: str
    questions: List[str]
    conversation_context: str


class UserResponseEvent(Event):
    """Event containing user's response"""

    user_message: str
    conversation_context: str


class AssessmentEvent(Event):
    """Event to assess if we have enough info for RFE"""

    conversation_context: str


class CreateRFEEvent(Event):
    """Event to create the RFE document"""

    conversation_context: str


class RFECompleteEvent(Event):
    """Event when RFE is complete"""

    rfe_content: str


# Structured Output Models
class AgentInvestigationResponse(BaseModel):
    """Structured response from agent investigation"""

    insights: str = Field(
        description="Agent's professional insights about the idea (2-3 sentences)"
    )
    questions: List[str] = Field(
        description="3-5 specific questions to help refine the RFE"
    )


class CompletenessAssessment(BaseModel):
    """Assessment of whether we have enough information for RFE"""

    assessment: str = Field(description="Either 'NEED_MORE_INFO' or 'READY_FOR_RFE'")
    reasoning: str = Field(description="Brief explanation of the assessment")


class FollowUpResponse(BaseModel):
    """Follow-up questions and insights"""

    insights: str = Field(
        description="Summary of what we've learned and what's missing"
    )
    questions: List[str] = Field(description="3-5 specific follow-up questions")


class RFEInvestigationWorkflow(Workflow):
    """
    Interactive RFE investigation workflow.

    This workflow handles each user message and provides interactive chat responses
    with AI agents to thoroughly investigate and refine an RFE idea.
    """

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.llm: LLM = Settings.llm
        self.agent_manager = RFEAgentManager()

    @step
    async def start_investigation(self, ctx: Context, ev: StartEvent) -> QuestionEvent:
        """Step 1: Analyze initial user idea and generate first questions"""
        user_msg = ev.get("user_msg", "")
        chat_history = ev.get("chat_history", [])

        # Store in context for other steps
        await ctx.set(
            "conversation_history",
            chat_history + [{"role": "user", "content": user_msg}],
        )

        ctx.write_event_to_stream(
            UIEvent(
                type="investigation_progress",
                data=InvestigationUIEventData(
                    stage="analyzing",
                    description="Agent is analyzing your idea...",
                    streaming_type="reasoning",
                ),
            )
        )

        # Get agent for investigation
        agent_personas = await get_agent_personas()
        persona_key = self._select_investigation_agent(agent_personas)
        persona_config = (
            agent_personas.get(persona_key)
            if isinstance(agent_personas, dict) and agent_personas
            else None
        )

        # Get initial insights and questions from agent
        insights, questions = await self._get_agent_investigation(
            persona_key, user_msg, None, persona_config, ctx
        )

        conversation_context = self._build_conversation_context(chat_history, user_msg)

        return QuestionEvent(
            agent_persona=persona_key,
            insights=insights,
            questions=questions,
            conversation_context=conversation_context,
        )

    @step
    async def present_questions(self, ctx: Context, ev: QuestionEvent) -> StopEvent:
        """Step 2: Present agent questions to user and wait for response"""

        ctx.write_event_to_stream(
            UIEvent(
                type="investigation_progress",
                data=InvestigationUIEventData(
                    stage="waiting_for_user",
                    description=f"Agent {ev.agent_persona} is ready with questions...",
                    agent_persona=ev.agent_persona,
                ),
            )
        )

        # Format response with insights and questions
        agent_response = f"""I'll help you develop this RFE! Let me analyze your idea as a **{ev.agent_persona}** agent.

**My Analysis:**
{ev.insights}

**Questions to help refine your RFE:**
"""
        for i, question in enumerate(ev.questions, 1):
            agent_response += f"\n{i}. {question}"

        agent_response += f"\n\nPlease answer these questions so I can help you create a comprehensive RFE document!"

        # Store context for when user responds
        await ctx.set("last_conversation_context", ev.conversation_context)
        await ctx.set("current_agent", ev.agent_persona)

        return StopEvent(result={"response": agent_response})

    @step
    async def process_user_response(
        self, ctx: Context, ev: UserResponseEvent
    ) -> AssessmentEvent:
        """Step 3: Process user's response and update conversation context"""

        ctx.write_event_to_stream(
            UIEvent(
                type="investigation_progress",
                data=InvestigationUIEventData(
                    stage="processing",
                    description="Processing your response...",
                    streaming_type="reasoning",
                ),
            )
        )

        # Get stored conversation context and update it
        conversation_history = await ctx.get("conversation_history", [])
        conversation_history.append({"role": "user", "content": ev.user_message})
        await ctx.set("conversation_history", conversation_history)

        # Build updated conversation context
        updated_context = self._build_conversation_context_from_history(
            conversation_history
        )

        return AssessmentEvent(conversation_context=updated_context)

    @step
    async def assess_completeness(
        self, ctx: Context, ev: AssessmentEvent
    ) -> Union[QuestionEvent, CreateRFEEvent]:
        """Step 4: Assess if we need more info or can create RFE"""

        ctx.write_event_to_stream(
            UIEvent(
                type="investigation_progress",
                data=InvestigationUIEventData(
                    stage="assessing",
                    description="Assessing if we have enough information...",
                    streaming_type="reasoning",
                ),
            )
        )

        # Assess if we need more information
        needs_more_info = await self._assess_need_for_more_investigation(
            ev.conversation_context
        )

        if needs_more_info:
            # Generate follow-up questions - LOOP BACK TO QUESTIONS STEP
            current_agent = await ctx.get("current_agent", "Assistant")
            insights, questions = await self._generate_follow_up_questions(
                ev.conversation_context, current_agent, ctx
            )

            return QuestionEvent(
                agent_persona=current_agent,
                insights=insights,
                questions=questions,
                conversation_context=ev.conversation_context,
            )
        else:
            # Ready to create RFE - MOVE TO CREATION STEP
            return CreateRFEEvent(conversation_context=ev.conversation_context)

    @step
    async def create_rfe_document(
        self, ctx: Context, ev: CreateRFEEvent
    ) -> RFECompleteEvent:
        """Step 5: Create the final RFE document"""

        ctx.write_event_to_stream(
            UIEvent(
                type="investigation_progress",
                data=InvestigationUIEventData(
                    stage="creating_rfe",
                    description="Creating your RFE document...",
                    streaming_type="writing",
                ),
            )
        )

        # Generate the RFE document
        rfe_content = await self._generate_rfe_from_conversation(
            ev.conversation_context
        )

        # Create the artifact
        ctx.write_event_to_stream(
            ArtifactEvent(
                data=Artifact(
                    type=ArtifactType.DOCUMENT,
                    created_at=int(time.time()),
                    data=DocumentArtifactData(
                        title="RFE Document",
                        content=rfe_content,
                        type="markdown",
                        sources=[],
                    ),
                ),
            )
        )

        return RFECompleteEvent(rfe_content=rfe_content)

    @step
    async def finalize_rfe(self, ctx: Context, ev: RFECompleteEvent) -> StopEvent:
        """Step 6: Present completed RFE and next options"""

        ctx.write_event_to_stream(
            UIEvent(
                type="investigation_progress",
                data=InvestigationUIEventData(
                    stage="completed",
                    description="RFE document completed!",
                ),
            )
        )

        # Create chat response explaining what we did
        chat_response = f"""Perfect! I've created a comprehensive RFE document based on our conversation. 

**What I included:**
- Problem statement and background
- Detailed requirements and specifications  
- User stories and acceptance criteria
- Technical considerations and constraints
- Success metrics and validation approach

The RFE document is now available in the artifacts panel. You can:

✅ **Continue refining**: Ask me to adjust any part of the RFE
🚀 **Generate artifacts**: Say "generate artifacts" to create Feature Refinement, Architecture, and Epics & Stories documents  
💬 **Keep chatting**: I'm here to help with any questions or changes

What would you like to do next?"""

        return StopEvent(
            result={
                "response": chat_response,
                "rfe_document": ev.rfe_content,
                "phase": "rfe_complete",
            }
        )

    # Special step to handle user responses - this gets triggered when user sends a new message
    @step
    async def handle_new_user_message(
        self, ctx: Context, ev: StartEvent
    ) -> Union[UserResponseEvent, QuestionEvent]:
        """Handle new user messages and route appropriately"""
        user_msg = ev.get("user_msg", "")
        chat_history = ev.get("chat_history", [])

        # Determine if this is an initial idea or a response to questions
        conversation_stage = self._determine_conversation_stage(chat_history)

        if conversation_stage == "initial":
            # This is handled by start_investigation step
            return QuestionEvent(
                agent_persona="Assistant",
                insights="Starting investigation...",
                questions=["Tell me more about your idea"],
                conversation_context=user_msg,
            )
        else:
            # This is a response to previous questions
            conversation_context = self._build_conversation_context(
                chat_history, user_msg
            )
            return UserResponseEvent(
                user_message=user_msg, conversation_context=conversation_context
            )

    def _determine_conversation_stage(self, chat_history: List) -> str:
        """Determine what stage of the investigation we're in"""
        if not chat_history:
            return "initial"

        # Look for RFE document in chat history
        has_rfe_artifact = any(
            "RFE Document" in str(msg) or "rfe_document" in str(msg)
            for msg in chat_history
        )

        # Check if we're in refinement mode (after RFE is created)
        if has_rfe_artifact:
            return "refining"

        # Check if we're in active investigation (agent has asked questions)
        recent_agent_questions = any(
            "Questions to help refine" in str(msg) or "?" in str(msg)
            for msg in chat_history[-3:]
            if msg
        )

        if recent_agent_questions:
            return "investigating"

        return "initial"

    async def _handle_initial_idea(
        self, ctx: Context, user_msg: str, chat_history: List
    ) -> StopEvent:
        """Handle the user's initial RFE idea"""
        ctx.write_event_to_stream(
            UIEvent(
                type="investigation_progress",
                data=InvestigationUIEventData(
                    stage="analyzing",
                    description="Agent is analyzing your idea and preparing questions...",
                    streaming_type="reasoning",
                ),
            )
        )

        # Get agent for investigation
        agent_personas = await get_agent_personas()
        persona_key = self._select_investigation_agent(agent_personas)
        persona_config = (
            agent_personas.get(persona_key)
            if isinstance(agent_personas, dict) and agent_personas
            else None
        )

        # Get initial insights and questions from agent
        insights, questions = await self._get_agent_investigation(
            persona_key, user_msg, None, persona_config, ctx
        )

        # Format response with insights and questions
        agent_response = f"""I'll help you develop this RFE! Let me analyze your idea as a **{persona_key}** agent.

**My Analysis:**
{insights}

**Questions to help refine your RFE:**
"""
        for i, question in enumerate(questions, 1):
            agent_response += f"\n{i}. {question}"

        agent_response += f"\n\nPlease answer these questions so I can help you create a comprehensive RFE document!"

        return StopEvent(result={"response": agent_response})

    async def _handle_investigation_response(
        self, ctx: Context, user_msg: str, chat_history: List
    ) -> StopEvent:
        """Handle user's response during investigation phase"""
        ctx.write_event_to_stream(
            UIEvent(
                type="investigation_progress",
                data=InvestigationUIEventData(
                    stage="processing",
                    description="Processing your response and determining next steps...",
                    streaming_type="reasoning",
                ),
            )
        )

        # Build conversation context
        conversation_text = self._build_conversation_context(chat_history, user_msg)

        # Decide if we have enough information for RFE or need more questions
        needs_more_info = await self._assess_need_for_more_investigation(
            conversation_text
        )

        if needs_more_info:
            return await self._ask_follow_up_questions(ctx, conversation_text)
        else:
            return await self._create_rfe_document(ctx, conversation_text)

    async def _handle_refinement_request(
        self, ctx: Context, user_msg: str, chat_history: List
    ) -> StopEvent:
        """Handle requests to refine or adjust the RFE after it's been created"""
        ctx.write_event_to_stream(
            UIEvent(
                type="investigation_progress",
                data=InvestigationUIEventData(
                    stage="refining",
                    description="Analyzing your refinement request...",
                    streaming_type="reasoning",
                ),
            )
        )

        # Check if user wants to generate artifacts
        if any(
            keyword in user_msg.lower()
            for keyword in [
                "generate artifacts",
                "create artifacts",
                "next workflow",
                "generate documents",
            ]
        ):
            return await self._suggest_artifact_generation(ctx)

        # Otherwise, handle refinement of the RFE
        conversation_context = self._build_conversation_context(chat_history, user_msg)
        return await self._refine_existing_rfe(ctx, conversation_context, user_msg)

    async def _handle_general_chat(
        self, ctx: Context, user_msg: str, chat_history: List
    ) -> StopEvent:
        """Handle general chat messages"""
        response = f"I'm here to help you investigate and refine RFE ideas. Please share your feature idea and I'll help you develop it into a comprehensive RFE document!"
        return StopEvent(result={"response": response})

    async def _get_agent_investigation(
        self,
        persona_key: str,
        user_input: str,
        current_rfe: Optional[str],
        persona_config: Optional[Dict],
        ctx=None,
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
                    persona_key, context, persona_config, ctx
                )
                insights = analysis.get("analysis", "No insights provided")

                # Extract or generate questions
                questions = self._extract_questions_from_analysis(analysis, persona_key)
                return insights, questions

            except Exception as e:
                print(f"Agent analysis error: {e}")

        # Fallback to direct LLM
        return await self._fallback_investigation(persona_key, context)

    def _build_conversation_context(self, chat_history: List, current_msg: str) -> str:
        """Build conversation context from chat history"""
        context_parts = []

        for msg in chat_history[-10:]:  # Last 10 messages for context
            if hasattr(msg, "content"):
                context_parts.append(f"User: {msg.content}")
            elif isinstance(msg, dict) and "content" in msg:
                role = msg.get("role", "user")
                context_parts.append(f"{role}: {msg['content']}")
            else:
                context_parts.append(f"Message: {str(msg)}")

        context_parts.append(f"User: {current_msg}")
        return "\n\n".join(context_parts)

    def _build_conversation_context_from_history(
        self, conversation_history: List
    ) -> str:
        """Build conversation context from stored conversation history"""
        context_parts = []

        for msg in conversation_history[-10:]:  # Last 10 messages for context
            if isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                context_parts.append(f"{role}: {content}")
            else:
                context_parts.append(f"Message: {str(msg)}")

        return "\n\n".join(context_parts)

    async def _generate_follow_up_questions(
        self, conversation_context: str, agent_persona: str, ctx=None
    ) -> tuple[str, List[str]]:
        """Generate follow-up questions based on conversation using structured outputs"""

        # Stream UI event for generating follow-up questions
        if ctx:
            ctx.write_event_to_stream(
                UIEvent(
                    type="investigation_progress",
                    data=InvestigationUIEventData(
                        stage="generating_questions",
                        description=f"🤔 {agent_persona} is analyzing the conversation and generating follow-up questions...",
                        agent_persona=agent_persona,
                        streaming_type="reasoning",
                    ),
                )
            )

        prompt_template = PromptTemplate(
            """
        As a {agent_persona} expert, review this conversation and generate follow-up questions to gather missing information.

        Conversation:
        {conversation_context}

        Analyze what we've learned so far and what key information is still missing to create a comprehensive RFE document.
        
        Your insights should summarize the current state and identify gaps.
        Your questions should be 3-5 specific, actionable follow-up questions that will help fill those gaps.
        """
        )

        formatted_prompt = prompt_template.format(
            agent_persona=agent_persona, conversation_context=conversation_context
        )
        response = await Settings.llm.astream_structured_predict(
            FollowUpResponse, formatted_prompt
        )

        # Stream completion event
        if ctx:
            ctx.write_event_to_stream(
                UIEvent(
                    type="investigation_progress",
                    data=InvestigationUIEventData(
                        stage="questions_generated",
                        description=f"✅ {agent_persona} generated {len(response.questions)} follow-up questions",
                        agent_persona=agent_persona,
                        streaming_type="reasoning",
                    ),
                )
            )

        return response.insights, response.questions

    async def _assess_need_for_more_investigation(self, conversation_text: str) -> bool:
        """Assess if we need more information before creating RFE using structured outputs"""

        prompt_template = PromptTemplate(
            """
        Based on this conversation about an RFE idea, determine if we have enough information to create a comprehensive RFE document.

        Conversation:
        {conversation_text}

        Consider:
        - Do we understand the problem being solved?
        - Are the requirements clear?
        - Do we know the target users?
        - Are success criteria identified?
        - Are constraints and limitations understood?

        Assessment should be either 'NEED_MORE_INFO' or 'READY_FOR_RFE'.
        Provide reasoning for your assessment.
        """
        )

        formatted_prompt = prompt_template.format(conversation_text=conversation_text)
        response = await Settings.llm.astream_structured_predict(
            CompletenessAssessment, formatted_prompt
        )
        return response.assessment == "NEED_MORE_INFO"

    async def _ask_follow_up_questions(
        self, ctx: Context, conversation_text: str
    ) -> StopEvent:
        """Generate follow-up questions based on conversation using structured outputs"""
        ctx.write_event_to_stream(
            UIEvent(
                type="investigation_progress",
                data=InvestigationUIEventData(
                    stage="analyzing",
                    description="Generating follow-up questions...",
                    streaming_type="reasoning",
                ),
            )
        )

        prompt_template = PromptTemplate(
            """
        Based on this conversation about an RFE, generate specific follow-up questions to gather missing information.

        Conversation:
        {conversation_text}

        Generate questions that help clarify:
        - Technical requirements not yet discussed
        - Business objectives and success metrics
        - User experience considerations
        - Implementation constraints
        - Integration requirements

        Your insights should briefly summarize what we know and what's missing.
        Your questions should be 3-5 specific, actionable questions.
        """
        )

        formatted_prompt = prompt_template.format(conversation_text=conversation_text)
        response = await Settings.llm.astream_structured_predict(
            FollowUpResponse, formatted_prompt
        )

        # Format questions nicely
        formatted_questions = "\n".join(
            [f"{i+1}. {q}" for i, q in enumerate(response.questions)]
        )

        agent_response = f"""Thanks for the additional details! I need a bit more information to create a comprehensive RFE document.

**My Assessment:**
{response.insights}

**Follow-up questions:**

{formatted_questions}

Please provide more details on these aspects so I can create the perfect RFE document for you!"""

        return StopEvent(result={"response": agent_response})

    async def _create_rfe_document(
        self, ctx: Context, conversation_text: str
    ) -> StopEvent:
        """Create the final RFE document and artifact"""
        ctx.write_event_to_stream(
            UIEvent(
                type="investigation_progress",
                data=InvestigationUIEventData(
                    stage="finalizing",
                    description="Creating your RFE document...",
                    streaming_type="writing",
                ),
            )
        )

        # Generate the RFE document
        rfe_content = await self._generate_rfe_from_conversation(conversation_text)

        # Create the artifact
        ctx.write_event_to_stream(
            ArtifactEvent(
                data=Artifact(
                    type=ArtifactType.DOCUMENT,
                    created_at=int(time.time()),
                    data=DocumentArtifactData(
                        title="RFE Document",
                        content=rfe_content,
                        type="markdown",
                        sources=[],
                    ),
                ),
            )
        )

        # Create chat response explaining what we did
        chat_response = f"""Perfect! I've created a comprehensive RFE document based on our conversation. 

**What I included:**
- Problem statement and background
- Detailed requirements and specifications  
- User stories and acceptance criteria
- Technical considerations and constraints
- Success metrics and validation approach

The RFE document is now available in the artifacts panel. You can:

✅ **Continue refining**: Ask me to adjust any part of the RFE
🚀 **Generate artifacts**: Say "generate artifacts" to create Feature Refinement, Architecture, and Epics & Stories documents  
💬 **Keep chatting**: I'm here to help with any questions or changes

What would you like to do next?"""

        ctx.write_event_to_stream(
            UIEvent(
                type="investigation_progress",
                data=InvestigationUIEventData(
                    stage="completed",
                    description="RFE document created! You can now refine it or generate additional artifacts.",
                ),
            )
        )

        return StopEvent(
            result={
                "response": chat_response,
                "rfe_document": rfe_content,
                "phase": "rfe_complete",
            }
        )

    async def _generate_rfe_from_conversation(self, conversation_text: str) -> str:
        """Generate comprehensive RFE document from conversation"""
        prompt = f"""
        Create a comprehensive RFE (Request for Enhancement) document based on this conversation.

        Conversation:
        {conversation_text}

        Create a well-structured RFE document in markdown format with these sections:

        # RFE: [Feature Name]

        ## Executive Summary
        Brief overview of the proposed feature

        ## Problem Statement
        What problem does this solve?

        ## Proposed Solution
        Detailed description of the proposed solution

        ## Requirements
        ### Functional Requirements
        ### Non-Functional Requirements
        ### User Stories

        ## Technical Specifications
        Technical details and approach

        ## Constraints and Limitations
        Any constraints or limitations

        ## Success Criteria
        How will we measure success?

        ## Implementation Timeline
        High-level timeline considerations

        Make it comprehensive, professional, and implementation-ready.
        """

        response = await self.llm.acomplete(prompt)
        return response.text.strip()

    async def _suggest_artifact_generation(self, ctx: Context) -> StopEvent:
        """Suggest moving to artifact generation workflow"""
        response = """Great! You're ready to generate additional artifacts from your RFE.

To generate the supporting documents (Feature Refinement, Architecture, Epics & Stories), you'll need to use the **Artifact Generation Workflow**.

**How to proceed:**
1. Switch to the `artifact-generation-workflow` service
2. Provide your RFE document as input
3. The workflow will generate all three supporting documents
4. They'll appear as tabs in the artifacts panel

**Or** if you want to continue refining the RFE first, just let me know what changes you'd like to make!"""

        return StopEvent(result={"response": response})

    async def _refine_existing_rfe(
        self, ctx: Context, conversation_context: str, refinement_request: str
    ) -> StopEvent:
        """Refine an existing RFE based on user request"""
        ctx.write_event_to_stream(
            UIEvent(
                type="investigation_progress",
                data=InvestigationUIEventData(
                    stage="refining",
                    description="Refining your RFE document...",
                    streaming_type="writing",
                ),
            )
        )

        # Extract current RFE from conversation context
        current_rfe = self._extract_current_rfe_from_context(conversation_context)

        # Generate refined RFE
        refined_rfe = await self._apply_refinements_to_rfe(
            current_rfe, refinement_request
        )

        # Create updated artifact
        ctx.write_event_to_stream(
            ArtifactEvent(
                data=Artifact(
                    type=ArtifactType.DOCUMENT,
                    created_at=int(time.time()),
                    data=DocumentArtifactData(
                        title="RFE Document",
                        content=refined_rfe,
                        type="markdown",
                        sources=[],
                    ),
                ),
            )
        )

        chat_response = f"""I've updated your RFE document based on your request: "{refinement_request}"

The refined RFE document is now available in the artifacts panel. 

**What I changed:**
- Incorporated your feedback
- Updated relevant sections
- Maintained document structure and completeness

Anything else you'd like me to adjust, or are you ready to generate the additional artifacts?"""

        return StopEvent(
            result={"response": chat_response, "rfe_document": refined_rfe}
        )

    def _extract_current_rfe_from_context(self, conversation_context: str) -> str:
        """Extract the current RFE content from conversation context"""
        # Look for RFE document in the conversation
        lines = conversation_context.split("\n")
        rfe_lines = []
        in_rfe = False

        for line in lines:
            if "# RFE:" in line or "RFE Document" in line:
                in_rfe = True
            if in_rfe:
                rfe_lines.append(line)

        if rfe_lines:
            return "\n".join(rfe_lines)

        # Fallback
        return "No RFE document found in conversation history."

    async def _apply_refinements_to_rfe(
        self, current_rfe: str, refinement_request: str
    ) -> str:
        """Apply user's refinement request to the RFE"""
        prompt = f"""
        Update this RFE document based on the user's refinement request.

        Current RFE:
        {current_rfe}

        User's refinement request:
        {refinement_request}

        Apply the requested changes while maintaining the RFE document structure and completeness.
        Return the full updated RFE document.
        """

        response = await self.llm.acomplete(prompt)
        return response.text.strip()

    async def _fallback_investigation(
        self, persona_key: str, context: str
    ) -> tuple[str, List[str]]:
        """Fallback investigation without agent manager using structured outputs"""

        prompt_template = PromptTemplate(
            """
        You are a {persona_key} expert. {context}
        
        As a {persona_key}, analyze this idea and provide your professional insights and specific questions to help refine this into a complete RFE.
        
        Your insights should be 2-3 sentences covering the technical/business aspects from your expertise area.
        Your questions should be 3-5 specific, actionable questions that will help gather missing information.
        """
        )

        formatted_prompt = prompt_template.format(
            persona_key=persona_key, context=context
        )
        response = await Settings.llm.astream_structured_predict(
            AgentInvestigationResponse, formatted_prompt
        )
        return response.insights, response.questions

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


# Export for LlamaDeploy
rfe_investigation_workflow = create_rfe_investigation_workflow()
