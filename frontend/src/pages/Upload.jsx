import { useEffect, useState } from "react";
import { uploadDocument } from "../api";

export default function Upload({ setPage }) {
  const [file, setFile] = useState(null),
    [status, setStatus] = useState(""),
    [busy, setBusy] = useState(false),
    [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    if (!busy) return;
    const timer = setInterval(() => setElapsed((value) => value + 1), 1000);
    return () => clearInterval(timer);
  }, [busy]);
  async function submit(event) {
    event.preventDefault();
    if (!file) return;
    setBusy(true);
    setElapsed(0);
    setStatus("Preparing document and generating embeddings…");
    try {
      const result = await uploadDocument(file);
      setStatus(
        `Indexed ${result.filename} into ${result.chunk_count} chunk${result.chunk_count === 1 ? "" : "s"}.`,
      );
      setFile(null);
    } catch (error) {
      setStatus(error.message);
    } finally {
      setBusy(false);
    }
  }
  const isSuccess = status.startsWith("Indexed");
  return (
    <section className="max-w-3xl py-12">
      <p className="eyebrow">Knowledge sources</p>
      <h1 className="mt-3 text-3xl font-bold">Upload and index documents</h1>
      <p className="mt-2 max-w-xl text-slate-400">
        Add a UTF-8 `.txt`, `.md`, or text-based `.pdf` source. RAGLens extracts
        text, creates overlapping chunks, and stores vectors for retrieval.
      </p>
      <form onSubmit={submit} className="panel mt-8 p-6 sm:p-8">
        <div className="rounded-xl border border-dashed border-slate-700 bg-slate-950/40 p-7 text-center">
          <div className="mx-auto grid h-11 w-11 place-items-center rounded-xl bg-cyan-400/10 text-xl text-cyan-400">
            ↑
          </div>
          <p className="mt-4 font-medium text-slate-200">
            Choose a knowledge source
          </p>
          <p className="mt-1 text-sm text-slate-500">
            Markdown, plain text, or text-based PDF
          </p>
          <label className="action-secondary mt-5 inline-block cursor-pointer">
            <span>{file ? file.name : "Select a file"}</span>
            <input
              type="file"
              accept=".txt,.md,.pdf,text/plain,text/markdown,application/pdf"
              onChange={(event) => setFile(event.target.files?.[0] || null)}
              className="sr-only"
            />
          </label>
          {file && (
            <p className="mt-3 text-xs text-slate-500">
              {Math.ceil(file.size / 1024)} KB ready to index
            </p>
          )}
        </div>
        <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-xs leading-5 text-slate-500">
            The first local run may load the embedding model. Once it is ready,
            indexing small files takes only a few seconds.
          </p>
          <button disabled={!file || busy} className="action-primary shrink-0">
            {busy ? `Indexing · ${elapsed}s` : "Upload and index"}
          </button>
        </div>
        {status && (
          <div
            className={`mt-5 rounded-xl border p-4 text-sm ${isSuccess ? "border-emerald-900/70 bg-emerald-950/30 text-emerald-200" : busy ? "border-cyan-900/70 bg-cyan-950/30 text-cyan-100" : "border-rose-900/70 bg-rose-950/30 text-rose-200"}`}
          >
            <p className="font-medium">
              {isSuccess
                ? "Index complete"
                : busy
                  ? "Indexing in progress"
                  : "Upload failed"}
            </p>
            <p className="mt-1 opacity-80">{status}</p>
            {busy && elapsed >= 30 && (
              <p className="mt-3 text-xs opacity-80">
                The local embedding model is still loading. Keep this page open;
                the first initialization can take a few minutes.
              </p>
            )}
            {isSuccess && (
              <button
                type="button"
                onClick={() => setPage("ask")}
                className="mt-3 text-sm font-semibold text-emerald-300 hover:text-emerald-200"
              >
                Ask a question about this source →
              </button>
            )}
          </div>
        )}
      </form>
      <div className="mt-8 grid gap-3 sm:grid-cols-3">
        {[
          ["1", "Chunk", "Split source text with overlap."],
          ["2", "Embed", "Create local MiniLM vectors."],
          ["3", "Retrieve", "Find evidence for each question."],
        ].map(([number, label, copy]) => (
          <div key={number} className="rounded-xl border border-slate-800 p-4">
            <p className="text-xs font-semibold text-cyan-400">{number}</p>
            <p className="mt-3 text-sm font-medium">{label}</p>
            <p className="mt-1 text-xs leading-5 text-slate-500">{copy}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
