import { useState } from "react";
import { askQuestion } from "../api";
import RetrievedChunk from "../components/RetrievedChunk";

function TimingGrid({ timing }) {
  const values = [
    ["Embed", timing.embedding_ms],
    ["Retrieve", timing.retrieval_ms],
    ["Generate", timing.generation_ms],
    ["Total", timing.total_ms],
  ];

  return (
    <div className="mt-6 grid grid-cols-2 gap-2 border-t border-slate-800 pt-4 text-xs sm:grid-cols-4">
      {values.map(([label, milliseconds]) => (
        <div key={label} className="rounded-lg bg-slate-950/60 p-2">
          <p className="text-slate-500">{label}</p>
          <p className="mt-1 font-medium text-slate-300">
            {(milliseconds / 1000).toFixed(2)}s
          </p>
        </div>
      ))}
    </div>
  );
}

export default function Ask({ setPage }) {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event) {
    event.preventDefault();
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion) return;

    setBusy(true);
    setError("");
    setResult(null);

    try {
      setResult(await askQuestion(trimmedQuestion));
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="max-w-5xl py-12">
      <p className="eyebrow">Grounded Q&A</p>
      <h1 className="mt-3 text-3xl font-bold">Ask your knowledge base</h1>
      <p className="mt-2 text-slate-400">
        RAGLens retrieves the most relevant chunks before generating an answer.
      </p>
      <form
        onSubmit={submit}
        className="panel mt-8 p-3 sm:flex sm:items-center sm:gap-3"
      >
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="What do you want to know?"
          className="w-full min-w-0 bg-transparent px-3 py-3 text-slate-100 outline-none placeholder:text-slate-600"
        />
        <button
          disabled={!question.trim() || busy}
          className="action-primary mt-2 w-full sm:mt-0 sm:w-auto"
        >
          {busy ? "Generating…" : "Ask question"}
        </button>
      </form>
      {busy && (
        <p className="mt-4 text-sm text-slate-400">
          Searching your indexed documents and generating a grounded response…
        </p>
      )}
      {error && (
        <div className="mt-5 rounded-xl border border-rose-900/70 bg-rose-950/30 p-4 text-sm text-rose-200">
          <p className="font-medium">The question could not be completed.</p>
          <p className="mt-1 text-rose-300/80">{error}</p>
        </div>
      )}
      {result && (
        <div className="mt-9 grid gap-8 lg:grid-cols-[1.1fr_.9fr]">
          <div className="panel p-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="eyebrow">Grounded answer</p>
                <p className="mt-2 text-xs text-slate-500">
                  Generated with {result.model}
                </p>
              </div>
              <button
                onClick={() => setPage("traces")}
                className="action-secondary"
              >
                View trace
              </button>
            </div>
            <p className="mt-6 whitespace-pre-wrap text-[15px] leading-7 text-slate-200">
              {result.answer}
            </p>
            <TimingGrid timing={result.timing} />
            <p className="mt-4 text-xs text-slate-500">
              Trace ID · {result.trace_id}
            </p>
          </div>
          <aside>
            <div className="flex items-end justify-between">
              <div>
                <p className="eyebrow">Evidence</p>
                <h2 className="mt-2 text-lg font-semibold">
                  Retrieved sources
                </h2>
              </div>
              <p className="text-xs text-slate-500">
                {result.citations.length} match
                {result.citations.length === 1 ? "" : "es"}
              </p>
            </div>
            <div className="mt-4 grid gap-3">
              {result.citations.map((chunk, index) => (
                <RetrievedChunk
                  key={`${chunk.document}-${index}`}
                  chunk={chunk}
                  index={index + 1}
                />
              ))}
            </div>
          </aside>
        </div>
      )}
    </section>
  );
}
