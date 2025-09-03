import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { Markdown } from "@llamaindex/chat-ui/widgets";
import { 
  FileText, 
  Workflow, 
  Building2, 
  ListChecks, 
  Edit3,
  Download,
  Copy,
  Check,
  Send
} from "lucide-react";


const ARTIFACT_META = {
  rfe_description: {
    icon: FileText,
    title: "RFE Description",
    color: "bg-blue-50 text-blue-700 border-blue-200",
    description: "Complete RFE specification"
  },
  feature_refinement: {
    icon: Workflow,
    title: "Feature Refinement",
    color: "bg-green-50 text-green-700 border-green-200", 
    description: "Detailed feature breakdown"
  },
  architecture: {
    icon: Building2,
    title: "Architecture",
    color: "bg-purple-50 text-purple-700 border-purple-200",
    description: "System architecture design"
  },
  epics_stories: {
    icon: ListChecks,
    title: "Epics & Stories",
    color: "bg-orange-50 text-orange-700 border-orange-200",
    description: "Development epics and user stories"
  }
};

// Inlined JiraPublisher to comply with import restrictions
const ISSUE_TYPES = [
  { value: "Epic", label: "Epic", icon: "🎯" },
  { value: "Story", label: "Story", icon: "📖" },
  { value: "Task", label: "Task", icon: "✅" },
  { value: "Bug", label: "Bug", icon: "🐛" },
  { value: "Improvement", label: "Improvement", icon: "✨" },
];

const ARTIFACT_TO_ISSUE_TYPE = {
  rfe_description: "Epic",
  feature_refinement: "Story",
  architecture: "Task",
  epics_stories: "Epic",
};

const getStoredJiraConfig = () => {
  try {
    const stored = localStorage.getItem('jiraConfig');
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (e) {
    console.error('Failed to load stored JIRA config:', e);
  }
  return {
    domain: "",
    email: "",
    apiToken: "",
  };
};

const saveJiraConfig = (config) => {
  try {
    localStorage.setItem('jiraConfig', JSON.stringify(config));
  } catch (e) {
    console.error('Failed to save JIRA config:', e);
  }
};

const modalStyles = {
  overlay: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
  },
  content: {
    backgroundColor: "white",
    borderRadius: "8px",
    padding: "24px",
    maxWidth: "525px",
    width: "90%",
    maxHeight: "90vh",
    overflow: "auto",
    boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
  },
  header: {
    marginBottom: "20px",
  },
  title: {
    fontSize: "20px",
    fontWeight: "600",
    marginBottom: "8px",
    color: "#111827",
  },
  description: {
    fontSize: "14px",
    color: "#6B7280",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "16px",
  },
  fieldGroup: {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
  },
  label: {
    fontSize: "14px",
    fontWeight: "500",
    color: "#374151",
  },
  required: {
    color: "#EF4444",
  },
  input: {
    padding: "8px 12px",
    borderRadius: "6px",
    border: "1px solid #D1D5DB",
    fontSize: "14px",
    outline: "none",
    transition: "border-color 0.2s",
  },
  select: {
    padding: "8px 12px",
    borderRadius: "6px",
    border: "1px solid #D1D5DB",
    fontSize: "14px",
    outline: "none",
    backgroundColor: "white",
    cursor: "pointer",
  },
  footer: {
    display: "flex",
    gap: "12px",
    justifyContent: "flex-end",
    marginTop: "24px",
  },
  button: {
    padding: "8px 16px",
    borderRadius: "6px",
    fontSize: "14px",
    fontWeight: "500",
    border: "none",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    gap: "8px",
    transition: "all 0.2s",
  },
  primaryButton: {
    backgroundColor: "#3B82F6",
    color: "white",
  },
  secondaryButton: {
    backgroundColor: "white",
    color: "#374151",
    border: "1px solid #D1D5DB",
  },
  disabledButton: {
    opacity: 0.5,
    cursor: "not-allowed",
  },
  alert: {
    padding: "12px",
    borderRadius: "6px",
    fontSize: "14px",
    display: "flex",
    alignItems: "center",
    gap: "8px",
  },
  errorAlert: {
    backgroundColor: "#FEE2E2",
    color: "#991B1B",
    border: "1px solid #FECACA",
  },
  successAlert: {
    backgroundColor: "#D1FAE5",
    color: "#065F46",
    border: "1px solid #A7F3D0",
  },
  warningAlert: {
    backgroundColor: "#FEF3C7",
    color: "#92400E",
    border: "1px solid #FDE68A",
  },
  labelBadge: {
    display: "inline-block",
    padding: "2px 8px",
    borderRadius: "4px",
    fontSize: "12px",
    backgroundColor: "#F3F4F6",
    color: "#4B5563",
    margin: "2px",
  },
  configSection: {
    backgroundColor: "#F9FAFB",
    border: "1px solid #E5E7EB",
    borderRadius: "6px",
    padding: "12px",
    marginBottom: "16px",
  },
};

