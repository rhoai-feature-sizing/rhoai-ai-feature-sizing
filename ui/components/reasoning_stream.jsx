import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { Brain, MessageSquare, CheckCircle } from "lucide-react";

function ReasoningStreamCard({ event }) {
  const [displayText, setDisplayText] = useState("");
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (event) {
      setDisplayText(event.current_text || "");
      setIsComplete(event.is_complete || false);
    }
  }, [event]);

  if (!event) return null;

  const { agent_persona } = event;

  return (
    <div className="flex w-full items-start justify-center py-2">
      <Card
        className={cn(
          "w-full rounded-xl shadow-md transition-all duration-500",
          "border-0 bg-gradient-to-br from-slate-50 via-slate-25 to-white",
        )}
        style={{
          boxShadow:
            "0 2px 12px 0 rgba(80, 80, 120, 0.08), 0 1px 3px 0 rgba(80, 80, 120, 0.04)",
        }}
      >
        <CardHeader className="flex flex-row items-center gap-3 px-4 pb-2 pt-3">
          <div className="flex items-center justify-center rounded-full p-2 bg-slate-100 text-slate-600">
            {isComplete ? (
              <CheckCircle className="h-5 w-5" />
            ) : (
              <Brain className="h-5 w-5 animate-pulse" />
            )}
          </div>
          <div className="flex-1">
            <CardTitle className="flex items-center gap-2 text-base font-semibold">
              {isComplete ? "🧠 Agent Reasoning Complete" : "🧠 Agent Thinking..."}
              <Badge className="ml-1 bg-slate-100 text-slate-700 px-2 py-0.5 text-xs">
                {agent_persona}
              </Badge>
              {!isComplete && (
                <Badge className="animate-pulse bg-blue-100 text-blue-700 px-2 py-0.5 text-xs">
                  Streaming
                </Badge>
              )}
            </CardTitle>
          </div>
        </CardHeader>

        <CardContent className="px-4 py-2">
          <div className="space-y-3">
            {/* Reasoning Text Display */}
            <div className="bg-slate-50 rounded-lg border border-slate-200">
              <div className="flex items-center gap-2 px-3 py-2 border-b border-slate-200 bg-slate-100 rounded-t-lg">
                <MessageSquare className="h-4 w-4 text-slate-600" />
                <span className="text-sm font-medium text-slate-700">
                  Agent Reasoning Process
                </span>
                {!isComplete && (
                  <div className="ml-auto flex items-center gap-1">
                    <div className="w-1 h-1 bg-green-500 rounded-full animate-ping"></div>
                    <div className="w-1 h-1 bg-green-500 rounded-full animate-ping delay-75"></div>
                    <div className="w-1 h-1 bg-green-500 rounded-full animate-ping delay-150"></div>
                  </div>
                )}
              </div>
              <ScrollArea className="h-64 w-full">
                <div className="p-4">
                  <pre className="whitespace-pre-wrap text-sm text-slate-700 font-mono leading-relaxed">
                    {displayText}
                    {!isComplete && (
                      <span className="inline-block w-2 h-4 bg-slate-400 animate-pulse ml-1"></span>
                    )}
                  </pre>
                </div>
              </ScrollArea>
            </div>

            {/* Status indicators */}
            <div className="flex items-center justify-between text-xs text-slate-500">
              <div className="flex items-center gap-2">
                <span>Characters: {displayText.length}</span>
                <span>•</span>
                <span>Words: {displayText.split(/\s+/).filter(w => w.length > 0).length}</span>
              </div>
              <div>
                {isComplete ? (
                  <span className="text-green-600 font-medium">✓ Complete</span>
                ) : (
                  <span className="text-blue-600 font-medium animate-pulse">● Streaming...</span>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function Component({ events }) {
  const aggregateEvents = () => {
    if (!events || events.length === 0) return null;

    // LlamaIndex server pre-processes events - look for reasoning_text_stream events
    const reasoningEvents = events.map(e => {
      if (e && typeof e === 'object' && e.agent_persona && e.current_text !== undefined) {
        return {
          type: 'reasoning_text_stream',
          data: e
        };
      }
      return e;
    });

    const streamEvents = reasoningEvents.filter(e => e.type === 'reasoning_text_stream');
    return streamEvents[streamEvents.length - 1]?.data;
  };

  const event = aggregateEvents();

  return <ReasoningStreamCard event={event} />;
}
