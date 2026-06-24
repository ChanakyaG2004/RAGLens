export default function RetrievedChunk({ chunk, index, expanded = false }) {
  const score = Math.round(chunk.similarity_score * 100);
  return (
    <article className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
            Source {index}
          </p>
          <p className="mt-1 text-sm font-medium text-slate-200">
            {chunk.document}{" "}
            <span className="font-normal text-slate-500">
              · chunk {chunk.chunk_index + 1}
            </span>
          </p>
        </div>
        <span className="rounded-full border border-slate-700 bg-slate-900 px-2.5 py-1 text-xs font-medium text-slate-300">
          {score}% match
        </span>
      </div>
      <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full rounded-full bg-cyan-400"
          style={{ width: `${Math.max(0, Math.min(100, score))}%` }}
        />
      </div>
      <p
        className={`mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-400 ${expanded ? "" : "line-clamp-4"}`}
      >
        {chunk.content}
      </p>
    </article>
  );
}
