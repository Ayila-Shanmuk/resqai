import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext.jsx";
import { useToast } from "../ToastContext.jsx";

export default function Register() {
  const { register } = useAuth();
  const { push } = useToast();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "", email: "", phone: "", emergency_contact_name: "",
    emergency_contact: "", password: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const user = await register(form);
      push(`Account created. Welcome, ${user.name.split(" ")[0]}.`, "success");
      navigate("/");
    } catch (err) {
      setError(err.friendlyMessage || "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-main-auth">
      <div className="auth-side">
        <div>
          <div className="auth-side-mark">R</div>
          <div className="auth-side-title">Set up your safety profile.</div>
          <div className="auth-side-desc">
            Your emergency contact is notified automatically the moment a serious
            accident is confirmed - with your live location and severity, so
            help can reach you faster.
          </div>
        </div>
      </div>

      <div className="auth-wrap">
        <div className="auth-card">
          <h1 style={{ fontSize: 22 }}>Create your account</h1>
          <p className="text-muted text-sm mt-8 mb-16">Takes under a minute.</p>

          {error && <div className="form-error">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Full name</label>
              <input className="form-input" name="name" required value={form.name} onChange={handleChange} placeholder="Jane Doe" />
            </div>
            <div className="form-row form-group">
              <div>
                <label className="form-label">Email</label>
                <input className="form-input" type="email" name="email" required value={form.email} onChange={handleChange} placeholder="you@example.com" />
              </div>
              <div>
                <label className="form-label">Phone number</label>
                <input className="form-input" name="phone" required value={form.phone} onChange={handleChange} placeholder="+91 90000 00000" />
              </div>
            </div>
            <div className="form-row form-group">
              <div>
                <label className="form-label">Emergency contact name</label>
                <input className="form-input" name="emergency_contact_name" value={form.emergency_contact_name} onChange={handleChange} placeholder="Optional" />
              </div>
              <div>
                <label className="form-label">Emergency contact number</label>
                <input className="form-input" name="emergency_contact" required value={form.emergency_contact} onChange={handleChange} placeholder="+91 90000 00001" />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Password</label>
              <input className="form-input" type="password" name="password" required minLength={6} value={form.password} onChange={handleChange} placeholder="At least 6 characters" />
            </div>
            <button className="btn btn-primary btn-block btn-lg mt-16" disabled={loading}>
              {loading ? <span className="spinner" /> : "Create account"}
            </button>
          </form>

          <div className="auth-switch">
            Already have an account? <Link to="/login">Log in</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
