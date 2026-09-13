// Renders an OpenStreetMap embed (no API key required) centered on the given
// coordinates. If GOOGLE_MAPS_API_KEY is configured on the frontend build,
// this could be swapped for a Google Maps JS embed instead - OSM is used by
// default so the map works out of the box for anyone cloning the project.
export default function MapView({ latitude, longitude, label = "Location", height = 260 }) {
  if (!latitude || !longitude) {
    return (
      <div className="map-view" style={{ minHeight: height }}>
        <div className="map-fallback">No GPS coordinates available yet.</div>
      </div>
    );
  }

  const delta = 0.01;
  const bbox = [longitude - delta, latitude - delta, longitude + delta, latitude + delta].join(",");
  const src = `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&marker=${latitude},${longitude}&layers=M`;
  const directionsUrl = `https://www.google.com/maps?q=${latitude},${longitude}`;

  return (
    <div>
      <div className="map-view" style={{ minHeight: height }}>
        <iframe title={label} src={src} style={{ minHeight: height }} loading="lazy" />
      </div>
      <a href={directionsUrl} target="_blank" rel="noreferrer" className="btn btn-ghost btn-block mt-12">
        Open in Google Maps
      </a>
    </div>
  );
}
