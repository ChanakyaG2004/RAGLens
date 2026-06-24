import { useEffect, useState } from "react";
import { getTraces } from "../api";
import TraceCard from "../components/TraceCard";

export default function Traces({ setPage }) {
  const [traces, setTraces] = useState([]),
    [error, setError] = useState(""),
    [loading, setLoading] = useState(true);
  async function load() {
    setLoading(true);
    try {
      setTraces(await getTraces());
      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    load();
  }, []);
  return (
    <section className="py-12">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="eyebrow">Observability</p>
          <h1 className="mt-3 text-3xl font-bold">Trace Viewer</h1>
          <p className="mt-2 text-slate-400">
            Inspect the evidence and prompt behind every generated answer.
          </p>
        </div>
        <button onClick={load} className="action-secondary">
          {loading ? "Loading…" : "Refresh traces"}
        </button>
      </div>
      {error && (
        <div className="mt-7 rounded-xl border border-rose-900/70 bg-rose-950/30 p-4 text-sm text-rose-200">
          Could not load traces: {error}
        </div>
      )}
      {!loading && !error && !traces.length && (
        <div className="panel mt-8 p-10 text-center">
          <p className="text-lg font-semibold">No traces yet</p>
          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-400">
            Ask a question after indexing a document and each complete RAG run
            will appear here.
          </p>
          <button
            onClick={() => setPage("ask")}
            className="action-primary mt-6"
          >
            Ask a question
          </button>
        </div>
      )}
      <div className="mt-8 grid gap-6">
        {traces.map((trace) => (
          <TraceCard key={trace.id} trace={trace} />
        ))}
      </div>
    </section>
  );
}
