import { useEffect, useState } from "react";
import { useToast } from "../ToastContext.jsx";
import { getAccidentHistory } from "../services/api.js";

const STATUS_LABEL = {
  pending: "Pending",
  confirmed: "Emergency Sent",
  false_alarm: "False Alarm",
  resolved: "Resolved",
};

export default function AccidentHistory() {
  const { push } = useToast();
  const [accidents, setAccidents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await getAccidentHistory();
        setAccidents(res.data);
      } catch (err) {
        push(err.friendlyMessage || "Could not load accident history.", "error");
      } finally {
        setLoading(false);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Accident History</h1>
          <div className="page-subtitle">All detected and simulated events for your account</div>
        </div>
      </div>

      <div className="card">
        {loading ? (
          <div className="text-muted text-sm"><span className="spinner" /> Loading…</div>
        ) : accidents.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-title">No events yet</div>
            <div className="text-sm">Run a simulation from the dashboard to see history here.</div>
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table className="history-table">
              <thead>
                <tr>
                  <th>Date &amp; Time</th>
                  <th>Location</th>
                  <th>Severity</th>
                  <th>Detection</th>
                  <th>Response Status</th>
                  <th>Hospital</th>
                </tr>
              </thead>
              <tbody>
                {accidents.map((a) => (
                  <tr key={a.id}>
                    <td>{new Date(a.timestamp).toLocaleString()}</td>
                    <td>{a.latitude ? `${a.latitude.toFixed(3)}, ${a.longitude.toFixed(3)}` : "—"}</td>
                    <td>
                      {a.severity
                        ? <span className={`badge badge-${a.severity.toLowerCase()}`}>{a.severity}</span>
                        : <span className="badge badge-neutral">N/A</span>}
                    </td>
                    <td className="text-muted">{a.detection_status.replaceAll("_", " ")}</td>
                    <td>{STATUS_LABEL[a.status] || a.status}</td>
                    <td className="text-muted">{a.hospital || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