function JiraPublisher({ 
  isOpen, 
  onClose, 
  artifactType, 
  artifactTitle,
  content,
  onPublishSuccess,
  jiraDomain,
  jiraEmail,
  jiraApiToken
}) {
  const [publishing, setPublishing] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [formData, setFormData] = useState({
    projectKey: "",
    summary: "",
    issueType: ARTIFACT_TO_ISSUE_TYPE[artifactType] || "Task",
    assignee: "",
    labels: "",
    epicKey: "",
  });
  const [jiraConfig, setJiraConfig] = useState(() => {
    const stored = getStoredJiraConfig();
    return {
      domain: jiraDomain || stored.domain,
      email: jiraEmail || stored.email,
      apiToken: jiraApiToken || stored.apiToken,
    };
  });
  const [saveConfig, setSaveConfig] = useState(false);

  useEffect(() => {
    if (saveConfig && jiraConfig.domain && jiraConfig.email && jiraConfig.apiToken) {
      saveJiraConfig(jiraConfig);
    }
  }, [saveConfig, jiraConfig]);

  useEffect(() => {
    if (isOpen) {
      setFormData({
        projectKey: "",
        summary: artifactTitle || `${artifactType?.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())} Document`,
        issueType: ARTIFACT_TO_ISSUE_TYPE[artifactType] || "Task",
        assignee: "",
        labels: "rfe,ai-generated",
        epicKey: "",
      });
      setError(null);
      setSuccess(null);
    }
  }, [isOpen, artifactType, artifactTitle]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setPublishing(true);
    setError(null);

    if (!jiraConfig.domain || !jiraConfig.email || !jiraConfig.apiToken) {
      setError("JIRA configuration is incomplete. Please provide domain, email, and API token.");
      setPublishing(false);
      return;
    }

    try {
      const descriptionADF = {
        type: "doc",
        version: 1,
        content: [
          {
            type: "paragraph",
            content: [
              {
                type: "text",
                text: content
              }
            ]
          }
        ]
      };

      const payload = {
        fields: {
          project: { key: formData.projectKey },
          summary: formData.summary,
          description: descriptionADF,
          issuetype: { name: formData.issueType },
        }
      };

      if (formData.assignee) {
        payload.fields.assignee = { accountId: formData.assignee };
      }
      
      if (formData.labels) {
        payload.fields.labels = formData.labels.split(",").map(l => l.trim()).filter(Boolean);
      }

      if (formData.epicKey && formData.issueType !== "Epic") {
        payload.fields.parent = { key: formData.epicKey };
      }

      const jiraUrl = `https://${jiraConfig.domain}/rest/api/3/issue`;
      const authToken = btoa(`${jiraConfig.email}:${jiraConfig.apiToken}`);

      const response = await fetch(jiraUrl, {
        method: "POST",
        headers: {
          "Authorization": `Basic ${authToken}`,
          "Accept": "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        const errorMessage = errorData.errors 
          ? Object.entries(errorData.errors).map(([key, value]) => `${key}: ${value}`).join(", ")
          : errorData.errorMessages?.join(", ") || "Failed to create JIRA issue";
        throw new Error(errorMessage);
      }

      const result = await response.json();
      setSuccess({
        key: result.key,
        url: `https://${jiraConfig.domain}/browse/${result.key}`,
      });

      if (onPublishSuccess) {
        onPublishSuccess(result);
      }

      setTimeout(() => {
        onClose();
      }, 3000);

    } catch (err) {
      console.error("JIRA API Error:", err);
      setError(err.message || "An unexpected error occurred");
    } finally {
      setPublishing(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleConfigChange = (field, value) => {
    setJiraConfig(prev => ({ ...prev, [field]: value }));
  };

  if (!isOpen) return null;

  const hasValidConfig = jiraConfig.domain && jiraConfig.email && jiraConfig.apiToken;

  return (
    <div style={modalStyles.overlay} onClick={onClose}>
      <div style={modalStyles.content} onClick={(e) => e.stopPropagation()}>
        <div style={modalStyles.header}>
          <h2 style={modalStyles.title}>Publish to JIRA Cloud</h2>
          <p style={modalStyles.description}>
            Create a JIRA issue from this {artifactType?.replace(/_/g, " ")} artifact.
          </p>
        </div>

        <form onSubmit={handleSubmit} style={modalStyles.form}>
          {!hasValidConfig && (
            <div style={modalStyles.configSection}>
              <h3 style={{ ...modalStyles.label, marginBottom: "12px" }}>
                JIRA Configuration Required
              </h3>
              
              <div style={modalStyles.fieldGroup}>
                <label htmlFor="jiraDomain" style={modalStyles.label}>
                  JIRA Domain <span style={modalStyles.required}>*</span>
                </label>
                <input
                  id="jiraDomain"
                  type="text"
                  placeholder="your-domain.atlassian.net"
                  value={jiraConfig.domain}
                  onChange={(e) => handleConfigChange("domain", e.target.value)}
                  style={modalStyles.input}
                />
              </div>

              <div style={{ ...modalStyles.fieldGroup, marginTop: "12px" }}>
                <label htmlFor="jiraEmail" style={modalStyles.label}>
                  Email <span style={modalStyles.required}>*</span>
                </label>
                <input
                  id="jiraEmail"
                  type="email"
                  placeholder="your-email@example.com"
                  value={jiraConfig.email}
                  onChange={(e) => handleConfigChange("email", e.target.value)}
                  style={modalStyles.input}
                />
              </div>

              <div style={{ ...modalStyles.fieldGroup, marginTop: "12px" }}>
                <label htmlFor="jiraApiToken" style={modalStyles.label}>
                  API Token <span style={modalStyles.required}>*</span>
                </label>
                <input
                  id="jiraApiToken"
                  type="password"
                  placeholder="Your JIRA API token"
                  value={jiraConfig.apiToken}
                  onChange={(e) => handleConfigChange("apiToken", e.target.value)}
                  style={modalStyles.input}
                />
                <p style={{ fontSize: "12px", color: "#6B7280", marginTop: "4px" }}>
                  Generate an API token at: <a href="https://id.atlassian.com/manage-profile/security/api-tokens" target="_blank" rel="noopener noreferrer" style={{ color: "#3B82F6" }}>Atlassian Account Settings</a>
                </p>
              </div>

              <div style={{ marginTop: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
                <input
                  id="saveConfig"
                  type="checkbox"
                  checked={saveConfig}
                  onChange={(e) => setSaveConfig(e.target.checked)}
                  style={{ cursor: "pointer" }}
                />
                <label htmlFor="saveConfig" style={{ ...modalStyles.label, margin: 0, cursor: "pointer" }}>
                  Save configuration for future use
                </label>
              </div>
              
              {getStoredJiraConfig().domain && (
                <div style={{ marginTop: "8px" }}>
                  <button
                    type="button"
                    onClick={() => {
                      localStorage.removeItem('jiraConfig');
                      setJiraConfig({ domain: "", email: "", apiToken: "" });
                      setSaveConfig(false);
                    }}
                    style={{
                      fontSize: "12px",
                      color: "#DC2626",
                      background: "none",
                      border: "none",
                      cursor: "pointer",
                      textDecoration: "underline",
                    }}
                  >
                    Clear saved configuration
                  </button>
                </div>
              )}
            </div>
          )}

          {!hasValidConfig && (
            <div style={{ ...modalStyles.alert, ...modalStyles.warningAlert }}>
              <span>⚠️</span>
              <span>Please configure JIRA settings above before creating issues.</span>
            </div>
          )}

          <div style={modalStyles.fieldGroup}>
            <label htmlFor="projectKey" style={modalStyles.label}>
              Project Key <span style={modalStyles.required}>*</span>
            </label>
            <input
              id="projectKey"
              type="text"
              placeholder="e.g., PROJ, DEV, RHOAI"
              value={formData.projectKey}
              onChange={(e) => handleInputChange("projectKey", e.target.value.toUpperCase())}
              required
              disabled={publishing || success || !hasValidConfig}
              style={{
                ...modalStyles.input,
                ...(publishing || success || !hasValidConfig ? { opacity: 0.5, cursor: "not-allowed" } : {})
              }}
            />
          </div>

          <div style={modalStyles.fieldGroup}>
            <label htmlFor="summary" style={modalStyles.label}>
              Summary <span style={modalStyles.required}>*</span>
            </label>
            <input
              id="summary"
              type="text"
              placeholder="Brief description of the issue"
              value={formData.summary}
              onChange={(e) => handleInputChange("summary", e.target.value)}
              required
              disabled={publishing || success || !hasValidConfig}
              style={{
                ...modalStyles.input,
                ...(publishing || success || !hasValidConfig ? { opacity: 0.5, cursor: "not-allowed" } : {})
              }}
            />
          </div>

          <div style={modalStyles.fieldGroup}>
            <label htmlFor="issueType" style={modalStyles.label}>
              Issue Type <span style={modalStyles.required}>*</span>
            </label>
            <select
              id="issueType"
              value={formData.issueType}
              onChange={(e) => handleInputChange("issueType", e.target.value)}
              disabled={publishing || success || !hasValidConfig}
              style={{
                ...modalStyles.select,
                ...(publishing || success || !hasValidConfig ? { opacity: 0.5, cursor: "not-allowed" } : {})
              }}
            >
              {ISSUE_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.icon} {type.label}
                </option>
              ))}
            </select>
          </div>

          {formData.issueType !== "Epic" && (
            <div style={modalStyles.fieldGroup}>
              <label htmlFor="epicKey" style={modalStyles.label}>
                Epic Key
                <span style={{ ...modalStyles.label, color: "#6B7280", marginLeft: "8px" }}>
                  (optional)
                </span>
              </label>
              <input
                id="epicKey"
                type="text"
                placeholder="e.g., PROJ-123"
                value={formData.epicKey}
                onChange={(e) => handleInputChange("epicKey", e.target.value.toUpperCase())}
                disabled={publishing || success || !hasValidConfig}
                style={{
                  ...modalStyles.input,
                  ...(publishing || success || !hasValidConfig ? { opacity: 0.5, cursor: "not-allowed" } : {})
                }}
              />
            </div>
          )}

          <div style={modalStyles.fieldGroup}>
            <label htmlFor="assignee" style={modalStyles.label}>
              Assignee Account ID
              <span style={{ ...modalStyles.label, color: "#6B7280", marginLeft: "8px" }}>
                (optional)
              </span>
            </label>
            <input
              id="assignee"
              type="text"
              placeholder="JIRA account ID (e.g., 5a1b2c3d-4e5f-6789-0abc-def123456789)"
              value={formData.assignee}
              onChange={(e) => handleInputChange("assignee", e.target.value)}
              disabled={publishing || success || !hasValidConfig}
              style={{
                ...modalStyles.input,
                ...(publishing || success || !hasValidConfig ? { opacity: 0.5, cursor: "not-allowed" } : {})
              }}
            />
            <p style={{ fontSize: "12px", color: "#6B7280", marginTop: "4px" }}>
              Note: For JIRA Cloud, use the account ID, not email. You can find account IDs in JIRA user profiles.
            </p>
          </div>

          <div style={modalStyles.fieldGroup}>
            <label htmlFor="labels" style={modalStyles.label}>
              Labels
              <span style={{ ...modalStyles.label, color: "#6B7280", marginLeft: "8px" }}>
                (comma-separated)
              </span>
            </label>
            <input
              id="labels"
              type="text"
              placeholder="rfe, ai-generated, frontend"
              value={formData.labels}
              onChange={(e) => handleInputChange("labels", e.target.value)}
              disabled={publishing || success || !hasValidConfig}
              style={{
                ...modalStyles.input,
                ...(publishing || success || !hasValidConfig ? { opacity: 0.5, cursor: "not-allowed" } : {})
              }}
            />
            <div style={{ display: "flex", flexWrap: "wrap", gap: "4px", marginTop: "4px" }}>
              {formData.labels.split(",").map((label, idx) => {
                const trimmed = label.trim();
                return trimmed ? (
                  <span key={idx} style={modalStyles.labelBadge}>
                    {trimmed}
                  </span>
                ) : null;
              })}
            </div>
          </div>

          {error && (
            <div style={{ ...modalStyles.alert, ...modalStyles.errorAlert }}>
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div style={{ ...modalStyles.alert, ...modalStyles.successAlert }}>
              <span>✅</span>
              <span style={{ flex: 1 }}>Issue created successfully: {success.key}</span>
              <button
                type="button"
                onClick={() => window.open(success.url, "_blank")}
                style={{
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  padding: "4px",
                  color: "#065F46",
                }}
              >
                🔗
              </button>
            </div>
          )}
        </form>

        <div style={modalStyles.footer}>
          <button
            type="button"
            onClick={onClose}
            disabled={publishing}
            style={{
              ...modalStyles.button,
              ...modalStyles.secondaryButton,
              ...(publishing ? modalStyles.disabledButton : {}),
            }}
          >
            Cancel
          </button>
          <button
            type="submit"
            onClick={handleSubmit}
            disabled={publishing || !formData.projectKey || !formData.summary || success || !hasValidConfig}
            style={{
              ...modalStyles.button,
              ...modalStyles.primaryButton,
              ...(publishing || !formData.projectKey || !formData.summary || success || !hasValidConfig 
                ? modalStyles.disabledButton 
                : {}),
            }}
          >
            {publishing ? (
              <>
                <span style={{ display: "inline-block", animation: "spin 1s linear infinite" }}>⟳</span>
                Publishing...
              </>
            ) : success ? (
              <>
                <span>✅</span>
                Published
              </>
            ) : (
              <>
                <span>📤</span>
                Publish
              </>
            )}
          </button>
        </div>
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

function ArtifactTab({ artifactType, content, isActive, onEdit }) {
  const [copied, setCopied] = useState(false);
  const [showJiraPublisher, setShowJiraPublisher] = useState(false);
  const meta = ARTIFACT_META[artifactType] || ARTIFACT_META.rfe_description;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${artifactType.replace('_', '-')}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-gray-50">
        <div className="flex items-center gap-3">
          <div className={cn("p-2 rounded-lg border", meta.color)}>
            <meta.icon className="h-4 w-4" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{meta.title}</h3>
            <p className="text-xs text-gray-500">{meta.description}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <h1>hello</h1>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCopy}
            className="h-8"
          >
            {copied ? (
              <Check className="h-3 w-3 text-green-600" />
            ) : (
              <Copy className="h-3 w-3" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleDownload}
            className="h-8"
          >
            <Download className="h-3 w-3" />
          </Button>
          <Button
            variant="jira"
            size="sm"
            onClick={() => setShowJiraPublisher(true)}
            className="h-8"
            title="Publish to JIRA"
          >
            <Send className="h-3 w-3" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onEdit(artifactType)}
            className="h-8"
          >
            <Edit3 className="h-3 w-3" />
          </Button>
        </div>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1 p-4">
        <div className="prose prose-sm max-w-none">
          <Markdown content={content} />
        </div>
      </ScrollArea>
      
      {/* JIRA Publisher Dialog */}
      <JiraPublisher
        isOpen={showJiraPublisher}
        onClose={() => setShowJiraPublisher(false)}
        artifactType={artifactType}
        artifactTitle={meta.title}
        content={content}
        onPublishSuccess={(result) => {
          console.log('Published to JIRA:', result);
        }}
      />
    </div>
  );
}

function RFEBuilderProgress({ event }) {
  if (!event) return null;

  const { phase, stage, description, artifact_type, progress, streaming_type } = event;
  
  const getPhaseColor = (phase) => {
    switch (phase) {
      case 'building': return 'bg-blue-100 text-blue-800';
      case 'generating': return 'bg-green-100 text-green-800';
      case 'editing': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStreamingIndicator = (type) => {
    if (!type) return null;
    
    return (
      <Badge variant="outline" className="ml-2 animate-pulse">
        {type === 'reasoning' ? '🧠 Thinking...' : '✍️ Writing...'}
      </Badge>
    );
  };

  return (
    <Card className="mb-4">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Badge className={getPhaseColor(phase)}>
              {phase.charAt(0).toUpperCase() + phase.slice(1)} Phase
            </Badge>
            {getStreamingIndicator(streaming_type)}
          </div>
          <Badge variant="secondary">{progress}%</Badge>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="space-y-2">
          <div className="text-sm font-medium">
            {stage.charAt(0).toUpperCase() + stage.slice(1)}
            {artifact_type && ` - ${ARTIFACT_META[artifact_type]?.title}`}
          </div>
          {description && (
            <div className="text-xs text-gray-600">{description}</div>
          )}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function ArtifactTabs({ artifacts = {}, events = [], onEditArtifact }) {
  const [activeTab, setActiveTab] = useState(null);

  // Set default active tab when artifacts are available
  useEffect(() => {
    const artifactKeys = Object.keys(artifacts);
    if (artifactKeys.length > 0 && !activeTab) {
      setActiveTab(artifactKeys[0]);
    }
  }, [artifacts, activeTab]);

  // Get the latest progress event
  const latestProgressEvent = events
    .filter(e => e.type === 'rfe_builder_progress')
    .slice(-1)[0]?.data;

  const artifactCount = Object.keys(artifacts).length;
  const hasArtifacts = artifactCount > 0;

  if (!hasArtifacts && !latestProgressEvent) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        <div className="text-center">
          <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
          <p>No artifacts generated yet.</p>
          <p className="text-sm">Start a conversation to begin building your RFE!</p>
        </div>
      </div>
    );
  }

  if (latestProgressEvent && !hasArtifacts) {
    return (
      <div className="h-full p-4">
        <RFEBuilderProgress event={latestProgressEvent} />
        <div className="flex items-center justify-center flex-1 text-gray-500 mt-8">
          <div className="text-center">
            <Building2 className="h-12 w-12 mx-auto mb-4 text-gray-300 animate-pulse" />
            <p>Building your RFE and artifacts...</p>
            <p className="text-sm">This may take a few minutes.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Progress indicator if still in progress */}
      {latestProgressEvent && latestProgressEvent.progress < 100 && (
        <div className="p-4 border-b">
          <RFEBuilderProgress event={latestProgressEvent} />
        </div>
      )}

      {/* Artifact tabs */}
      {hasArtifacts && (
        <Tabs 
          value={activeTab} 
          onValueChange={setActiveTab}
          className="flex-1 flex flex-col"
        >
          <TabsList className="grid w-full grid-cols-4 h-12 p-1 m-4 mb-0">
            {Object.entries(artifacts).map(([key, content]) => {
              const meta = ARTIFACT_META[key] || ARTIFACT_META.rfe_description;
              return (
                <TabsTrigger 
                  key={key} 
                  value={key}
                  className="flex items-center gap-2 text-xs"
                >
                  <meta.icon className="h-3 w-3" />
                  <span className="hidden sm:inline">{meta.title}</span>
                </TabsTrigger>
              );
            })}
          </TabsList>

          {Object.entries(artifacts).map(([key, content]) => (
            <TabsContent 
              key={key} 
              value={key}
              className="flex-1 m-4 mt-0"
            >
              <Card className="h-full">
                <ArtifactTab
                  artifactType={key}
                  content={content}
                  isActive={activeTab === key}
                  onEdit={onEditArtifact}
                />
              </Card>
            </TabsContent>
          ))}
        </Tabs>
      )}
    </div>
  );
}
