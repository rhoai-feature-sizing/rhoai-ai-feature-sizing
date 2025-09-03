import yaml
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional

from pydantic import BaseModel, Field
from llama_index.core import VectorStoreIndex
from llama_index.core.storage import StorageContext
from llama_index.core.indices import load_index_from_storage
from llama_index.core.settings import Settings
from llama_index.core.prompts import PromptTemplate

from src.prompts import get_prompt, PROMPT_NAMES


# Pydantic models for structured outputs
class RFEAnalysis(BaseModel):
    """Structure for agent RFE analysis output"""

    analysis: str = Field(
        description="Detailed analysis of the RFE from the agent's perspective"
    )
    persona: str = Field(description="The agent persona that performed this analysis")
    estimatedComplexity: str = Field(
        description="Complexity estimate: LOW, MEDIUM, HIGH, or UNKNOWN"
    )
    concerns: List[str] = Field(description="List of concerns or risks identified")
    recommendations: List[str] = Field(
        description="List of recommendations for implementation"
    )
    requiredComponents: List[str] = Field(
        description="List of required components or systems"
    )


class Synthesis(BaseModel):
    """Structure for synthesized multi-agent analysis"""

    overallComplexity: str = Field(
        description="Overall complexity assessment: LOW, MEDIUM, HIGH, or UNKNOWN"
    )
    consensusRecommendations: List[str] = Field(
        description="Agreed-upon recommendations from all agents"
    )
    criticalRisks: List[str] = Field(
        description="Critical risks identified across agents"
    )
    requiredCapabilities: List[str] = Field(
        description="Required capabilities or skills needed"
    )
    estimatedTimeline: str = Field(description="Estimated timeline for implementation")
    synthesis: str = Field(
        description="Overall synthesis and summary of all agent inputs"
    )


class ComponentTeam(BaseModel):
    """Structure for a component team definition"""

    teamName: str = Field(description="Name of the component team")
    components: List[str] = Field(
        description="List of components this team is responsible for"
    )
    responsibilities: List[str] = Field(
        description="List of responsibilities for this team"
    )
    epicTitle: str = Field(description="Title of the epic for this team")
    epicDescription: str = Field(description="Description of the epic for this team")


class ComponentTeamsList(BaseModel):
    """Structure for list of component teams"""

    teams: List[ComponentTeam] = Field(
        description="List of component teams with their responsibilities"
    )


class Architecture(BaseModel):
    """Structure for architecture diagram output"""

    type: str = Field(
        description="Type of architecture diagram (e.g., 'system', 'component', 'flow')"
    )
    mermaidCode: str = Field(description="Mermaid diagram code for the architecture")
    description: str = Field(description="Description of the architecture")
    components: List[str] = Field(description="List of architectural components")
    integrations: List[str] = Field(
        description="List of system integrations or connections"
    )


