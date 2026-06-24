import { useState } from "react";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Upload from "./pages/Upload";
import Ask from "./pages/Ask";
import Traces from "./pages/Traces";
import Evaluations from "./pages/Evaluations";

export default function App() {
  const [page, setPage] = useState("home");
  const Page = { home: Home, upload: Upload, ask: Ask, traces: Traces, evaluations: Evaluations }[page];
  return (
    <>
      <Navbar page={page} setPage={setPage} />
      <main className="mx-auto min-h-screen max-w-6xl px-5 sm:px-6">
        <Page setPage={setPage} />
      </main>
    </>
  );
}
