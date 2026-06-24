import RetrievedChunk from "./RetrievedChunk";

export default function TraceCard({ trace }) {
  const [date, time] = new Date(trace.created_at).toLocaleString().split(", ");
  const scoreItems = trace.scores ? Object.entries(trace.scores) : [];
  return (
    <article className="panel overflow-hidden">
      <div className="border-b border-slate-800 px-5 py-5 sm:px-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="eyebrow">RAG run</p>
            <h2 className="mt-2 text-lg font-semibold text-white">
              {trace.question}
            </h2>
          </div>
          <div className="text-right text-xs text-slate-500">
            <p>{date}</p>
            <p className="mt-1">
              {time} · {trace.model}
            </p>
          </div>
        </div>
      </div>
      <div className="grid divide-y divide-slate-800 lg:grid-cols-[.9fr_1.1fr] lg:divide-x lg:divide-y-0">
          <section className="p-5 sm:p-6">
            <p className="eyebrow">Answer</p>
            <p className="mt-4 whitespace-pre-wrap leading-7 text-slate-200">
              {trace.answer}
            </p>
            {scoreItems.length > 0 && <div className="mt-5 grid grid-cols-2 gap-2 text-xs sm:grid-cols-4">{scoreItems.map(([label, value]) => <div key={label} className="rounded-lg bg-slate-950/60 p-2"><p className="capitalize text-slate-500">{label.replace("_", " ")}</p><p className="mt-1 font-medium text-cyan-300">{(value * 100).toFixed(0)}%</p></div>)}</div>}
          <div className="mt-6 grid grid-cols-2 gap-2 text-xs sm:grid-cols-4">
            {[
              ["Embed", trace.timing.embedding_ms],
              ["Retrieve", trace.timing.retrieval_ms],
              ["Generate", trace.timing.generation_ms],
              ["Total", trace.timing.total_ms],
            ].map(([label, ms]) => (
              <div key={label} className="rounded-lg bg-slate-950/60 p-2">
                <p className="text-slate-500">{label}</p>
                <p className="mt-1 font-medium text-slate-300">
                  {(ms / 1000).toFixed(2)}s
                </p>
              </div>
            ))}
          </div>
          <div className="mt-4 rounded-lg bg-slate-950/50 p-3 text-xs text-slate-500">
            <span className="font-medium text-slate-300">Model</span>
            <span className="mx-2 text-slate-700">·</span>
            {trace.model}
          </div>
        </section>
        <section className="p-5 sm:p-6">
          <div className="flex items-center justify-between">
            <p className="eyebrow">Retrieved evidence</p>
            <span className="text-xs text-slate-500">
              {trace.retrieved_chunks.length} chunk
              {trace.retrieved_chunks.length === 1 ? "" : "s"}
            </span>
          </div>
          <div className="mt-4 grid gap-3">
            {trace.retrieved_chunks.map((chunk, index) => (
              <RetrievedChunk
                key={`${trace.id}-${index}`}
                chunk={chunk}
                index={index + 1}
                expanded
              />
            ))}
          </div>
        </section>
      </div>
      <details className="border-t border-slate-800 px-5 py-4 sm:px-6">
        <summary className="cursor-pointer text-sm font-medium text-cyan-400 marker:text-slate-600">
          Inspect final prompt
        </summary>
        <pre className="mt-4 max-h-80 overflow-auto whitespace-pre-wrap rounded-xl bg-slate-950 p-4 text-xs leading-5 text-slate-400">
          {trace.final_prompt}
        </pre>
      </details>
    </article>
  );
}
