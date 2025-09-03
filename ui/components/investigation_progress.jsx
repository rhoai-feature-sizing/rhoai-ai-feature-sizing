import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { 
  MessageSquare, 
  Users, 
  FileText, 
  CheckCircle, 
  Loader2,
  Brain,
  Clock
} from "lucide-react";
import { useEffect, useState } from "react";

const STAGE_META = {
  starting: {
    icon: Loader2,
    title: "Starting Investigation",
    gradient: "from-blue-100 via-blue-50 to-white",
    iconBg: "bg-blue-100 text-blue-600",
    badge: "bg-blue-100 text-blue-700",
    progress: 10
  },
  analyzing: {
    icon: Brain,
    title: "Agent Analysis",
    gradient: "from-purple-100 via-purple-50 to-white",
    iconBg: "bg-purple-100 text-purple-600", 
    badge: "bg-purple-100 text-purple-700",
    progress: 30
  },
  // New detailed agent reasoning stages
  agent_analysis: {
    icon: Brain,
    title: "Agent Starting Analysis",
    gradient: "from-purple-100 via-purple-50 to-white",
    iconBg: "bg-purple-100 text-purple-600",
    badge: "bg-purple-100 text-purple-700",
    progress: 25
  },
  retrieving_knowledge: {
    icon: Brain,
    title: "Retrieving Knowledge",
    gradient: "from-indigo-100 via-indigo-50 to-white",
    iconBg: "bg-indigo-100 text-indigo-600",
    badge: "bg-indigo-100 text-indigo-700",
    progress: 30
  },
  processing_knowledge: {
    icon: Brain,
    title: "Processing Knowledge",
    gradient: "from-purple-100 via-purple-50 to-white",
    iconBg: "bg-purple-100 text-purple-600",
    badge: "bg-purple-100 text-purple-700",
    progress: 35
  },
  knowledge_fallback: {
    icon: Brain,
    title: "Using General Knowledge",
    gradient: "from-yellow-100 via-yellow-50 to-white",
    iconBg: "bg-yellow-100 text-yellow-600",
    badge: "bg-yellow-100 text-yellow-700",
    progress: 32
  },
  llm_reasoning: {
    icon: Brain,
    title: "Agent Reasoning",
    gradient: "from-purple-100 via-purple-50 to-white",
    iconBg: "bg-purple-100 text-purple-600",
    badge: "bg-purple-100 text-purple-700",
    progress: 40
  },
  reasoning_stream: {
    icon: Brain,
    title: "Agent Thinking",
    gradient: "from-indigo-100 via-indigo-50 to-white",
    iconBg: "bg-indigo-100 text-indigo-600",
    badge: "bg-indigo-100 text-indigo-700",
    progress: 42
  },
  streaming_analysis: {
    icon: Brain,
    title: "Streaming Analysis",
    gradient: "from-purple-100 via-purple-50 to-white",
    iconBg: "bg-purple-100 text-purple-600",
    badge: "bg-purple-100 text-purple-700",
    progress: 40
  },
  structuring_analysis: {
    icon: Brain,
    title: "Structuring Analysis",
    gradient: "from-violet-100 via-violet-50 to-white",
    iconBg: "bg-violet-100 text-violet-600",
    badge: "bg-violet-100 text-violet-700",
    progress: 45
  },
  llm_fallback: {
    icon: Brain,
    title: "Using Fallback Approach",
    gradient: "from-amber-100 via-amber-50 to-white",
    iconBg: "bg-amber-100 text-amber-600",
    badge: "bg-amber-100 text-amber-700",
    progress: 42
  },
  analysis_complete: {
    icon: CheckCircle,
    title: "Analysis Complete",
    gradient: "from-green-100 via-green-50 to-white",
    iconBg: "bg-green-100 text-green-600",
    badge: "bg-green-100 text-green-700",
    progress: 45
  },
  analysis_error: {
    icon: Brain,
    title: "Analysis Error",
    gradient: "from-red-100 via-red-50 to-white",
    iconBg: "bg-red-100 text-red-600",
    badge: "bg-red-100 text-red-700",
    progress: 30
  },
  generating_questions: {
    icon: Brain,
    title: "Generating Questions",
    gradient: "from-cyan-100 via-cyan-50 to-white",
    iconBg: "bg-cyan-100 text-cyan-600",
    badge: "bg-cyan-100 text-cyan-700",
    progress: 60
  },
  questions_generated: {
    icon: CheckCircle,
    title: "Questions Ready",
    gradient: "from-green-100 via-green-50 to-white",
    iconBg: "bg-green-100 text-green-600",
    badge: "bg-green-100 text-green-700",
    progress: 65
  },
  assessing: {
    icon: Brain,
    title: "Assessing Completeness",
    gradient: "from-teal-100 via-teal-50 to-white",
    iconBg: "bg-teal-100 text-teal-600",
    badge: "bg-teal-100 text-teal-700",
    progress: 75
  },
  creating_rfe: {
    icon: FileText,
    title: "Creating RFE Document",
    gradient: "from-violet-100 via-violet-50 to-white",
    iconBg: "bg-violet-100 text-violet-600",
    badge: "bg-violet-100 text-violet-700",
    progress: 85
  },
  waiting_for_user: {
    icon: MessageSquare,
    title: "Your Turn to Respond",
    gradient: "from-green-100 via-green-50 to-white",
    iconBg: "bg-green-100 text-green-600",
    badge: "bg-green-100 text-green-700",
    progress: 50
  },
  processing: {
    icon: Loader2,
    title: "Processing Response", 
    gradient: "from-orange-100 via-orange-50 to-white",
    iconBg: "bg-orange-100 text-orange-600",
    badge: "bg-orange-100 text-orange-700", 
    progress: 70
  },
  finalizing: {
    icon: FileText,
    title: "Finalizing RFE",
    gradient: "from-violet-100 via-violet-50 to-white",
    iconBg: "bg-violet-100 text-violet-600",
    badge: "bg-violet-100 text-violet-700",
    progress: 90
  },
  refining: {
    icon: FileText,
    title: "Refining RFE",
    gradient: "from-orange-100 via-orange-50 to-white",
    iconBg: "bg-orange-100 text-orange-600",
    badge: "bg-orange-100 text-orange-700",
    progress: 80
  },
  completed: {
    icon: CheckCircle,
    title: "Investigation Complete",
    gradient: "from-emerald-100 via-emerald-50 to-white",
    iconBg: "bg-emerald-100 text-emerald-600",
    badge: "bg-emerald-100 text-emerald-700",
    progress: 100
  }
};

