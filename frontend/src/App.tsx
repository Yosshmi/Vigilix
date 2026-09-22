import { Activity, Camera, ShieldAlert, Users } from "lucide-react";

const stats = [
  { label: "People", value: "0", icon: Users },
  { label: "Vehicles", value: "0", icon: Camera },
  { label: "Events", value: "0", icon: ShieldAlert },
  { label: "FPS", value: "--", icon: Activity },
];

export function App() {
  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">INTELLIGENT VIDEO ANALYTICS</p>
          <h1>Vigilix</h1>
        </div>
        <span className="status-pill">SYSTEM READY</span>
      </header>

      <section className="dashboard-grid">
        <section className="video-panel panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">VIDEO ANALYTICS</p>
              <h2>Analysis workspace</h2>
            </div>
            <button type="button">Select video</button>
          </div>

          <div className="video-placeholder">
            <Camera size={46} />
            <strong>No video selected</strong>
            <span>Upload a surveillance clip to begin analysis.</span>
          </div>
        </section>

        <aside className="metrics">
          {stats.map(({ label, value, icon: Icon }) => (
            <article className="metric-card panel" key={label}>
              <Icon size={20} />
              <span>{label}</span>
              <strong>{value}</strong>
            </article>
          ))}
        </aside>
      </section>

      <section className="panel event-panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">EVENT STREAM</p>
            <h2>Recent detections</h2>
          </div>
        </div>
        <div className="empty-state">Analytics events will appear here.</div>
      </section>
    </main>
  );
}
