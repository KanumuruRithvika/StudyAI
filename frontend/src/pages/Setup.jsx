import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import AppShell from "../components/AppShell";
import { api, clearSessionId, saveSessionId, saveSessionState } from "../api/api";

const levels = ["Beginner", "Intermediate", "Advanced"];
const splitList = (value) => value.split(",").map((item) => item.trim()).filter(Boolean);

export default function Setup() {
  const navigate = useNavigate();
  const [mode, setMode] = useState("general");
  const [form, setForm] = useState({
    goal: "", current_level: "Beginner", available_time_minutes: 60, duration_days: "",
    learning_preferences: "", prior_experience: "", additional_instructions: "",
    role: "", project_name: "", project_description: "", required_skills: "", required_technologies: "", current_skills: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const isProject = mode === "project";

  const missing = useMemo(() => {
    if (!form.goal.trim() || !form.current_level || !form.available_time_minutes) return true;
    if (isProject && (!form.role.trim() || !form.project_name.trim() || !form.project_description.trim() || !form.required_skills.trim() || !form.required_technologies.trim() || !form.current_skills.trim())) return true;
    return false;
  }, [form, isProject]);

  const update = (key, value) => setForm((current) => ({ ...current, [key]: value }));

  async function handleSubmit(event) {
    event.preventDefault();
    if (missing) return;
    setError(""); setLoading(true); clearSessionId();

    const payload = {
      learning_mode: mode,
      goal: form.goal.trim(),
      current_level: form.current_level.toLowerCase(),
      available_time_minutes: Number(form.available_time_minutes),
      ...(form.duration_days ? { duration_days: Number(form.duration_days) } : {}),
      ...(form.learning_preferences.trim() ? { learning_preferences: form.learning_preferences.trim() } : {}),
      ...(form.prior_experience.trim() ? { prior_experience: form.prior_experience.trim() } : {}),
      ...(form.additional_instructions.trim() ? { additional_instructions: form.additional_instructions.trim() } : {}),
    };

    if (isProject) Object.assign(payload, {
      role: form.role.trim(), project_name: form.project_name.trim(), project_description: form.project_description.trim(),
      current_skills: splitList(form.current_skills), required_skills: splitList(form.required_skills), required_technologies: splitList(form.required_technologies),
    });

    try {
      const result = await api.startLearning(payload);
      const sessionId = result?.session_id || result?.state?.session_id;
      if (!sessionId) throw new Error("The server did not return a learning session.");
      saveSessionId(sessionId);
      saveSessionState(result?.state || result);
      navigate("/plan", { state: { sessionId } });
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  }

  return (
    <AppShell eyebrow="New learning journey" title="Define the goal. AgenticLearn builds the path.">
      <div className="setup-layout">
        <aside className="mode-panel">
          <span className="section-label">Learning mode</span>
          <button type="button" className={`mode-option ${mode === "general" ? "selected" : ""}`} onClick={() => setMode("general")}><span className="mode-icon">◎</span><span><b>General learning</b><small>Build knowledge around a learning goal.</small></span></button>
          <button type="button" className={`mode-option ${mode === "project" ? "selected" : ""}`} onClick={() => setMode("project")}><span className="mode-icon">⌘</span><span><b>Project learning</b><small>Close a real-world role and project skill gap.</small></span></button>
          <div className="setup-note"><span>✦</span><p>Required fields are marked with <b>*</b>. Your account identity comes from authentication.</p></div>
        </aside>

        <form className="setup-form" onSubmit={handleSubmit}>
          <div className="form-section">
            <div className="form-section-title"><span>01</span><div><h2>Goal & context</h2><p>Give the planner the information it actually needs.</p></div></div>
            <label>Goal <span>*</span><textarea rows="3" value={form.goal} onChange={(e) => update("goal", e.target.value)} placeholder="What do you want to learn or achieve?" required /></label>
            {isProject && <>
              <div className="form-grid"><label>Role <span>*</span><input value={form.role} onChange={(e) => update("role", e.target.value)} placeholder="e.g. Backend Developer" required /></label><label>Project name <span>*</span><input value={form.project_name} onChange={(e) => update("project_name", e.target.value)} placeholder="e.g. E-commerce API" required /></label></div>
              <label>Project description <span>*</span><textarea rows="4" value={form.project_description} onChange={(e) => update("project_description", e.target.value)} placeholder="Describe what you want to build." required /></label>
              <div className="form-grid"><label>Required skills <span>*</span><input value={form.required_skills} onChange={(e) => update("required_skills", e.target.value)} placeholder="REST APIs, testing, Git" required /><small className="hint">Comma-separated.</small></label><label>Required technologies <span>*</span><input value={form.required_technologies} onChange={(e) => update("required_technologies", e.target.value)} placeholder="Python, FastAPI, PostgreSQL" required /><small className="hint">Comma-separated.</small></label></div>
              <label>Current skills <span>*</span><input value={form.current_skills} onChange={(e) => update("current_skills", e.target.value)} placeholder="Python, Git, SQL" required /><small className="hint">Comma-separated. Used for project skill-gap analysis.</small></label>
            </>}
          </div>

          <div className="form-section">
            <div className="form-section-title"><span>02</span><div><h2>Availability</h2><p>The planner keeps the roadmap within your time constraints.</p></div></div>
            <div className="form-grid three">
              <label>Current level <span>*</span><select value={form.current_level} onChange={(e) => update("current_level", e.target.value)} required>{levels.map((level) => <option key={level}>{level}</option>)}</select></label>
              <label>Available time / day <span>*</span><div className="input-suffix"><input type="number" min="1" value={form.available_time_minutes} onChange={(e) => update("available_time_minutes", e.target.value)} required /><span>min</span></div></label>
              <label>Duration <span className="optional-label">optional</span><div className="input-suffix"><input type="number" min="1" value={form.duration_days} onChange={(e) => update("duration_days", e.target.value)} placeholder="7" /><span>days</span></div></label>
            </div>
          </div>

          <div className="form-section">
            <div className="form-section-title"><span>03</span><div><h2>Optional signals</h2><p>These are passed to the planner when supplied.</p></div></div>
            <div className="form-grid"><label>Learning preferences<input value={form.learning_preferences} onChange={(e) => update("learning_preferences", e.target.value)} placeholder="Hands-on, visual, project-based" /></label><label>Prior experience<input value={form.prior_experience} onChange={(e) => update("prior_experience", e.target.value)} placeholder="What should the planner know?" /></label></div>
            <label>Additional instructions<input value={form.additional_instructions} onChange={(e) => update("additional_instructions", e.target.value)} placeholder="Constraints or preferences for the roadmap" /></label>
          </div>

          {error && <div className="form-error">{error}</div>}
          <div className="form-submit"><div><b>Ready to build your plan?</b><span>The generated roadmap will appear for review before learning starts.</span></div><button className="button primary" disabled={loading || missing}>{loading ? "Building plan..." : "Generate learning plan →"}</button></div>
        </form>
      </div>
    </AppShell>
  );
}