function InvestigationProgressCard({ event }) {
  const [visible, setVisible] = useState(true);
  
  useEffect(() => {
    if (event?.stage === "completed") {
      // Keep visible for a while to show completion
      setTimeout(() => setVisible(false), 5000);
    } else {
      setVisible(true);
    }
  }, [event?.stage]);

  if (!event || !visible) return null;

  const { stage, description, agent_persona, streaming_type } = event;
  const meta = STAGE_META[stage] || STAGE_META.starting;
  
  const isAnimating = stage === "analyzing" || stage === "processing" || stage === "starting" ||
    stage === "agent_analysis" || stage === "retrieving_knowledge" || stage === "processing_knowledge" ||
    stage === "llm_reasoning" || stage === "reasoning_stream" || stage === "streaming_analysis" ||
    stage === "structuring_analysis" || stage === "llm_fallback" || stage === "generating_questions" || 
    stage === "assessing" || stage === "creating_rfe" || stage === "refining";

  return (
    <div className="flex min-h-[180px] w-full items-center justify-center py-2">
      <Card
        className={cn(
          "w-full rounded-xl shadow-md transition-all duration-500",
          "border-0",
          `bg-gradient-to-br ${meta.gradient}`,
        )}
        style={{
          boxShadow:
            "0 2px 12px 0 rgba(80, 80, 120, 0.08), 0 1px 3px 0 rgba(80, 80, 120, 0.04)",
        }}
      >
        <CardHeader className="flex flex-row items-center gap-3 px-4 pb-2 pt-3">
          <div className={cn("flex items-center justify-center rounded-full p-2", meta.iconBg)}>
            <meta.icon className={cn("h-5 w-5", isAnimating && "animate-spin")} />
          </div>
          <div className="flex-1">
            <CardTitle className="flex items-center gap-2 text-base font-semibold">
              {meta.title}
              <Badge className={cn("ml-1", meta.badge, "px-2 py-0.5 text-xs")}>
                {meta.progress}% Complete
              </Badge>
            </CardTitle>
          </div>
        </CardHeader>
        
        <CardContent className="px-4 py-2">
          <div className="space-y-3">
            {/* Agent information */}
            {agent_persona && (
              <div className="flex items-center gap-2">
                <Users className="h-3 w-3 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">
                  Agent: {agent_persona}
                </span>
                {streaming_type && (
                  <Badge variant="outline" className="text-xs animate-pulse">
                    {streaming_type === 'reasoning' ? '🧠 Thinking' : '✍️ Writing'}
                  </Badge>
                )}
              </div>
            )}

            {/* Stage description */}
            <div className="text-sm text-gray-600">
              {description || getDefaultDescription(stage)}
            </div>

            {/* Special content for waiting stage */}
            {stage === "waiting_for_user" && (
              <div className="flex items-center gap-2 p-2 bg-green-50 rounded-lg border border-green-200">
                <Clock className="h-4 w-4 text-green-600" />
                <div className="text-sm text-green-800">
                  Please respond to the agent's questions to continue refining your RFE.
                </div>
              </div>
            )}

            {/* Progress indicator */}
            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-500">Investigation Progress</span>
                <span className="font-medium">{meta.progress}%</span>
              </div>
              <Progress
                value={meta.progress}
                className="h-1.5 rounded-full bg-gray-200"
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function getDefaultDescription(stage) {
  switch (stage) {
    case "starting":
      return "Initializing RFE investigation with AI agents...";
    case "analyzing": 
      return "Agent is analyzing your idea and preparing questions...";
    case "agent_analysis":
      return "Agent is beginning detailed analysis of your RFE idea...";
    case "retrieving_knowledge":
      return "Agent is searching through knowledge base for relevant information...";
    case "processing_knowledge":
      return "Agent is processing retrieved documents and extracting insights...";
    case "knowledge_fallback":
      return "Agent is proceeding with general knowledge (knowledge base unavailable)...";
    case "llm_reasoning":
      return "Agent is reasoning through requirements and generating insights...";
    case "reasoning_stream":
      return "Agent is thinking out loud and working through the analysis step by step...";
    case "streaming_analysis":
      return "Agent is performing structured analysis with real-time insights...";
    case "structuring_analysis":
      return "Agent is organizing insights into structured analysis format...";
    case "llm_fallback":
      return "Agent is using an alternative approach to complete the analysis...";
    case "analysis_complete":
      return "Agent has completed analysis and determined complexity level...";
    case "analysis_error":
      return "Agent encountered an error during analysis, falling back to manual review...";
    case "generating_questions":
      return "Agent is analyzing conversation gaps and generating follow-up questions...";
    case "questions_generated":
      return "Agent has prepared follow-up questions to refine your RFE...";
    case "assessing":
      return "Agent is assessing if we have enough information for the RFE document...";
    case "creating_rfe":
      return "Agent is writing the comprehensive RFE document...";
    case "waiting_for_user":
      return "Waiting for your response to continue the investigation...";
    case "processing":
      return "Processing your response and updating the RFE draft..."; 
    case "finalizing":
      return "Creating the final RFE document...";
    case "refining":
      return "Agent is refining the RFE document based on your feedback...";
    case "completed":
      return "RFE investigation complete! You can now generate artifacts or continue refining.";
    default:
      return "Processing your request...";
  }
}

export default function Component({ events }) {
  const aggregateEvents = () => {
    if (!events || events.length === 0) return null;
    
    // LlamaIndex server pre-processes events for us - they come as direct data objects
    const normalizedEvents = events.map(e => {
      // Check if this is investigation progress data directly
      if (e && typeof e === 'object' && (e.stage || e.agent_persona)) {
        return {
          type: 'investigation_progress',
          data: e
        };
      }
      return e;  // Return as-is
    });
    
    const investigationEvents = normalizedEvents.filter(e => e.type === 'investigation_progress');
    return investigationEvents[investigationEvents.length - 1]?.data;
  };

  const event = aggregateEvents();

  return <InvestigationProgressCard event={event} />;
}
