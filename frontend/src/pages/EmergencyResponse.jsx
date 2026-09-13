import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext.jsx";
import { useToast } from "../ToastContext.jsx";
import MapView from "../components/MapView.jsx";
import SeverityCard from "../components/SeverityCard.jsx";
import HospitalCard from "../components/HospitalCard.jsx";
import { getNearbyHospitals, confirmSafe } from "../services/api.js";

export default function EmergencyResponse() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { push } = useToast();

  const accidentId = state?.accidentId;
  const sensors = state?.sensors;
  const severityData = state?.severityData;
  const alert = state?.alert;

  const [hospitals, setHospitals] = useState([]);
  const [loadingHospitals, setLoadingHospitals] = useState(true);

  useEffect(() => {
    if (!sensors) {
      navigate("/", { replace: true });
      return;
    }
    (async () => {
      try {
        const res = await getNearbyHospitals(sensors.latitude, sensors.longitude, accidentId);
        setHospitals(res.data);
      } catch (err) {
        push(err.friendlyMessage || "Could not load nearby hospitals.", "error");
      } finally {
        setLoadingHospitals(false);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!sensors) return null;

  const topHospital = hospitals[0];
  const severity = severityData?.severity || "Unknown";

  const handleCancelAlert = async () => {
    try {
      if (accidentId) await confirmSafe(accidentId);
      push("Alert cancelled.", "info");
      navigate("/", { replace: true });
    } catch (err) {
      push(err.friendlyMessage || "Could not cancel alert.", "error");
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">🔴 Emergency Response</h1>
          <div className="page-subtitle">
            {alert?.simulated ? "SIMULATION MODE - no real emergency service was contacted" : "Emergency response in progress"}
          </div>
        </div>
        <span className={`badge badge-${severity.toLowerCase()}`} style={{ fontSize: 14, padding: "7px 16px" }}>
          Severity: {severity.toUpperCase()}
        </span>
      </div>

      {alert?.simulated && (
        <div className="card mt-16" style={{ borderColor: "rgba(242,169,59,0.4)", background: "var(--warn-dim)" }}>
          <strong style={{ color: "var(--warn)" }}>Simulation Mode</strong>
          <p className="text-sm mt-8" style={{ color: "#ffe3b0" }}>
            No real emergency service, SMS, or call has been placed. Configure a real
            provider in <code>services/emergency_service.py</code> to enable live alerts.
          </p>
        </div>
      )}

      <div className="grid grid-2 mt-16">
        <div className="card">
          <div className="card-title">Accident Location</div>
          <MapView latitude={sensors.latitude} longitude={sensors.longitude} height={240} />
          <div className="text-muted text-sm mt-12">
            Lat {sensors.latitude?.toFixed(5)}, Lon {sensors.longitude?.toFixed(5)}
          </div>
        </div>

        <SeverityCard
          severity={severityData?.severity}
          confidence={severityData?.confidence}
          importantFeatures={severityData?.important_features}
        />
      </div>

      <div className="card mt-16">
        <div className="card-title">Recommended Hospital</div>
        {loadingHospitals ? (
          <div className="text-muted text-sm"><span className="spinner" /> Finding nearby hospitals…</div>
        ) : topHospital ? (
          <HospitalCard hospital={topHospital} />
        ) : (
          <div className="text-muted text-sm">No hospital data available.</div>
        )}
      </div>

      <div className="card mt-16">
        <div className="card-title">Emergency Contact</div>
        <div>{user?.emergency_contact_name || "Primary contact"} · {user?.emergency_contact}</div>
      </div>

      {alert?.message && (
        <div className="card mt-16">
          <div className="card-title">Alert Message Sent</div>
          <p className="text-sm" style={{ lineHeight: 1.6 }}>{alert.message}</p>
        </div>
      )}

      <div className="grid grid-2 mt-16" style={{ gridTemplateColumns: "repeat(4, 1fr)" }}>
        <a className="btn btn-danger" href="tel:112">Call Emergency Services</a>
        <a className="btn btn-primary" href={`tel:${user?.emergency_contact}`}>Call Emergency Contact</a>
        {topHospital && (
          <a className="btn btn-ghost" target="_blank" rel="noreferrer"
             href={`https://www.google.com/maps/dir/?api=1&destination=${topHospital.latitude},${topHospital.longitude}`}>
            Hospital Directions
          </a>
        )}
        <button className="btn btn-ghost" onClick={handleCancelAlert}>Cancel Alert</button>
      </div>
    </div>
  );
}
