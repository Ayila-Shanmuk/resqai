import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext.jsx";
import { useToast } from "../ToastContext.jsx";
import AccidentStatus from "../components/AccidentStatus.jsx";
import SensorCard from "../components/SensorCard.jsx";
import MapView from "../components/MapView.jsx";
import { detectAccident, getAccidentHistory } from "../services/api.js";
import { simulateNormalDriving, simulateSuddenImpact, simulateSeriousAccident } from "../services/sensorSimulator.js";

export default function Dashboard() {
  const { user } = useAuth();
  const { push } = useToast();
  const navigate = useNavigate();

  const [sensors, setSensors] = useState(simulateNormalDriving());
  const [status, setStatus] = useState("normal");
  const [reason, setReason] = useState("");
  const [simulating, setSimulating] = useState(null);
  const [recent, setRecent] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoadingHistory(true);
    try {
      const res = await getAccidentHistory();
      setRecent(res.data.slice(0, 4));
    } catch (err) {
      // Non-fatal on the dashboard - just show an empty recent list
    } finally {
      setLoadingHistory(false);
    }
  };

  const runSimulation = async (kind, generator) => {
    setSimulating(kind);
    const reading = generator();
    setSensors(reading);
    try {
      const res = await detectAccident(reading);
      setStatus(res.data.status);
      setReason(res.data.reason);

      if (res.data.status === "possible_accident") {
        navigate("/accident-detected", {
          state: { accidentId: res.data.accident_id, sensors: reading, reason: res.data.reason },
        });
      } else if (res.data.status === "suspicious") {
        push("Unusual motion detected - monitoring.", "warning");
      } else {
        push("Sensor check complete - all normal.", "success");
      }
    } catch (err) {
      push(err.friendlyMessage || "Could not run detection.", "error");
    } finally {
      setSimulating(null);
      loadHistory();
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Welcome back, {user?.name?.split(" ")[0]}</h1>
          <div className="page-subtitle">Live safety overview and simulation mode</div>
        </div>
      </div>

      <AccidentStatus status={status} reason={reason} />

      <div className="card mt-16">
        <div className="card-title">Simulation Mode</div>
        <p className="text-muted text-sm mb-16">
          Desktop browsers don't expose real accelerometer/gyroscope data, so use these
          buttons to generate realistic sensor readings and exercise the full detection
          → severity → hospital → emergency-alert pipeline.
        </p>
        <div className="sim-panel">
          <button className="btn btn-safe" disabled={!!simulating} onClick={() => runSimulation("normal", simulateNormalDriving)}>
            {simulating === "normal" ? <span className="spinner" /> : "Simulate Normal Driving"}
          </button>
          <button className="btn btn-warn" disabled={!!simulating} onClick={() => runSimulation("impact", simulateSuddenImpact)}>
            {simulating === "impact" ? <span className="spinner" /> : "Simulate Sudden Impact"}
          </button>
          <button className="btn btn-danger" disabled={!!simulating} onClick={() => runSimulation("accident", simulateSeriousAccident)}>
            {simulating === "accident" ? <span className="spinner" /> : "Simulate Serious Accident"}
          </button>
        </div>
      </div>

      <div className="grid grid-2 mt-16">
        <SensorCard sensors={sensors} />
        <div className="card">
          <div className="card-title">Current Location</div>
          <MapView latitude={sensors.latitude} longitude={sensors.longitude} height={220} />
        </div>
      </div>

      <div className="grid grid-2 mt-16">
        <div className="card">
          <div className="card-title">Emergency Contact</div>
          <div className="flex items-center gap-12">
            <span className="status-dot safe" />
            <div>
              <div style={{ fontWeight: 600 }}>{user?.emergency_contact_name || "Primary contact"}</div>
              <div className="text-muted text-sm">{user?.emergency_contact}</div>
            </div>
          </div>
          <div className="text-faint text-sm mt-16">
            This contact is alerted automatically if a serious accident is confirmed.
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-16">
            <div className="card-title" style={{ marginBottom: 0 }}>Recent Accident History</div>
            <a href="/history" className="text-sm" style={{ color: "var(--info)" }}>View all</a>
          </div>
          {loadingHistory ? (
            <div className="text-muted text-sm">Loading…</div>
          ) : recent.length === 0 ? (
            <div className="text-muted text-sm">No events recorded yet. Try a simulation above.</div>
          ) : (
            recent.map((a) => (
              <div key={a.id} className="flex items-center justify-between" style={{ padding: "8px 0", borderBottom: "1px solid var(--border-soft)" }}>
                <div className="text-sm">{new Date(a.timestamp).toLocaleString()}</div>
                <span className={`badge badge-${(a.severity || "neutral").toLowerCase()}`}>{a.severity || a.detection_status}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
