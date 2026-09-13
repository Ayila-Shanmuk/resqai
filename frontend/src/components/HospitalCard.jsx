export default function HospitalCard({ hospital }) {
  const directionsUrl = `https://www.google.com/maps/dir/?api=1&destination=${hospital.latitude},${hospital.longitude}`;

  return (
    <div className="hospital-card">
      <div>
        <div className="hospital-name">{hospital.name}</div>
        <div className="hospital-meta">
          {hospital.address}
          {hospital.phone && <> · {hospital.phone}</>}
          {hospital.is_mock_data && <> · <span className="text-faint">sample data</span></>}
        </div>
      </div>
      <div className="flex items-center gap-12">
        <div className="hospital-distance">{hospital.distance_km} km</div>
        <a href={directionsUrl} target="_blank" rel="noreferrer" className="btn btn-ghost">Directions</a>
      </div>
    </div>
  );
}
