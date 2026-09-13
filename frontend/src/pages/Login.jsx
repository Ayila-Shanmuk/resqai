import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext.jsx";
import { useToast } from "../ToastContext.jsx";

export default function Login() {
  const { login } = useAuth();
  const { push } = useToast();
  const navigate = useNavigate();

  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const user = await login(form.email, form.password);
      push(`Welcome back, ${user.name.split(" ")[0]}.`, "success");
      navigate("/");
    } catch (err) {
      setError(err.friendlyMessage || "Login failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-main-auth">
      <div className="auth-side">
        <div>
          <div className="auth-side-mark">R</div>
          <div className="auth-side-title">Every second counts after a crash.</div>
          <div className="auth-side-desc">
            ResQAI watches for sudden impact signatures from your phone's sensors,
            estimates severity with a trained model, and gets your emergency
            contacts and the nearest hospital involved automatically.
          </div>
        </div>
        <div>
          <div className="auth-side-feature">🟢 Automatic crash detection from motion sensors</div>
          <div className="auth-side-feature">🧠 ML-based severity scoring with explainability</div>
          <div className="auth-side-feature">🏥 Nearest hospital lookup with directions</div>
          <div className="auth-side-feature">⏱ 10-second confirmation window to cancel false alarms</div>
        </div>
      </div>

      <div className="auth-wrap">
        <div className="auth-card">
          <h1 style={{ fontSize: 22 }}>Log in to ResQAI</h1>
          <p className="text-muted text-sm mt-8 mb-16">Access your safety dashboard.</p>

          {error && <div className="form-error">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input className="form-input" type="email" name="email" required
                value={form.email} onChange={handleChange} placeholder="you@example.com" />
            </div>
            <div className="form-group">
              <label className="form-label">Password</label>
              <input className="form-input" type="password" name="password" required
                value={form.password} onChange={handleChange} placeholder="••••••••" />
            </div>
            <button className="btn btn-primary btn-block btn-lg mt-16" disabled={loading}>
              {loading ? <span className="spinner" /> : "Log in"}
            </button>
          </form>

          <div className="auth-switch">
            Don't have an account? <Link to="/register">Create one</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
