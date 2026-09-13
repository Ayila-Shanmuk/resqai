import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useToast } from "../ToastContext.jsx";
import {
  predictSeverity, explainPrediction, saveAccidentLocation,
  sendEmergencyAlert, confirmSafe,
} from "../services/api.js";
import { simulatedSeverityContext } from "../services/sensorSimulator.js";

const COUNTDOWN_SECONDS = 10;
const RING_RADIUS = 52;
const RING_CIRCUMFERENCE = 2 * Math.PI * RING_RADIUS;

export default function AccidentDetected() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const { push } = useToast();

  const accidentId = state?.accidentId;
  const sensors = state?.sensors;
  const reason = state?.reason;

  const [secondsLeft, setSecondsLeft] = useState(COUNTDOWN_SECONDS);
  const [resolving, setResolving] = useState(false);
  const [severityData, setSeverityData] = useState(null);
  const triggeredRef = useRef(false);

  // Redirect home if this page is opened directly without an accident in flight.
  useEffect(() => {
    if (!sensors) navigate("/", { replace: true });
  }, [sensors, navigate]);

  // Kick off severity prediction in the background as soon as the screen opens.
  useEffect(() => {
    if (!sensors) return;
    (async () => {
      try {
        const context = simulatedSeverityContext(sensors);
        if (accidentId) context.accident_id = accidentId;
        const [sevRes, expRes] = await Promise.all([
          predictSeverity(context),
          explainPrediction({ accident_id: accidentId, features: context }),
        ]);
        setSeverityData({ ...sevRes.data, explanation: expRes.data });
        if (accidentId && sensors.latitude && sensors.longitude) {
          saveAccidentLocation({ accident_id: accidentId, latitude: sensors.latitude, longitude: sensors.longitude }).catch(() => {});
        }
      } catch (err) {
        // Non-fatal: the confirmation flow still works without severity data
      }
    })();
  }, [sensors, accidentId]);

  useEffect(() => {
    if (!sensors || resolving) return;
    if (secondsLeft <= 0) {
      triggerEmergency();
      return;
    }
    const timer = setTimeout(() => setSecondsLeft((s) => s - 1), 1000);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [secondsLeft, sensors, resolving]);

  const triggerEmergency = async () => {
    if (triggeredRef.current) return;
    triggeredRef.current = true;
    setResolving(true);
    try {
      const severity = severityData?.severity || "Moderate";
      const res = accidentId
        ? await sendEmergencyAlert({
            accident_id: accidentId,
            severity,
            latitude: sensors.latitude,
            longitude: sensors.longitude,
          })
        : { data: null };
      navigate("/emergency-response", {
        replace: true,
        state: { accidentId, sensors, severityData, alert: res.data },
      });
    } catch (err) {
      push(err.friendlyMessage || "Could not send emergency alert.", "error");
      setResolving(false);
      triggeredRef.current = false;
    }
  };

  const handleImSafe = async () => {
    setResolving(true);
    try {
      if (accidentId) await confirmSafe(accidentId);
      push("Marked as false alarm. Glad you're safe.", "success");
      navigate("/", { replace: true });
    } catch (err) {
      push(err.friendlyMessage || "Could not update accident status.", "error");
      setResolving(false);
    }
  };

  if (!sensors) return null;

  const progress = secondsLeft / COUNTDOWN_SECONDS;
  const dashOffset = RING_CIRCUMFERENCE * (1 - progress);

  return (
    <div className="emergency-overlay">
      <div className="emergency-modal">
        <div className="emergency-icon">
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none">
            <path d="M12 9v4M12 17h.01M10.3 3.9 1.8 18a1.8 1.8 0 0 0 1.55 2.7h17.3a1.8 1.8 0 0 0 1.55-2.7L13.7 3.9a1.8 1.8 0 0 0-3.4 0Z"
              stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        <h2 className="emergency-title">Possible accident detected!</h2>
        <p className="emergency-desc">
          {reason || "Strong impact and motion signature detected."} Confirm your status
          before an emergency alert is sent automatically.
        </p>

        <div className="countdown-ring-wrap">
          <svg width="120" height="120" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r={RING_RADIUS} fill="none" stroke="var(--border)" strokeWidth="8" />
            <circle
              cx="60" cy="60" r={RING_RADIUS} fill="none" stroke="var(--danger)" strokeWidth="8"
              strokeLinecap="round" strokeDasharray={RING_CIRCUMFERENCE} strokeDashoffset={dashOffset}
              transform="rotate(-90 60 60)" style={{ transition: "stroke-dashoffset 1s linear" }}
            />
          </svg>
          <div className="countdown-number">{secondsLeft}</div>
        </div>

        {severityData && (
          <p className="text-muted text-sm mt-8" style={{ marginBottom: 18 }}>
            Estimated severity: <strong style={{ color: "var(--text)" }}>{severityData.severity}</strong>
          </p>
        )}

        <div className="emergency-actions">
          <button className="btn btn-safe btn-lg" disabled={resolving} onClick={handleImSafe}>
            I'M SAFE
          </button>
          <button className="btn btn-danger btn-lg" disabled={resolving} onClick={triggerEmergency}>
            {resolving ? <span className="spinner" /> : "SEND EMERGENCY ALERT NOW"}
          </button>
        </div>
      </div>
    </div>
  );
}
