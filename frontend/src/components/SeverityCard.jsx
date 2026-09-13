const BADGE_CLASS = {
  Low: "badge-low",
  Moderate: "badge-moderate",
  High: "badge-high",
  Critical: "badge-critical",
};

export default function SeverityCard({ severity, confidence, importantFeatures }) {
  if (!severity) {
    return (
      <div className="card">
        <div className="card-title">Severity Assessment</div>
        <div className="text-muted text-sm">No prediction yet.</div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-title">Severity Assessment</div>
      <div className="flex items-center gap-12">
        <span className={`badge ${BADGE_CLASS[severity] || "badge-neutral"}`} style={{ fontSize: 14, padding: "6px 14px" }}>
          {severity.toUpperCase()}
        </span>
        <span className="text-muted text-sm">
          {Math.round((confidence || 0) * 100)}% model confidence
        </span>
      </div>
      {importantFeatures?.length > 0 && (
        <div className="mt-16">
          <div className="text-faint text-sm mb-16">Main contributing factors</div>
          <ol style={{ margin: 0, paddingLeft: 18, color: "var(--text)", fontSize: 13.5 }}>
            {importantFeatures.map((f) => (
              <li key={f} style={{ marginBottom: 4 }}>{f.replaceAll("_", " ")}</li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
