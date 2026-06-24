export default function Navbar({ page, setPage }) {
  const links = [
    ["home", "Overview"],
    ["upload", "Upload"],
    ["ask", "Ask"],
    ["traces", "Traces"],
    ["evaluations", "Evaluate"],
  ];
  return (
    <header className="sticky top-0 z-20 border-b border-slate-800/80 bg-slate-950/90 backdrop-blur">
      <nav className="mx-auto flex max-w-6xl items-center gap-5 px-5 py-4 sm:px-6">
        <button
          onClick={() => setPage("home")}
          className="flex items-center gap-2 text-left"
        >
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-cyan-400 text-sm font-black text-slate-950">
            R
          </span>
          <span className="text-lg font-bold tracking-tight">
            RAG<span className="text-cyan-400">Lens</span>
          </span>
        </button>
        <div className="ml-auto flex max-w-full gap-1 overflow-x-auto">
          {links.map(([key, label]) => (
            <button
              key={key}
              onClick={() => setPage(key)}
              className={`rounded-lg px-3 py-2 text-sm transition ${page === key ? "bg-slate-800 text-white" : "text-slate-400 hover:bg-slate-900 hover:text-white"}`}
            >
              {label}
            </button>
          ))}
        </div>
      </nav>
    </header>
  );
}
