import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import AppShell from "../components/AppShell";
import Loading from "../components/Loading";
import ErrorState from "../components/ErrorState";
import { api, getSessionId, getSessionState, mergeSessionState } from "../api/api";
import { CheckIcon, ChevronIcon, ClockIcon } from "../components/Icons";

function unwrap(data) {
  return data?.state || data?.data?.state || data || {};
}

function normalizeTasks(tasks = [], statuses = {}) {
  return tasks.map((task) => ({
    ...task,
    task_id: task.id || task.task_id,
    status: statuses[task.id || task.task_id] || task.status || "not_done",
  }));
}

function statusLabel(status) {
  return status === "done" ? "Done" : status === "skip" ? "Skip" : "Not done";
}

const typeIcon = { study: "📖", practice: "💻", project: "🚀" };
const toolTypeColor = {
  documentation: "#7fc8f5",
  tutorial: "#b9f36b",
  tool: "#f0c56b",
  practice: "#c084fc",
  video: "#fb923c",
  reference: "#94a3b8",
};

function TaskDetailPanel({ sessionId, task, onClose }) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");
    api.getTaskDetail(sessionId, task.task_id)
      .then(setDetail)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [task.task_id, sessionId]);

  return (
    <div className="task-detail-overlay">
      <div className="task-detail-panel">
        {/* Header */}
        <div className="tdp-header">
          <div>
            <span className="tdp-type">{typeIcon[task.task_type] || "📋"} {task.task_type}</span>
            <h2 className="tdp-title">{task.title || task.name}</h2>
            {task.estimated_minutes && (
              <span className="tdp-meta"><ClockIcon /> {task.estimated_minutes} min</span>
            )}
          </div>
          <button className="tdp-close" onClick={onClose}>✕</button>
        </div>

        {task.description && (
          <p className="tdp-description">{task.description}</p>
        )}

        {loading && (
          <div className="tdp-loading">
            <div className="tdp-spinner" />
            <span>Generating structured guide…</span>
          </div>
        )}

        {error && (
          <div className="tdp-error">
            <span>⚠ Could not load details: {error}</span>
          </div>
        )}

        {detail && !loading && (
          <div className="tdp-body">
            {/* How to complete */}
            {detail.how_to_complete?.length > 0 && (
              <section className="tdp-section">
                <h3 className="tdp-section-title">✅ How to complete this task</h3>
                <ol className="tdp-steps">
                  {detail.how_to_complete.map((step, i) => (
                    <li key={i} className="tdp-step">
                      <span className="step-num">{i + 1}</span>
                      <span>{step}</span>
                    </li>
                  ))}
                </ol>
              </section>
            )}

            {/* Key concepts */}
            {detail.key_concepts?.length > 0 && (
              <section className="tdp-section">
                <h3 className="tdp-section-title">💡 Key concepts</h3>
                <ul className="tdp-concepts">
                  {detail.key_concepts.map((concept, i) => (
                    <li key={i}>{concept}</li>
                  ))}
                </ul>
              </section>
            )}

            {/* Tips */}
            {detail.tips?.length > 0 && (
              <section className="tdp-section">
                <h3 className="tdp-section-title">⚡ Tips &amp; common mistakes</h3>
                <ul className="tdp-tips">
                  {detail.tips.map((tip, i) => (
                    <li key={i}>{tip}</li>
                  ))}
                </ul>
              </section>
            )}

            {/* Tools & Resources */}
            {detail.tools?.length > 0 && (
              <section className="tdp-section">
                <h3 className="tdp-section-title">🔧 Tools &amp; resources</h3>
                <div className="tdp-tools">
                  {detail.tools.map((tool, i) => (
                    <a
                      key={i}
                      href={tool.url}
                      target="_blank"
                      rel="noreferrer"
                      className="tdp-tool-card"
                    >
                      <div className="tdp-tool-top">
                        <span className="tdp-tool-name">{tool.name}</span>
                        <span
                          className="tdp-tool-type"
                          style={{ color: toolTypeColor[tool.type] || "#94a3b8" }}
                        >
                          {tool.type}
                        </span>
                      </div>
                      <p className="tdp-tool-desc">{tool.description}</p>
                      <span className="tdp-tool-url">↗ {tool.url.replace(/^https?:\/\//, "")}</span>
                    </a>
                  ))}
                </div>
              </section>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const navigate = useNavigate();
  const sessionId = getSessionId();
  const [state, setState] = useState(() => getSessionState());
  const [statuses, setStatuses] = useState({});
  const [activeDetail, setActiveDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    if (!sessionId) {
      navigate("/setup", { replace: true });
      return;
    }
    setLoading(true);
    try {
      const progressResult = await api.getProgress(sessionId);
      const nextState = mergeSessionState(unwrap(progressResult));
      setState(nextState);

      const nextStatuses = {};
      (nextState.tasks || []).forEach((task) => {
        nextStatuses[task.id || task.task_id] = task.status || "not_done";
      });
      setStatuses(nextStatuses);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [sessionId]);

  const tasks = useMemo(
    () => normalizeTasks(state?.tasks || [], statuses),
    [state?.tasks, statuses],
  );

  const doneCount = tasks.filter((t) => t.status === "done").length;
  const completion = tasks.length ? Math.round((doneCount / tasks.length) * 100) : 0;
  const topic = state?.current_topic || "Learning";
  const day = state?.current_day || 1;
  const revisionMode = state?.adaptive_action === "improve_weak_topics" || state?.revision_mode;
  const carried = state?.carried_forward_tasks || [];

  function setStatus(taskId, status) {
    setStatuses((cur) => ({ ...cur, [taskId]: status }));
  }

  async function submitDay() {
    if (!tasks.length) return;
    setSaving(true);
    setError("");
    try {
      const result = await api.submitDay(
        sessionId,
        tasks.map((task) => ({
          task_id: task.task_id,
          status: statuses[task.task_id] || "not_done",
          notes: null,
        })),
      );
      const nextState = unwrap(result);
      setState(mergeSessionState(nextState));

      const interruptType = nextState?.interrupt_type || nextState?.waiting_for || result?.interrupt?.type;
      if (interruptType === "quiz_submission" || nextState?.quiz?.length) {
        navigate("/quiz");
        return;
      }

      setSubmitted(true);
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <AppShell><Loading label="Loading your learning workspace..." /></AppShell>;
  if (error && !state) return <AppShell><ErrorState message={error} onRetry={load} /></AppShell>;

  return (
    <AppShell>
      {/* Task detail overlay */}
      {activeDetail && (
        <TaskDetailPanel
          sessionId={sessionId}
          task={activeDetail}
          onClose={() => setActiveDetail(null)}
        />
      )}

      {/* Header */}
      <div className="workspace-header">
        <div>
          <span className="eyebrow">{revisionMode ? "Focused remediation" : `Day ${day}`}</span>
          <h1>{topic}</h1>
          <p className="workspace-subtitle">
            Work through today's tasks at your own pace.
            {carried.length > 0 && <span className="carry-badge">{carried.length} carried forward</span>}
          </p>
        </div>
        <button className="button secondary small" onClick={() => navigate("/report")}>
          📊 Performance
        </button>
      </div>

      {/* Progress bar */}
      <div className="day-progress-bar">
        <div className="day-progress-fill" style={{ width: `${completion}%` }} />
      </div>
      <div className="day-progress-label">
        <span>{doneCount} of {tasks.length} completed</span>
        <span>{completion}%</span>
      </div>

      {/* Task list */}
      <div className="task-list clean">
        {tasks.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">✦</span>
            <h3>No tasks waiting here.</h3>
            <p>The learning workflow may be waiting for your next step.</p>
            <button className="button primary" onClick={load}>Refresh workspace</button>
          </div>
        ) : tasks.map((task, index) => (
          <article className={`task-card clean ${task.status}`} key={task.task_id}>
            <div className="task-main">
              <div className="task-number">{String(index + 1).padStart(2, "0")}</div>
              <div className="task-copy">
                <div className="task-title-row">
                  <h3>{task.title || task.name || `Task ${index + 1}`}</h3>
                  <div className="task-badges">
                    {task.estimated_minutes && (
                      <span className="badge"><ClockIcon /> {task.estimated_minutes} min</span>
                    )}
                    <span className="badge type">
                      {typeIcon[task.task_type] || "📋"} {task.task_type || "study"}
                    </span>
                  </div>
                </div>
                <p className="task-desc">{task.description || "Complete this task as part of today's learning plan."}</p>
                {task.objective && (
                  <p className="task-objective">🎯 {task.objective}</p>
                )}
                <button
                  className="details-button"
                  onClick={() => setActiveDetail(task)}
                >
                  View details <ChevronIcon />
                </button>
              </div>
            </div>

            {/* Status actions */}
            <div className="status-actions">
              {["done", "not_done", "skip"].map((status) => (
                <button
                  key={status}
                  className={`status-button ${task.status === status ? `active ${status}` : ""}`}
                  onClick={() => setStatus(task.task_id, status)}
                >
                  {status === "done" && <CheckIcon />}
                  {statusLabel(status)}
                </button>
              ))}
            </div>
          </article>
        ))}
      </div>

      {error && <div className="form-error" style={{ marginTop: "1rem" }}>{error}</div>}

      {/* Footer */}
      {!submitted && tasks.length > 0 && (
        <div className="day-footer clean">
          <div>
            <b>Ready to submit?</b>
            <span>Unfinished tasks carry forward. Skipped tasks do not.</span>
          </div>
          <button className="button primary" onClick={submitDay} disabled={saving}>
            {saving ? "Saving..." : "Submit today's work →"}
          </button>
        </div>
      )}

      {submitted && (
        <div className="day-submitted">
          <span className="submitted-icon">✓</span>
          <div>
            <b>Day submitted!</b>
            <span>Your progress has been saved. The next day will load shortly.</span>
          </div>
        </div>
      )}
    </AppShell>
  );
}
