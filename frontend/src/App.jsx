import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./AuthContext.jsx";
import { ToastProvider } from "./ToastContext.jsx";
import Navbar from "./components/Navbar.jsx";

import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import AccidentDetected from "./pages/AccidentDetected.jsx";
import EmergencyResponse from "./pages/EmergencyResponse.jsx";
import Hospitals from "./pages/Hospitals.jsx";
import AccidentHistory from "./pages/AccidentHistory.jsx";

function ProtectedRoute({ children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function AppShell({ children }) {
  const { user } = useAuth();
  return (
    <div className="app-shell">
      {user && <Navbar />}
      <main className={user ? "app-main" : "app-main app-main-auth"}>{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <AppShell>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/accident-detected"
            element={
              <ProtectedRoute>
                <AccidentDetected />
              </ProtectedRoute>
            }
          />
          <Route
            path="/emergency-response"
            element={
              <ProtectedRoute>
                <EmergencyResponse />
              </ProtectedRoute>
            }
          />
          <Route
            path="/hospitals"
            element={
              <ProtectedRoute>
                <Hospitals />
              </ProtectedRoute>
            }
          />
          <Route
            path="/history"
            element={
              <ProtectedRoute>
                <AccidentHistory />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppShell>
    </ToastProvider>
  );
}
