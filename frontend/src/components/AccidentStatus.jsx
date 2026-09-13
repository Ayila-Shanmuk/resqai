// Big hero card at the top of the dashboard showing the current safety state.
// status: "normal" | "suspicious" | "possible_accident"
const STATUS_META = {
  normal: { cls: "safe", label: "SAFE", emoji: "🟢", desc: "No unusual motion detected. Driving normally." },
  suspicious: { cls: "suspicious", label: "POSSIBLE ACCIDENT", emoji: "🟡", desc: "Unusual sensor activity detected. Monitoring closely." },
  possible_accident: { cls: "accident", label: "ACCIDENT DETECTED", emoji: "🔴", desc: "Strong impact signature detected. Confirmation required." },
};

export default function AccidentStatus({ status, reason, onSimulateSafe }) {
  const meta = STATUS_META[status] || STATUS_META.normal;

  return (
    <div className={`status-hero status-${meta.cls}`}>
      <div className="status-hero-left">
        <span className={`status-dot ${meta.cls === "safe" ? "safe" : meta.cls === "suspicious" ? "suspicious" : "accident"}`} />
        <div>
          <div className="status-hero-label">Current Status</div>
          <div className="status-hero-value">{meta.emoji} {meta.label}</div>
          {reason && <div className="text-muted text-sm mt-8">{reason}</div>}
          {!reason && <div className="text-muted text-sm mt-8">{meta.desc}</div>}
        </div>
      </div>
    </div>
  );
}
