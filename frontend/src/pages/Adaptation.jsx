import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import AppShell from "../components/AppShell";
import Loading from "../components/Loading";
import ErrorState from "../components/ErrorState";
import { api, getSessionId, getSessionState, mergeSessionState } from "../api/api";
import { SparkIcon, CheckIcon } from "../components/Icons";

function unwrap(data) {
  return data?.state || data?.data?.state || data || {};
}

function pickPerformance(data) {
  return data?.performance || data?.state || data || {};
}

export default function Adaptation() {
  const navigate = useNavigate();
  const sessionId = getSessionId();
  // Initialize from session state immediately — Quiz.jsx saves all scoring fields there
  const [state, setState] = useState(() => getSessionState());
  const [performance, setPerformance] = useState(null);
  const [selected, setSelected] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    if (!sessionId) {
      navigate("/setup", { replace: true });
      return;
    }

    setLoading(true);
    try {
      const [progressResult, performanceResult] = await Promise.all([
        api.getProgress(sessionId),
        api.getPerformance(sessionId),
      ]);

      // Merge progress but DON'T overwrite scoring fields that Quiz.jsx saved
      const freshProgress = unwrap(progressResult);
      const cachedState = getSessionState() || {};
      // Preserve quiz scoring fields from session cache (set by Quiz submit)
      const merged = mergeSessionState({
        ...freshProgress,
        // Keep these from cached state if fresh progress doesn't have them
        quiz_score: freshProgress.quiz_score ?? cachedState.quiz_score,
        correct_answers: cachedState.correct_answers,
        total_questions: cachedState.total_questions,
        weak_topics: freshProgress.weak_topics?.length ? freshProgress.weak_topics : cachedState.weak_topics,
        strong_topics: freshProgress.strong_topics?.length ? freshProgress.strong_topics : cachedState.strong_topics,
        medium_topics: freshProgress.medium_topics?.length ? freshProgress.medium_topics : cachedState.medium_topics,
        adaptive_action: freshProgress.adaptive_action ?? cachedState.adaptive_action,
      });
      setState(merged);
      setPerformance(pickPerformance(performanceResult));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [sessionId]);

  // Quiz score: prefer the value saved directly from quiz submit (most accurate)
  const score = Number(
    state?.quiz_score ??
    performance?.quiz_accuracy ??
    0,
  );

  const correctAnswers = Number(state?.correct_answers ?? 0);
  const totalQuestions = Number(state?.total_questions ?? 0);
  const hasExactCount = totalQuestions > 0;

  const currentTopicResult = state?.topic_performance?.[state?.current_topic] || null;
  const classification = currentTopicResult?.performance ? `${currentTopicResult.performance} understanding` :
    score >= 80 ? "Strong understanding" :
    score >= 60 ? "Developing understanding" :
    score > 0 ? "Needs reinforcement" :
    "Assessment complete";

  const weakTopics = state?.weak_topics?.length ? state.weak_topics : (performance?.weak_topics || []);
  const improvementGuidance = state?.improvement_description || performance?.improvement_description || "";
  const strongTopics = state?.strong_topics?.length ? state.strong_topics : (performance?.strong_topics || []);
  const mediumTopics = state?.medium_topics?.length ? state.medium_topics : (performance?.medium_topics || []);
  const recommendation = state?.adaptive_action || "move_forward";

  const recommendationText = state?.adaptive_recommendation || (recommendation === "improve_weak_topics" ? "Work on weak topics" : "Go to next topic");

  const canRemediate = weakTopics.length > 0;
  const displayWeak = weakTopics.slice(0, 5);

  async function chooseAction() {
    if (!selected) return;

    setSubmitting(true);
    setError("");

    try {
      const result = await api.submitAdaptation(sessionId, selected);
      const nextState = mergeSessionState(unwrap(result));

      if (selected === "improve_weak_topics") {
        navigate("/dashboard", { replace: true, state: { remediation: true } });
      } else if (
        nextState?.goal_completed ||
        nextState?.learning_completed ||
        nextState?.readiness
      ) {
        navigate("/report", { replace: true });
      } else {
        navigate("/dashboard", { replace: true });
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }


  if (loading) return <AppShell><Loading label="Analyzing your assessment..." /></AppShell>;
  if (error && !state) return <AppShell><ErrorState message={error} onRetry={load} /></AppShell>;

  return (
    <AppShell eyebrow="Assessment complete" title={state?.current_topic || "Adaptive decision"}>
      <div className="adaptation-hero">
        <div className="score-ring">
          <strong>{Math.round(score)}%</strong>
          <span>{hasExactCount ? `${correctAnswers} / ${totalQuestions} correct` : "score"}</span>
        </div>
        <div>
          <span className="eyebrow">Performance</span>
          <h2>{classification}</h2>
          <p>The system has analyzed your result. The recommendation is guidance — <b>you decide</b> what happens next.</p>
        </div>
      </div>

      <div className="analysis-grid">
        <div className="analysis-card">
          <span className="section-label">Strong areas</span>
          {strongTopics.length ? (
            <div className="topic-pills">{strongTopics.map((topic) => <span key={topic}><CheckIcon /> {topic}</span>)}</div>
          ) : <p className="muted">No strong areas were recorded yet.</p>}
        </div>

        <div className="analysis-card weak">
          <span className="section-label">Needs more practice</span>
          {displayWeak.length ? (
            <div className="topic-pills">{displayWeak.map((topic) => <span key={topic}>{topic}</span>)}</div>
          ) : <p className="muted">No weak topics were identified.</p>}
        </div>

        {mediumTopics.length > 0 && (
          <div className="analysis-card full-width">
            <span className="section-label">Developing areas</span>
            <div className="topic-pills">{mediumTopics.map((topic) => <span key={topic}>{topic}</span>)}</div>
          </div>
        )}
      </div>

      <div className="improvement-guidance"><span className="section-label">Question-level improvement guidance</span><p>{improvementGuidance || "No question-level improvement guidance was recorded."}</p></div>

      <div className="recommendation">
        <div className="insight-icon"><SparkIcon /></div>
        <div>
          <span className="section-label">AI recommendation</span>
          <h3>{recommendationText}</h3>
          <p>{canRemediate ? "The backend identified areas that could benefit from focused practice before moving forward." : "Your current result does not require a remediation path."}</p>
        </div>
      </div>

      <section className="decision-panel">
        <div>
          <span className="eyebrow">Your choice</span>
          <h2>What would you like to do?</h2>
          <p>Select one path. AgenticLearn will follow your decision.</p>
        </div>

        <div className="decision-options">
          <button
            className={`decision-option ${selected === "improve_weak_topics" ? "selected" : ""}`}
            disabled={!canRemediate}
            onClick={() => setSelected("improve_weak_topics")}
          >
            <span className="decision-icon">↻</span>
            <span><b>Work on weak topics</b><small>Generate up to three focused remediation tasks, then reassess.</small></span>
            <span className="radio">{selected === "improve_weak_topics" ? "✓" : ""}</span>
          </button>

          <button
            className={`decision-option ${selected === "move_forward" ? "selected" : ""}`}
            onClick={() => setSelected("move_forward")}
          >
            <span className="decision-icon">→</span>
            <span><b>Go to next topic</b><small>Continue with the next topic in your approved learning plan.</small></span>
            <span className="radio">{selected === "move_forward" ? "✓" : ""}</span>
          </button>
        </div>

        {error && <div className="form-error">{error}</div>}

        <div className="decision-footer">
          <span>Recommendation: <b>{recommendationText}</b></span>
          <button className="button primary" disabled={!selected || submitting} onClick={chooseAction}>
            {submitting ? "Updating path..." : "Continue →"}
          </button>
        </div>
      </section>
    </AppShell>
  );
}