class RFEAgentManager:
    """Manages multi-agent RFE analysis"""

    def __init__(self):
        self.indices: Dict[str, VectorStoreIndex] = {}
        self.agent_configs: Dict[str, Dict] = {}
        self.load_agent_configurations()

    def load_agent_configurations(self):
        """Load agent configs from YAML files"""
        # Get agents directory relative to this file's location
        agents_dir = Path(__file__).parent / "agents"

        if not agents_dir.exists():
            print(f"Warning: Agents directory not found at {agents_dir}")
            return

        for yaml_file in agents_dir.glob("*.yaml"):
            if yaml_file.name.startswith("agent-schema"):
                continue

            try:
                with open(yaml_file, "r") as f:
                    config = yaml.safe_load(f)

                persona = config.get("persona")
                if persona:
                    self.agent_configs[persona] = config
                    print(f"✅ Loaded agent config: {persona}")
            except Exception as e:
                print(f"❌ Error loading {yaml_file}: {e}")

    async def get_agent_index(self, persona: str) -> Optional[VectorStoreIndex]:
        """Get or load index for agent persona"""
        if persona in self.indices:
            return self.indices[persona]

        # Try to load from Python RAG storage first
        storage_dir = Path(f"../output/python-rag/{persona.lower()}")
        if storage_dir.exists():
            try:
                storage_context = StorageContext.from_defaults(
                    persist_dir=str(storage_dir)
                )
                index = load_index_from_storage(storage_context)
                self.indices[persona] = index
                print(f"🐍 Loaded Python index for {persona}")
                return index
            except Exception as e:
                print(f"❌ Failed to load Python index for {persona}: {e}")

        # Fallback to LlamaCloud storage
        llamacloud_dir = Path(f"../output/llamacloud/{persona.lower()}")
        if llamacloud_dir.exists():
            try:
                storage_context = StorageContext.from_defaults(
                    persist_dir=str(llamacloud_dir)
                )
                index = load_index_from_storage(storage_context)
                self.indices[persona] = index
                print(f"☁️ Loaded LlamaCloud index for {persona}")
                return index
            except Exception as e:
                print(f"❌ Failed to load LlamaCloud index for {persona}: {e}")

        print(f"⚠️  No index found for {persona}")
        return None

    async def analyze_rfe(
        self, persona: str, rfe_description: str, config: Dict, ctx=None
    ) -> Dict[str, Any]:
        """Analyze RFE with specific agent persona"""
        print(f"🔍 {persona} analyzing RFE...")

        # Stream UI event for agent analysis start
        if ctx:
            from src.rfe_investigation_workflow import InvestigationUIEventData
            from llama_index.core.chat_ui.events import UIEvent

            ctx.write_event_to_stream(
                UIEvent(
                    type="investigation_progress",
                    data=InvestigationUIEventData(
                        stage="agent_analysis",
                        description=f"🤖 {persona} is analyzing your RFE...",
                        agent_persona=persona,
                        streaming_type="reasoning",
                    ),
                )
            )

        # Get relevant context from agent's knowledge base
        if ctx:
            ctx.write_event_to_stream(
                UIEvent(
                    type="investigation_progress",
                    data=InvestigationUIEventData(
                        stage="retrieving_knowledge",
                        description=f"📚 {persona} is retrieving relevant knowledge...",
                        agent_persona=persona,
                        streaming_type="reasoning",
                    ),
                )
            )

        index = await self.get_agent_index(persona)
        context = "No specific knowledge base available."

        if index:
            try:
                retriever = index.as_retriever(similarity_top_k=5)
                nodes = retriever.retrieve(rfe_description)
                if nodes:
                    context = "\n\n".join([node.node.get_content() for node in nodes])
                    print(f"📚 Retrieved {len(nodes)} relevant documents for {persona}")

                    if ctx:
                        ctx.write_event_to_stream(
                            UIEvent(
                                type="investigation_progress",
                                data=InvestigationUIEventData(
                                    stage="processing_knowledge",
                                    description=f"🧠 {persona} found {len(nodes)} relevant documents and is processing insights...",
                                    agent_persona=persona,
                                    streaming_type="reasoning",
                                ),
                            )
                        )
            except Exception as e:
                print(f"❌ Error retrieving context for {persona}: {e}")
                if ctx:
                    ctx.write_event_to_stream(
                        UIEvent(
                            type="investigation_progress",
                            data=InvestigationUIEventData(
                                stage="knowledge_fallback",
                                description=f"⚠️ {persona} proceeding with general knowledge (knowledge base unavailable)",
                                agent_persona=persona,
                                streaming_type="reasoning",
                            ),
                        )
                    )

        # Use the persona's analysis prompt or fallback
        analysis_prompt_config = config.get("analysisPrompt", {})
        if analysis_prompt_config and "template" in analysis_prompt_config:
            # Use the agent's custom prompt template
            template = analysis_prompt_config["template"]
            prompt = template.replace("{rfe_description}", rfe_description).replace(
                "{context}", context
            )
        else:
            # Use fallback prompt
            prompt = get_prompt(
                PROMPT_NAMES.AGENT_ANALYSIS,
                {
                    "rfe_description": rfe_description,
                    "context": context,
                    "persona": config.get("name", persona),
                },
            )

        # Stream UI event for LLM analysis
        if ctx:
            ctx.write_event_to_stream(
                UIEvent(
                    type="investigation_progress",
                    data=InvestigationUIEventData(
                        stage="llm_reasoning",
                        description=f"🧠 {persona} is analyzing requirements and generating insights...",
                        agent_persona=persona,
                        streaming_type="reasoning",
                    ),
                )
            )

        print(f"🧠 {persona} starting LLM analysis...")
        print(f"🧠 LLM model: {Settings.llm.model}")
        print(f"🧠 LLM streaming: {getattr(Settings.llm, 'streaming', 'unknown')}")
        print(f"🧠 Analysis prompt config: {analysis_prompt_config}")
        print(f"🧠 RFE description length: {len(rfe_description)}")
        print(f"🧠 Context length: {len(context)}")

        try:
            # Single Phase: Streaming Structured Prediction - Stream the analysis directly
            if ctx:
                ctx.write_event_to_stream(
                    UIEvent(
                        type="investigation_progress",
                        data=InvestigationUIEventData(
                            stage="streaming_analysis",
                            description=f"🧠 {persona} is analyzing and streaming insights...",
                            agent_persona=persona,
                            streaming_type="reasoning",
                        ),
                    )
                )

            # Create the analysis prompt (use custom template if available, otherwise fallback)
            if analysis_prompt_config and "template" in analysis_prompt_config:
                print(f"🧠 {persona} using custom structured streaming template")
                analysis_template = PromptTemplate(analysis_prompt_config["template"])
                template_vars = {
                    "rfe_description": rfe_description,
                    "context": context,
                    "persona": persona,
                }
            else:
                print(f"🧠 {persona} using fallback structured streaming template")
                fallback_template = f"""
                As a {persona} expert, analyze this RFE and provide your insights.
                
                RFE: {rfe_description}
                Context: {context}
                
                Think through this step by step and provide a structured analysis covering:
                - Your detailed technical analysis from a {persona} perspective
                - Complexity assessment (LOW/MEDIUM/HIGH/UNKNOWN) 
                - Main concerns or risks you identify
                - Your recommendations for implementation
                - Required components or systems needed
                
                Be thorough in your analysis and reasoning.
                """
                analysis_template = PromptTemplate(fallback_template)
                template_vars = {}

            print(f"🧠 {persona} starting streaming structured prediction...")

            # Track reasoning text for UI display
            reasoning_text = ""

            try:
                # Use streaming structured prediction directly

                testllm = await Settings.llm.apredict(
                    analysis_template, **template_vars
                )
                print(f"🧠 {persona} streaming structured analysis: {testllm}")

                stream_output = await Settings.llm.astream_structured_predict(
                    RFEAnalysis, analysis_template, **template_vars
                )

                response = None
                partial_count = 0

                print(f"🧠 {persona} streaming structured analysis started")

                # Iterate through partial outputs
                async for partial_output in stream_output:
                    partial_count += 1
                    print(
                        f"🧠 {persona} partial {partial_count}: {type(partial_output)}"
                    )

                    # Build reasoning text from partial outputs
                    if hasattr(partial_output, "analysis") and partial_output.analysis:
                        # Use the analysis field as our reasoning text
                        current_text = partial_output.analysis
                        if current_text != reasoning_text:  # Only update if changed
                            reasoning_text = current_text
                            print(
                                f"🧠 {persona} updated reasoning text length: {len(reasoning_text)}"
                            )

                            # Send UI updates with current analysis text
                            if ctx:
                                ctx.write_event_to_stream(
                                    UIEvent(
                                        type="reasoning_text_stream",
                                        data={
                                            "agent_persona": persona,
                                            "current_text": reasoning_text,
                                            "is_complete": False,
                                        },
                                    )
                                )

                    # Store the latest partial as final (will be most complete)
                    response = partial_output

                print(f"🧠 {persona} received {partial_count} partial outputs total")
                print(f"🧠 {persona} streaming structured prediction completed")

                # Send final reasoning text
                if ctx:
                    ctx.write_event_to_stream(
                        UIEvent(
                            type="reasoning_text_stream",
                            data={
                                "agent_persona": persona,
                                "current_text": reasoning_text,
                                "is_complete": True,
                            },
                        )
                    )

            except Exception as e:
                print(f"🧠 {persona} streaming structured prediction failed: {e}")

                # Fallback to regular structured prediction
                if ctx:
                    ctx.write_event_to_stream(
                        UIEvent(
                            type="investigation_progress",
                            data=InvestigationUIEventData(
                                stage="llm_fallback",
                                description=f"⏰ {persona} using non-streaming structured analysis...",
                                agent_persona=persona,
                                streaming_type="reasoning",
                            ),
                        )
                    )

                # Create non-streaming LLM for fallback
                from llama_index.llms.openai import OpenAI
                import os

                fallback_llm = OpenAI(
                    model="gpt-4",
                    temperature=0.1,
                    api_key=os.getenv("OPENAI_API_KEY"),
                    streaming=False,
                )

                response = await fallback_llm.astructured_predict(
                    RFEAnalysis, analysis_template, **template_vars
                )

                # Generate some reasoning text for UI
                reasoning_text = f"Analysis completed using {persona} expertise. Complexity assessment: {getattr(response, 'estimatedComplexity', 'UNKNOWN')}"

                # Send reasoning text to UI
                if ctx:
                    ctx.write_event_to_stream(
                        UIEvent(
                            type="reasoning_text_stream",
                            data={
                                "agent_persona": persona,
                                "current_text": reasoning_text,
                                "is_complete": True,
                            },
                        )
                    )

            print(f"🧠 {persona} completed analysis")
            print(f"🧠 Reasoning captured: {len(reasoning_text)} characters")

            # Ensure persona is set correctly
            if response:
                response.persona = persona

        except Exception as e:
            print(f"❌ Error during {persona} streaming analysis: {e}")

            # Fallback to simple structured prediction on error
            if ctx:
                ctx.write_event_to_stream(
                    UIEvent(
                        type="investigation_progress",
                        data=InvestigationUIEventData(
                            stage="llm_fallback",
                            description=f"⚠️ {persona} switching to fallback analysis due to error...",
                            agent_persona=persona,
                            streaming_type="reasoning",
                        ),
                    )
                )

            # Simple fallback response
            response = RFEAnalysis(
                analysis=f"Basic analysis completed for {persona}. Error occurred during detailed reasoning: {str(e)}",
                persona=persona,
                estimatedComplexity="MEDIUM",
                concerns=["Detailed analysis unavailable due to technical issue"],
                recommendations=["Manual review recommended"],
                requiredComponents=["To be determined"],
            )
            print(f"🧠 {persona} created fallback response due to error")
            if ctx:
                ctx.write_event_to_stream(
                    UIEvent(
                        type="investigation_progress",
                        data=InvestigationUIEventData(
                            stage="analysis_complete",
                            description=f"✅ {persona} completed analysis with complexity: {response.estimatedComplexity}",
                            agent_persona=persona,
                            streaming_type="reasoning",
                        ),
                    )
                )

            print(f"✅ {persona} analysis complete")
            # Convert Pydantic model to dict for backward compatibility
            return response.model_dump()

        except Exception as e:
            print(f"❌ Error generating analysis for {persona}: {e}")

            # Stream error event
            if ctx:
                ctx.write_event_to_stream(
                    UIEvent(
                        type="investigation_progress",
                        data=InvestigationUIEventData(
                            stage="analysis_error",
                            description=f"❌ {persona} encountered an error during analysis: {str(e)}",
                            agent_persona=persona,
                            streaming_type="reasoning",
                        ),
                    )
                )

            # Return structured fallback using the Pydantic model
            fallback = RFEAnalysis(
                analysis=f"Error during analysis: {str(e)}",
                persona=persona,
                estimatedComplexity="UNKNOWN",
                concerns=[f"Analysis failed: {str(e)}"],
                recommendations=["Manual review required"],
                requiredComponents=[],
            )
            return fallback.model_dump()

    async def synthesize_analyses(self, analyses: List[Dict]) -> Dict[str, Any]:
        """Synthesize multiple agent analyses"""
        print("🔄 Synthesizing agent analyses...")

        # Format analyses for synthesis
        analyses_text = "\n\n".join(
            [
                f"**{a['persona']}:**\n"
                f"Analysis: {a.get('analysis', 'No analysis')}\n"
                f"Complexity: {a.get('estimatedComplexity', 'UNKNOWN')}\n"
                f"Concerns: {', '.join(a.get('concerns', []))}\n"
                f"Recommendations: {', '.join(a.get('recommendations', []))}"
                for a in analyses
            ]
        )

        # Use synthesis prompt
        synthesis_prompt = get_prompt(
            PROMPT_NAMES.SYNTHESIS,
            {
                "rfe_description": analyses[0].get("rfe_description", "RFE analysis"),
                "agent_analyses": analyses_text,
            },
        )

        try:
            # Create PromptTemplate for structured prediction
            prompt_template = PromptTemplate(synthesis_prompt)
            response = await Settings.llm.astructured_predict(
                Synthesis, prompt_template
            )

            print("✅ Synthesis complete")
            return response.model_dump()

        except Exception as e:
            print(f"❌ Synthesis error: {e}")
            # Return structured fallback using the Pydantic model
            fallback = Synthesis(
                overallComplexity="UNKNOWN",
                consensusRecommendations=[],
                criticalRisks=[f"Analysis error: {str(e)}"],
                requiredCapabilities=[],
                estimatedTimeline="Unknown",
                synthesis=f"Error during synthesis: {str(e)}",
            )
            return fallback.model_dump()

    async def generate_component_teams(self, synthesis: Dict) -> List[Dict]:
        """Generate component teams from synthesis"""
        try:
            prompt = get_prompt(
                PROMPT_NAMES.COMPONENT_TEAMS,
                {
                    "rfe_description": "Feature implementation",
                    "synthesis": json.dumps(synthesis, indent=2),
                    "agent_analyses": "Based on agent recommendations",
                },
            )

            # Create PromptTemplate for structured prediction
            prompt_template = PromptTemplate(prompt)
            response = await Settings.llm.astructured_predict(
                ComponentTeamsList, prompt_template
            )

            # Convert to list of dicts for backward compatibility
            return [team.model_dump() for team in response.teams]

        except Exception as e:
            print(f"❌ Component teams generation error: {e}")
            # Return structured fallback using the Pydantic model
            fallback_team = ComponentTeam(
                teamName="Development Team",
                components=["Implementation"],
                responsibilities=["Feature development"],
                epicTitle="Feature Implementation",
                epicDescription="Implement the requested feature",
            )
            return [fallback_team.model_dump()]

    async def generate_architecture(self, synthesis: Dict) -> Dict:
        """Generate architecture diagram from synthesis"""
        try:
            prompt = get_prompt(
                PROMPT_NAMES.ARCHITECTURE_DIAGRAM,
                {
                    "rfe_description": "System architecture",
                    "synthesis": json.dumps(synthesis, indent=2),
                    "component_teams": "Development teams",
                },
            )

            # Create PromptTemplate for structured prediction
            prompt_template = PromptTemplate(prompt)
            response = await Settings.llm.astructured_predict(
                Architecture, prompt_template
            )

            return response.model_dump()

        except Exception as e:
            print(f"❌ Architecture generation error: {e}")
            # Return structured fallback using the Pydantic model
            fallback = Architecture(
                type="system",
                mermaidCode="graph TD\n    A[User] --> B[System]\n    B --> C[Database]",
                description="Basic system architecture",
                components=[],
                integrations=[],
            )
            return fallback.model_dump()


async def get_agent_personas() -> Dict[str, Dict]:
    """Get all available agent personas"""
    manager = RFEAgentManager()
    return manager.agent_configs
