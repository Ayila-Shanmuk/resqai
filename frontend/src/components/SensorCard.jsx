export default function SensorCard({ sensors }) {
  const tiles = [
    { label: "Accel X", value: sensors.accelerometer_x, unit: "m/s²" },
    { label: "Accel Y", value: sensors.accelerometer_y, unit: "m/s²" },
    { label: "Accel Z", value: sensors.accelerometer_z, unit: "m/s²" },
    { label: "Gyro X", value: sensors.gyroscope_x, unit: "rad/s" },
    { label: "Gyro Y", value: sensors.gyroscope_y, unit: "rad/s" },
    { label: "Gyro Z", value: sensors.gyroscope_z, unit: "rad/s" },
  ];

  return (
    <div className="card">
      <div className="card-title">Live Sensor Readings</div>
      <div className="grid grid-3">
        {tiles.map((t) => (
          <div className="data-tile" key={t.label}>
            <div className="data-tile-label">{t.label}</div>
            <div className="data-tile-value">
              {t.value !== undefined && t.value !== null ? t.value.toFixed(2) : "--"}
              <span className="data-tile-unit">{t.unit}</span>
            </div>
          </div>
        ))}
      </div>
      <div className="grid grid-2 mt-16">
        <div className="data-tile">
          <div className="data-tile-label">Speed</div>
          <div className="data-tile-value">
            {sensors.speed !== undefined ? sensors.speed.toFixed(1) : "--"}
            <span className="data-tile-unit">km/h</span>
          </div>
        </div>
        <div className="data-tile">
          <div className="data-tile-label">GPS</div>
          <div className="data-tile-value" style={{ fontSize: 14 }}>
            {sensors.latitude ? sensors.latitude.toFixed(4) : "--"}, {sensors.longitude ? sensors.longitude.toFixed(4) : "--"}
          </div>
        </div>
      </div>
    </div>
  );
}
