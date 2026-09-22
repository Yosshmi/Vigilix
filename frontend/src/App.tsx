import { ChangeEvent, useEffect, useMemo, useRef, useState } from "react";
import { Activity, Camera, ShieldAlert, Upload, Users } from "lucide-react";

import {
  AnalysisResult,
  getResult,
  getStatus,
  startAnalysis,
  uploadVideo,
} from "./services/api";

export function App() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [videoId, setVideoId] = useState<string | null>(null);
  const [status, setStatus] = useState("idle");
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!videoId || !["queued", "processing"].includes(status)) {
      return;
    }

    const timer = window.setInterval(async () => {
      try {
        const latest = await getStatus(videoId);
        setStatus(latest.status);
        setProgress(latest.progress);

        if (latest.status === "completed") {
          const completed = await getResult(videoId);
          setResult(completed);
          setBusy(false);
        }

        if (latest.status === "failed") {
          setError(latest.error ?? "Analysis failed.");
          setBusy(false);
        }
      } catch (requestError) {
        setError(
          requestError instanceof Error ? requestError.message : "Unable to read analysis status.",
        );
        setBusy(false);
      }
    }, 1500);

    return () => window.clearInterval(timer);
  }, [videoId, status]);

  const metrics = useMemo(
    () => [
      {
        label: "Occupancy",
        value: String(result?.analytics.occupancy ?? 0),
        icon: Users,
      },
      {
        label: "Active tracks",
        value: String(result?.analytics.active_tracks ?? 0),
        icon: Camera,
      },
      {
        label: "Events",
        value: String(result?.events.length ?? 0),
        icon: ShieldAlert,
      },
      {
        label: "FPS",
        value: result ? result.average_fps.toFixed(1) : "--",
        icon: Activity,
      },
    ],
    [result],
  );

  function onFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null;
    setSelectedFile(file);
    setVideoId(null);
    setResult(null);
    setError(null);
    setStatus(file ? "selected" : "idle");
    setProgress(0);
  }

  async function runAnalysis() {
    if (!selectedFile) {
      inputRef.current?.click();
      return;
    }

    setBusy(true);
    setError(null);

    try {
      setStatus("uploading");
      const uploaded = await uploadVideo(selectedFile);
      setVideoId(uploaded.video_id);
      setStatus(uploaded.status);
      await startAnalysis(uploaded.video_id);
      setStatus("queued");
    } catch (requestError) {
      setError(
        requestError instanceof Error ? requestError.message : "Unable to start analysis.",
      );
      setBusy(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">INTELLIGENT VIDEO ANALYTICS</p>
          <h1>Vigilix</h1>
          <p className="subtitle">Object detection, tracking and surveillance event analysis.</p>
        </div>
        <span className="status-pill">{status.replaceAll("_", " ").toUpperCase()}</span>
      </header>

      <section className="dashboard-grid">
        <section className="video-panel panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">VIDEO ANALYTICS</p>
              <h2>Analysis workspace</h2>
            </div>
            <div className="actions">
              <input
                ref={inputRef}
                type="file"
                accept="video/mp4,video/quicktime,video/x-msvideo,video/x-matroska"
                hidden
                onChange={onFileChange}
              />
              <button className="secondary-button" type="button" onClick={() => inputRef.current?.click()}>
                <Upload size={16} />
                Select video
              </button>
              <button type="button" disabled={!selectedFile || busy} onClick={runAnalysis}>
                {busy ? "Analyzing..." : "Run analysis"}
              </button>
            </div>
          </div>

          {result ? (
            <video className="result-video" controls src={result.output_url} />
          ) : (
            <div className="video-placeholder">
              <Camera size={46} />
              <strong>{selectedFile?.name ?? "No video selected"}</strong>
              <span>
                {selectedFile
                  ? "Ready for detection, tracking and event analysis."
                  : "Upload a surveillance clip to begin analysis."}
              </span>
            </div>
          )}

          {busy && (
            <div className="progress-wrap" aria-label="Analysis progress">
              <div className="progress-track">
                <div className="progress-value" style={{ width: `${Math.max(progress * 100, 8)}%` }} />
              </div>
              <span>{status === "queued" ? "Queued" : "Processing video"}</span>
            </div>
          )}

          {error && <div className="error-message">{error}</div>}
        </section>

        <aside className="metrics">
          {metrics.map(({ label, value, icon: Icon }) => (
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
            <h2>Detected surveillance events</h2>
          </div>
          {result && (
            <span className="summary-copy">
              {result.frame_count} frames · {result.processing_seconds.toFixed(1)}s processing
            </span>
          )}
        </div>

        {result?.events.length ? (
          <div className="event-list">
            {result.events.map((event) => (
              <article className="event-row" key={event.id}>
                <div>
                  <strong>{event.event_type.replaceAll("_", " ")}</strong>
                  <span>
                    {event.object_class} #{event.track_id}
                  </span>
                </div>
                <div>
                  <strong>{event.timestamp_seconds.toFixed(1)}s</strong>
                  <span>{Math.round(event.confidence * 100)}% confidence</span>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="empty-state">Analytics events will appear here after processing.</div>
        )}
      </section>
    </main>
  );
}
