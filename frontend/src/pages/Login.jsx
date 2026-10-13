import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(form);
      navigate(location.state?.from?.pathname || "/dashboard", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <button className="brand auth-brand" onClick={() => navigate("/")}>
          <span className="brand-mark">A</span>
          <span>AgenticLearn</span>
        </button>

        <div className="auth-heading">
          <span className="eyebrow">Welcome back</span>
          <h1>Continue learning.</h1>
          <p>Sign in to return to your adaptive workspace.</p>
        </div>

        {error && <div className="form-error">{error}</div>}

        <form onSubmit={handleSubmit} className="form">
          <label>
            Email <span>*</span>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              placeholder="you@example.com"
              autoComplete="email"
              required
            />
          </label>

          <label>
            Password <span>*</span>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder="Enter your password"
              autoComplete="current-password"
              required
            />
          </label>

          <button className="button primary full" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <p className="auth-footer">
          New to AgenticLearn? <Link to="/signup">Create an account</Link>
        </p>
      </div>
    </div>
  );
}
  