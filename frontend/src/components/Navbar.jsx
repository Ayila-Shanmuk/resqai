import { NavLink } from "react-router-dom";
import { useAuth } from "../AuthContext.jsx";

const icons = {
  dashboard: (
    <svg viewBox="0 0 20 20" fill="none"><path d="M3 10.5 10 4l7 6.5M5 9v7h4v-4h2v4h4V9" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/></svg>
  ),
  hospital: (
    <svg viewBox="0 0 20 20" fill="none"><rect x="3" y="4" width="14" height="13" rx="1.5" stroke="currentColor" strokeWidth="1.6"/><path d="M10 8v5M7.5 10.5h5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/></svg>
  ),
  history: (
    <svg viewBox="0 0 20 20" fill="none"><path d="M10 5v5l3.5 2" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/><circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="1.6"/></svg>
  ),
};

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <div className="navbar-brand-mark">R</div>
        <div>
          <div className="navbar-brand-text">ResQAI</div>
          <div className="navbar-brand-sub">Accident Response</div>
        </div>
      </div>

      <div className="navbar-links">
        <NavLink to="/" end className={({ isActive }) => `navbar-link${isActive ? " active" : ""}`}>
          <span className="navbar-link-icon">{icons.dashboard}</span> Dashboard
        </NavLink>
        <NavLink to="/hospitals" className={({ isActive }) => `navbar-link${isActive ? " active" : ""}`}>
          <span className="navbar-link-icon">{icons.hospital}</span> Hospitals
        </NavLink>
        <NavLink to="/history" className={({ isActive }) => `navbar-link${isActive ? " active" : ""}`}>
          <span className="navbar-link-icon">{icons.history}</span> Accident History
        </NavLink>
      </div>

      <div className="navbar-footer">
        <div className="navbar-user">{user?.name}</div>
        <div className="navbar-user-sub">{user?.phone}</div>
        <button className="navbar-logout" onClick={logout}>Log out</button>
      </div>
    </nav>
  );
}
