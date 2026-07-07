import { useEffect, useState } from "react";

type HealthState =
  | { status: "checking" }
  | { status: "online"; service: string; version: string }
  | { status: "offline"; message: string };

const apiBase = import.meta.env.VITE_HELIXSCOPE_API_BASE ?? "http://127.0.0.1:8000";

export default function App() {
  const [health, setHealth] = useState<HealthState>({ status: "checking" });

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${apiBase}/health`, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        return response.json() as Promise<{ service: string; version: string }>;
      })
      .then((data) => setHealth({ status: "online", service: data.service, version: data.version }))
      .catch((error: Error) => {
        if (error.name !== "AbortError") {
          setHealth({ status: "offline", message: error.message });
        }
      });
    return () => controller.abort();
  }, []);

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <h1>HelixScope</h1>
          <p>ScopeView</p>
        </div>
        <StatusPill health={health} />
      </header>

      <section className="workspace" aria-label="ScopeView workspace">
        <aside className="sidebar">
          <button type="button" className="navButton active">
            LocusProbe
          </button>
          <button type="button" className="navButton">
            ControlDeck
          </button>
          <button type="button" className="navButton">
            EvidenceRelay
          </button>
        </aside>

        <section className="viewer">
          <div className="trackHeader">
            <span>Report viewer</span>
            <span>{apiBase}</span>
          </div>
          <div className="trackCanvas">
            <div className="axis" />
            <div className="track blue" />
            <div className="track orange" />
            <div className="track green" />
            <div className="motifLane">
              <span />
              <span />
              <span />
            </div>
          </div>
        </section>
      </section>
    </main>
  );
}

function StatusPill({ health }: { health: HealthState }) {
  if (health.status === "checking") {
    return <span className="status checking">Checking</span>;
  }
  if (health.status === "online") {
    return (
      <span className="status online">
        {health.service} {health.version}
      </span>
    );
  }
  return <span className="status offline">Offline</span>;
}
