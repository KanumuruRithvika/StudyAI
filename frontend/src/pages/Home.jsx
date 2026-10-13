import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Home() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  return (
    <div className="landing">
      <nav className="landing-nav">
        <button className="brand" onClick={() => navigate("/")}>
          <span className="brand-mark">A</span>
          <span>AgenticLearn</span>
        </button>
        <div className="landing-actions">
          {isAuthenticated ? (
            <button className="button primary" onClick={() => navigate("/dashboard")}>
              Open learning
            </button>
          ) : (
            <>
              <button className="nav-link" onClick={() => navigate("/login")}>Log in</button>
              <button className="button primary" onClick={() => navigate("/signup")}>Get started</button>
            </>
          )}
        </div>
      </nav>

      <section className="hero">
        <div className="hero-copy">
          <div className="pill"><span className="status-pulse" /> Adaptive learning workspace</div>
          <h1>Learn with a plan that <em>changes with you.</em></h1>
          <p>
            AgenticLearn turns your goal, time, current skills and performance
            into an adaptive learning path with daily work, assessment and
            user-controlled next steps.
          </p>
          <div className="hero-actions">
            <button className="button primary large" onClick={() => navigate(isAuthenticated ? "/setup" : "/signup")}>
              Start learning <span>→</span>
            </button>
            <button className="text-action" onClick={() => navigate("/login")}>
              I already have an account
            </button>
          </div>
        </div>

        <div className="hero-visual">
          <div className="orb orb-one" />
          <div className="orb orb-two" />
          <div className="preview-window">
            <div className="preview-top">
              <span className="window-dot" /><span className="window-dot" /><span className="window-dot" />
              <span className="preview-label">Today</span>
            </div>
            <div className="preview-content">
              <span className="preview-kicker">Python fundamentals</span>
              <h3>Day 3 · Decorators</h3>
              <div className="preview-progress"><span /></div>
              <div className="preview-task done">
                <span className="mini-check">✓</span>
                <div><b>Understand decorators</b><small>20 min · Complete</small></div>
              </div>
              <div className="preview-task active">
                <span className="mini-number">2</span>
                <div><b>Build a practical decorator</b><small>40 min · In progress</small></div>
              </div>
              <div className="preview-insight">
                <span>✦</span>
                <div><b>Adaptive insight</b><small>Your next assessment focuses on applied usage.</small></div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
