const stages = [
  [
    "01",
    "Ingest",
    "Upload UTF-8 text or Markdown. RAGLens chunks and embeds it locally.",
  ],
  [
    "02",
    "Retrieve",
    "Ask a question and inspect ranked semantic matches with similarity scores.",
  ],
  [
    "03",
    "Inspect",
    "Review the prompt, cited answer, model, and persisted execution trace.",
  ],
];

export default function Home({ setPage }) {
  return (
    <section className="py-12 sm:py-20">
      <div className="grid items-center gap-12 lg:grid-cols-[1.1fr_.9fr]">
        <div>
          <p className="eyebrow">RAG evaluation & observability</p>
          <h1 className="mt-5 max-w-3xl text-4xl font-bold tracking-tight text-white sm:text-6xl">
            Make every RAG answer{" "}
            <span className="text-cyan-400">explainable.</span>
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-400">
            RAGLens helps developers understand, debug, and improve RAG systems
            by showing what was retrieved, what was sent to the model, and
            whether an answer is grounded in its sources.
          </p>
          <div className="mt-9 flex flex-wrap gap-3">
            <button
              onClick={() => setPage("upload")}
              className="action-primary"
            >
              Upload a knowledge source <span aria-hidden="true">→</span>
            </button>
            <button
              onClick={() => setPage("traces")}
              className="action-secondary"
            >
              Inspect traces
            </button>
          </div>
        </div>
        <div className="panel overflow-hidden">
          <div className="border-b border-slate-800 bg-slate-900/80 px-5 py-4">
            <p className="text-sm font-semibold">Trace preview</p>
            <p className="mt-1 text-xs text-slate-500">
              Every answer is inspectable.
            </p>
          </div>
          <div className="space-y-4 p-5 text-sm">
            <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
              <p className="text-xs text-slate-500">QUESTION</p>
              <p className="mt-1 text-slate-200">
                What is the main goal of RAGLens?
              </p>
            </div>
            <div className="flex gap-3">
              <div className="mt-1 h-2.5 w-2.5 rounded-full bg-cyan-400" />
              <div>
                <p className="text-xs font-medium text-cyan-400">
                  RETRIEVED CONTEXT
                </p>
                <p className="mt-1 text-slate-400">
                  Source 1 · high semantic similarity
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <div className="mt-1 h-2.5 w-2.5 rounded-full bg-violet-400" />
              <div>
                <p className="text-xs font-medium text-violet-300">
                  GROUNDED ANSWER
                </p>
                <p className="mt-1 text-slate-400">
                  Answer, prompt, model, and timestamp saved.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="mt-20 grid gap-4 md:grid-cols-3">
        {stages.map(([number, title, description]) => (
          <article key={number} className="panel p-6">
            <p className="text-sm font-semibold text-cyan-400">{number}</p>
            <h2 className="mt-6 text-lg font-semibold">{title}</h2>
            <p className="mt-2 text-sm leading-6 text-slate-400">
              {description}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}
