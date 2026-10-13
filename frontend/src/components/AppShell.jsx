import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { clearSessionId } from "../api/api";

export default function AppShell({ children, title, eyebrow, showBack = false }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function continueLearning() {
    clearSessionId();
    navigate("/setup");
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <button className="brand" onClick={() => navigate("/dashboard")} aria-label="Go to learning workspace">
          <span className="brand-mark">A</span><span>AgenticLearn</span>
        </button>
        <nav className="topbar-right" aria-label="Primary navigation">
          <button className="nav-link" onClick={() => navigate("/dashboard")}>Learning</button>
          <button className="nav-link" onClick={() => navigate("/report")}>Report</button>
          <button className="nav-link accent-link" onClick={continueLearning}>+ Continue learning</button>
          <div className="user-menu">
            <span className="avatar">{(user?.name || user?.email || "U").slice(0, 1).toUpperCase()}</span>
            <button className="nav-link" onClick={() => { clearSessionId(); logout(); navigate("/login", { replace: true }); }}>Sign out</button>
          </div>
        </nav>
      </header>
      <main className="page-frame">
        {showBack && <button className="back-link" onClick={() => navigate(-1)}>← Back</button>}
        {(eyebrow || title) && <div className="page-heading">{eyebrow && <span className="eyebrow">{eyebrow}</span>}{title && <h1>{title}</h1>}</div>}
        {children}
      </main>
    </div>
  );
}
