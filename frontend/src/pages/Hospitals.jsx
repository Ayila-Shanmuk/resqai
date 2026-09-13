import { useEffect, useState } from "react";
import { useToast } from "../ToastContext.jsx";
import HospitalCard from "../components/HospitalCard.jsx";
import MapView from "../components/MapView.jsx";
import { getNearbyHospitals } from "../services/api.js";

const DEFAULT_LAT = 17.385;
const DEFAULT_LON = 78.4867;

export default function Hospitals() {
  const { push } = useToast();
  const [coords, setCoords] = useState({ latitude: DEFAULT_LAT, longitude: DEFAULT_LON });
  const [hospitals, setHospitals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [usingBrowserLocation, setUsingBrowserLocation] = useState(false);

  const search = async (lat, lon) => {
    setLoading(true);
    try {
      const res = await getNearbyHospitals(lat, lon);
      setHospitals(res.data);
    } catch (err) {
      push(err.friendlyMessage || "Could not load hospitals.", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    search(coords.latitude, coords.longitude);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const useMyLocation = () => {
    if (!navigator.geolocation) {
      push("Geolocation isn't available in this browser.", "error");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const c = { latitude: pos.coords.latitude, longitude: pos.coords.longitude };
        setCoords(c);
        setUsingBrowserLocation(true);
        search(c.latitude, c.longitude);
      },
      () => push("Couldn't get your location - showing default area instead.", "warning")
    );
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Nearby Hospitals</h1>
          <div className="page-subtitle">
            {usingBrowserLocation ? "Based on your current location" : "Based on default demo location - Hyderabad"}
          </div>
        </div>
        <button className="btn btn-ghost" onClick={useMyLocation}>Use My Location</button>
      </div>

      <div className="grid grid-2 mt-16">
        <MapView latitude={coords.latitude} longitude={coords.longitude} height={320} />
        <div className="card">
          <div className="card-title">Results {loading ? "" : `(${hospitals.length})`}</div>
          {loading ? (
            <div className="text-muted text-sm"><span className="spinner" /> Searching…</div>
          ) : hospitals.length === 0 ? (
            <div className="text-muted text-sm">No hospitals found near this location.</div>
          ) : (
            <div style={{ maxHeight: 420, overflowY: "auto" }}>
              {hospitals.map((h, i) => <HospitalCard key={i} hospital={h} />)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
