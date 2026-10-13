import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import AppShell from "../components/AppShell";
import Loading from "../components/Loading";
import ErrorState from "../components/ErrorState";
import { api, getSessionId, getSessionState, mergeSessionState, saveSessionState } from "../api/api";

function unwrap(data) {
  return data?.state || data?.data?.state || data || {};
}

export default function Quiz() {
  const navigate = useNavigate();
  const sessionId = getSessionId();
  const [state, setState] = useState(() => getSessionState());
  const [answers, setAnswers] = useState({});
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
      const result = await api.getProgress(sessionId);
      const nextState = unwrap(result);
      setState(mergeSessionState(nextState));

      if (!nextState?.quiz?.length) {
        navigate("/dashboard", { replace: true });
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [sessionId]);

  async function submit() {
    const quiz = state?.quiz || [];
    if (Object.keys(answers).length !== quiz.length) {
      setError("Please answer every question before submitting.");
      return;
    }

    setSubmitting(true);
    setError("");

    try {
      const result = await api.submitQuiz(
        sessionId,
        quiz.map((question) => ({
          question_id: question.id || question.question_id,
          answer: answers[question.id || question.question_id],
        })),
      );

      // Merge the state from result.state into session storage
      const mergedState = mergeSessionState(unwrap(result));

      // Also persist top-level scoring fields (correct_answers, total_questions etc.)
      // which are returned at the top level of the response, not inside result.state
      const scoringFields = {
        quiz_score: result.quiz_score ?? result.score ?? mergedState.quiz_score,
        correct_answers: result.correct_answers ?? result.correct,
        total_questions: result.total_questions ?? result.total,
        weak_topics: result.weak_topics ?? mergedState.weak_topics ?? [],
        strong_topics: result.strong_topics ?? mergedState.strong_topics ?? [],
        medium_topics: result.medium_topics ?? mergedState.medium_topics ?? [],
        adaptive_action: result.adaptive_action ?? mergedState.adaptive_action ?? "move_forward",
      };
      saveSessionState({ ...mergedState, ...scoringFields });
      setState({ ...mergedState, ...scoringFields });

      navigate("/adaptation", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <AppShell><Loading label="Preparing your assessment..." /></AppShell>;
  if (error && !state) return <AppShell><ErrorState message={error} onRetry={load} /></AppShell>;

  const quiz = state?.quiz || [];
  const answered = Object.keys(answers).length;

  return (
    <AppShell eyebrow="Topic assessment" title={state?.current_topic || "Knowledge check"}>
      <div className="quiz-progress-bar"><i style={{ width: `${quiz.length ? (answered / quiz.length) * 100 : 0}%` }} /></div>
      <div className="quiz-intro">
        <div>
          <p>Answer the questions based on what you learned in this topic. Your result will inform the next-step recommendation.</p>
        </div>
        <span className="quiz-count">{answered} / {quiz.length} answered</span>
      </div>

      <div className="quiz-list">
        {quiz.map((question, index) => {
          const id = question.id || question.question_id;
          return (
            <article className="quiz-question" key={id}>
              <div className="question-number">{String(index + 1).padStart(2, "0")}</div>
              <div className="question-body">
                <div className="question-type">{question.question_type || "mcq"}{question.topic ? ` · ${question.topic}` : ""}</div><h2>{question.question}</h2>
                <div className="options">
                  {(question.options || []).map((option) => (
                    <button
                      key={option}
                      className={`option ${answers[id] === option ? "selected" : ""}`}
                      onClick={() => setAnswers((current) => ({ ...current, [id]: option }))}
                    >
                      <span className="radio">{answers[id] === option ? "✓" : ""}</span>
                      <span>{option}</span>
                    </button>
                  ))}
                </div>
              </div>
            </article>
          );
        })}
      </div>

      {error && <div className="form-error">{error}</div>}

      <div className="quiz-submit">
        <span>Assessment complete → adaptive analysis</span>
        <button className="button primary" disabled={submitting || answered !== quiz.length} onClick={submit}>
          {submitting ? "Evaluating..." : "Submit assessment"}
        </button>
      </div>
    </AppShell>
  );
}
