import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import AppShell from "../components/AppShell";
import Loading from "../components/Loading";
import ErrorState from "../components/ErrorState";
import { api, getSessionId, getSessionState, mergeSessionState, saveSessionId } from "../api/api";
import { ClockIcon, CheckIcon } from "../components/Icons";

const getState = (data) => data?.state || data?.data?.state || data || {};
const list = (value) => Array.isArray(value) ? value : [];

export default function Plan() {
  const navigate = useNavigate();
  const location = useLocation();
  const sessionId = location.state?.sessionId || getSessionId();
  const [state, setState] = useState(() => getSessionState());
  const [feedback, setFeedback] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(!getSessionState());
  const [submitting, setSubmitting] = useState(false);

  async function load() {
    if (!sessionId) return navigate("/setup", { replace: true });
    setLoading(true);
    try {
      const result = await api.getProgress(sessionId);
      const server = getState(result);
      const merged = mergeSessionState(server);
      setState(merged); saveSessionId(sessionId);
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  }
  useEffect(() => { load(); }, [sessionId]);

  const plan = state?.plan || {};
  const topics = list(plan.topics);
  const totalDays = useMemo(() => topics.reduce((sum, topic) => sum + Number(topic.estimated_days || 1), 0), [topics]);
  const skillGaps = list(state?.skill_gaps).map((gap) => typeof gap === "string" ? gap : gap?.skill).filter(Boolean);

  async function approve(approved) {
    setSubmitting(true); setError("");
    try {
      const result = await api.approvePlan(sessionId, approved, feedback);
      const nextState = mergeSessionState(getState(result)); setState(nextState);
      if (approved) navigate("/dashboard", { replace: true }); else setFeedback("");
    } catch (err) { setError(err.message); } finally { setSubmitting(false); }
  }

  if (loading && !state) return <AppShell><Loading label="Preparing your learning plan..." /></AppShell>;
  if (error && !state) return <AppShell><ErrorState message={error} onRetry={load} /></AppShell>;

  return <AppShell eyebrow="Plan approval" title={plan.title || "Your learning plan"}>
    <div className="plan-summary">
      <div><p>{plan.summary || "A structured roadmap generated from your goal, level, availability and context."}</p><div className="context-tags"><span>{state?.learning_mode === "project" ? "Project learning" : "General learning"}</span><span>{state?.current_level || "beginner"}</span><span>{state?.available_time_minutes || 60} min/day</span>{state?.duration_days && <span>{state.duration_days} days</span>}</div></div>
      <div className="plan-metrics"><div><strong>{topics.length}</strong><span>topics</span></div><div><strong>{totalDays}</strong><span>estimated days</span></div></div>
    </div>

    {state?.learning_mode === "project" && <section className="context-card"><div><span className="section-label">Project skill-gap analysis</span><h2>{state.project_name || state.role}</h2><p>{state.project_description}</p></div>{skillGaps.length > 0 ? <div className="topic-pills">{skillGaps.map((gap) => <span key={gap}>{gap}</span>)}</div> : <p className="muted">No missing skills were identified from the supplied project context.</p>}</section>}

    <div className="timeline">{topics.map((topic, index) => <div className="timeline-item" key={`${topic.title}-${index}`}><div className="timeline-marker">{String(index + 1).padStart(2, "0")}</div><div className="timeline-line" /><div className="timeline-content"><div className="topic-top"><div><span className="topic-index">Topic {index + 1}</span><h2>{topic.title}</h2></div><span className="duration"><ClockIcon /> {topic.estimated_days || 1} day{Number(topic.estimated_days || 1) !== 1 ? "s" : ""}</span></div><p>{topic.description}</p>{list(topic.objectives).length > 0 && <div className="objective-list">{topic.objectives.map((objective) => <span key={objective}><CheckIcon /> {objective}</span>)}</div>}</div></div>)}</div>

    <div className="approval-panel"><div><span className="eyebrow">Your review</span><h2>Does this roadmap look right?</h2><p>Approve it to begin daily learning, or send feedback to the planner for a revision.</p></div><textarea value={feedback} onChange={(e) => setFeedback(e.target.value)} placeholder="Optional revision feedback..." rows="2" />{error && <div className="form-error">{error}</div>}<div className="approval-actions"><button className="button secondary" disabled={submitting} onClick={() => approve(false)}>Request revision</button><button className="button primary" disabled={submitting} onClick={() => approve(true)}>{submitting ? "Saving..." : "Approve plan →"}</button></div></div>
  </AppShell>;
}
