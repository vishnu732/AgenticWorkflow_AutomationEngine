import { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [processDescription, setProcessDescription] = useState(
    "A customer requested a refund. Check the customer record, validate refund eligibility, create a support ticket, update CRM status, and send a confirmation email."
  );

  const [workflows, setWorkflows] = useState([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [latestResult, setLatestResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchWorkflows = async () => {
    try {
      setHistoryLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/workflows`);

      if (!response.ok) {
        throw new Error("Failed to fetch workflow history");
      }

      const data = await response.json();
      setWorkflows(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setHistoryLoading(false);
    }
  };

  const fetchWorkflowDetails = async (workflowId) => {
    try {
      setError("");
      const response = await fetch(`${API_BASE_URL}/api/workflows/${workflowId}`);

      if (!response.ok) {
        throw new Error("Failed to fetch workflow details");
      }

      const data = await response.json();
      setSelectedWorkflow(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const runWorkflow = async () => {
    if (!processDescription.trim()) {
      setError("Please enter a business process description.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setLatestResult(null);

      const response = await fetch(`${API_BASE_URL}/api/workflows/run`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          process_description: processDescription
        })
      });

      if (!response.ok) {
        throw new Error("Workflow execution failed");
      }

      const data = await response.json();

      setLatestResult(data);
      setSelectedWorkflow(data);

      await fetchWorkflows();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  const reviewWorkflow = async (workflowId, reviewStatus) => {
    const reason =
      reviewStatus === "approved"
        ? "Human reviewer approved the workflow execution."
        : "Human reviewer rejected the workflow execution.";

    try {
      setError("");

      const response = await fetch(`${API_BASE_URL}/api/workflows/${workflowId}/review`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          review_status: reviewStatus,
          override_reason: reason
        })
      });

      if (!response.ok) {
        throw new Error("Failed to update workflow review status");
      }

      const data = await response.json();

      setSelectedWorkflow(data);
      await fetchWorkflows();
    } catch (err) {
      setError(err.message);
    }
  };

  const retryWorkflow = async (workflowId) => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_BASE_URL}/api/workflows/${workflowId}/retry`, {
        method: "POST"
      });

      if (!response.ok) {
        throw new Error("Failed to retry workflow");
      }

      const data = await response.json();

      setLatestResult(data);
      setSelectedWorkflow(data);

      await fetchWorkflows();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    fetchWorkflows();
  }, []);

  const activeWorkflow = selectedWorkflow || latestResult;

  return (
    <div className="app">
      <header className="hero">
        <div>
          <p className="eyebrow">Agentic AI Workflow Platform</p>
          <h1>Agentic Workflow Automation Engine</h1>
          <p className="hero-subtitle">
            Decompose business processes into executable AI-planned tasks,
            route them to tools, and track every action with audit logs.
          </p>
        </div>

        <div className="status-card">
          <span className="status-dot"></span>
          <p>Backend Connected</p>
          <strong>FastAPI + Gemini + LangChain</strong>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <main className="dashboard">
        <section className="panel input-panel">
          <div className="panel-header">
            <div>
              <p className="section-label">Run Workflow</p>
              <h2>Business Process Input</h2>
            </div>
          </div>

          <textarea
            value={processDescription}
            onChange={(event) => setProcessDescription(event.target.value)}
            placeholder="Describe a business process..."
          />

          <button onClick={runWorkflow} disabled={loading}>
            {loading ? "Running Agent..." : "Run AI Workflow"}
          </button>
        </section>

        <section className="panel history-panel">
          <div className="panel-header">
            <div>
              <p className="section-label">Saved Runs</p>
              <h2>Workflow History</h2>
            </div>
            <button className="secondary-button" onClick={fetchWorkflows}>
              Refresh
            </button>
          </div>

          {historyLoading ? (
            <p className="muted">Loading workflow history...</p>
          ) : workflows.length === 0 ? (
            <p className="muted">No workflow runs saved yet.</p>
          ) : (
            <div className="workflow-list">
              {workflows.map((workflow) => (
                <button
                  key={workflow.workflow_id}
                  className="workflow-item"
                  onClick={() => fetchWorkflowDetails(workflow.workflow_id)}
                >
                  <div>
                    <strong>{workflow.status}</strong>
                    <p>{workflow.original_process}</p>
                  </div>
                  <span>{workflow.step_count} steps</span>
                </button>
              ))}
            </div>
          )}
        </section>

        <section className="panel details-panel">
          <div className="panel-header">
            <div>
              <p className="section-label">Execution Details</p>
              <h2>Workflow Result</h2>
            </div>
          </div>

          {!activeWorkflow ? (
            <p className="muted">Run or select a workflow to view details.</p>
          ) : (
            <>
              <div className="summary-grid">
                <div>
                  <span>Status</span>
                  <strong>{activeWorkflow.status}</strong>
                </div>
                              <div className="review-actions">
                <div>
                  <span>Review Status</span>
                  <strong>{activeWorkflow.review_status || "pending"}</strong>
                </div>

                <button
                  className="approve-button"
                  onClick={() => reviewWorkflow(activeWorkflow.workflow_id, "approved")}
                >
                  Approve Workflow
                </button>

                <button
                  className="reject-button"
                  onClick={() => reviewWorkflow(activeWorkflow.workflow_id, "rejected")}
                >
                  Reject Workflow
                </button>

                <button
                  className="retry-button"
                  onClick={() => retryWorkflow(activeWorkflow.workflow_id)}
                  disabled={loading}
                >
                  Retry Workflow
                </button>
              </div>

              {activeWorkflow.override_reason && (
                <div className="override-note">
                  <strong>Override Reason:</strong> {activeWorkflow.override_reason}
                </div>
              )}
                <div>
                  <span>Workflow ID</span>
                  <strong className="small-text">{activeWorkflow.workflow_id}</strong>
                </div>
                <div>
                  <span>Total Steps</span>
                  <strong>{activeWorkflow.steps?.length || 0}</strong>
                </div>
              </div>

              <h3>Agent Steps</h3>
              <div className="steps">
                {activeWorkflow.steps?.map((step) => (
                  <div className="step-card" key={step.step_id}>
                    <div className="step-top">
                      <span>Step {step.step_id}</span>
                      <strong>{step.status}</strong>
                    </div>
                    <h4>{step.task}</h4>
                    <p>
                      Tool used: <code>{step.tool_used}</code>
                    </p>
                    <p>{step.result?.message}</p>
                  </div>
                ))}
              </div>

              <h3>Audit Log</h3>
              <div className="audit-log">
                {activeWorkflow.audit_log?.map((log, index) => (
                  <p key={index}>{log}</p>
                ))}
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;