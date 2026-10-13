import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import AppShell from "../components/AppShell";
import Loading from "../components/Loading";
import ErrorState from "../components/ErrorState";
import { api, getSessionId, getSessionState, mergeSessionState, clearSessionId } from "../api/api";

function unwrap(data) {
  return data?.state || data?.data?.state || data || {};
}

export default function Report() {
  const navigate = useNavigate();
  const sessionId = getSessionId();
  const [state, setState] = useState(() => getSessionState());
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
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
      setState(mergeSessionState(unwrap(progressResult)));
      setPerformance(performanceResult?.performance || performanceResult?.state || performanceResult || {});
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [sessionId]);

  if (loading) return <AppShell><Loading label="Preparing your progress report..." /></AppShell>;
  if (error && !state) return <AppShell><ErrorState message={error} onRetry={load} /></AppShell>;

  const score = Number(performance?.quiz_accuracy ?? state?.quiz_score ?? 0);
  const strong = performance?.strong_topics || state?.strong_topics || [];
  const medium = performance?.medium_topics || state?.medium_topics || [];
  const weak = performance?.weak_topics || state?.weak_topics || [];
  const quizHistory = performance?.quiz_history || [];
  const topicPerformance = performance?.topic_performance || [];
  const goalCompleted = Boolean(state?.goal_completed);

  return (
    <AppShell eyebrow="Performance" title="Your learning results.">
      {/* Hero */}
      <div className="report-hero clean">
        <div>
          <span className="eyebrow">{state?.goal || "Learning journey"}</span>
          <h2>{state?.plan?.title || "Your learning report"}</h2>
        </div>
        <div className="report-score-ring">
          <strong>{Math.round(score)}%</strong>
          <span>quiz accuracy</span>
        </div>
      </div>

      <div className="report-sections clean">
        {/* Topic performance */}
        {(strong.length > 0 || medium.length > 0 || weak.length > 0) && (
          <section className="report-card">
            <span className="section-label">Topic performance</span>
            <div className="report-topic-group">
              {strong.length > 0 && (
                <div>
                  <b className="topic-group-label strong">✓ Strong</b>
                  <div className="topic-pills">
                    {strong.map((item) => <span key={item} className="pill strong">{item}</span>)}
                  </div>
                </div>
              )}
              {medium.length > 0 && (
                <div>
                  <b className="topic-group-label medium">◎ Developing</b>
                  <div className="topic-pills">
                    {medium.map((item) => <span key={item} className="pill medium">{item}</span>)}
                  </div>
                </div>
              )}
              {weak.length > 0 && (
                <div>
                  <b className="topic-group-label weak">✗ Needs practice</b>
                  <div className="topic-pills">
                    {weak.map((item) => <span key={item} className="pill weak">{item}</span>)}
                  </div>
                </div>
              )}
            </div>
          </section>
        )}

        {/* Quiz history */}
        <section className="report-card full-width">
          <span className="section-label">Quiz history</span>
          {quizHistory.length ? (
            <div className="quiz-history-table">
              <div className="qh-header">
                <span>Topic</span>
                <span>Score</span>
                <span>Result</span>
              </div>
              {quizHistory.map((item, index) => {
                const correctAnswers = item.correct_answers ?? item.correct ?? null;
                const totalQuestions = item.total_questions ?? item.total ?? null;
                const resultText = (correctAnswers !== null && totalQuestions !== null)
                  ? `${correctAnswers} / ${totalQuestions} correct`
                  : totalQuestions
                    ? `— / ${totalQuestions}`
                    : "—";
                return (
                  <div className="qh-row" key={`${item.topic}-${index}`}>
                    <span className="qh-topic">{item.topic}</span>
                    <b className={`qh-score ${Number(item.score) >= 80 ? "strong" : Number(item.score) >= 60 ? "medium" : "weak"}`}>
                      {Math.round(Number(item.score || 0))}%
                    </b>
                    <span className="qh-detail">{resultText}</span>
                  </div>
                );
              })}
            </div>
          ) : <p className="muted">No quiz attempts recorded yet. Complete a topic to take a quiz.</p>}
        </section>

        {/* Topic performance history (scores per topic) */}
        {topicPerformance.length > 0 && (
          <section className="report-card full-width">
            <span className="section-label">Topic score breakdown</span>
            <div className="quiz-history-table">
              <div className="qh-header">
                <span>Topic</span>
                <span>Score</span>
                <span>Level</span>
              </div>
              {topicPerformance.map((item) => (
                <div className="qh-row" key={item.topic}>
                  <span className="qh-topic">{item.topic}</span>
                  <b className={`qh-score ${item.status === "strong" ? "strong" : item.status === "medium" ? "medium" : "weak"}`}>
                    {Math.round(Number(item.score || 0))}%
                  </b>
                  <span className="qh-detail">{item.status}</span>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>

      <div className="report-footer">
        <button className="button secondary" onClick={() => navigate("/dashboard")}>← Return to learning</button>
        <button className="button primary" onClick={() => { clearSessionId(); navigate("/setup"); }}>
          {goalCompleted ? "Start new journey →" : "New learning journey →"}
        </button>
      </div>
    </AppShell>
  );
}
