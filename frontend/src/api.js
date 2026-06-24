const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, options);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || "Request failed");
  return payload;
}

export const uploadDocument = (file) => {
  const data = new FormData();
  data.append("file", file);
  return request("/documents/upload", { method: "POST", body: data });
};
export const askQuestion = (question) =>
  request("/questions/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
export const getTraces = () => request("/traces");
export const getEvaluationRuns = () => request("/evaluations/runs");
export const createEvaluationRun = (payload) =>
  request("/evaluations/runs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
export const evaluationReportUrl = (id, format) =>
  `${API}/evaluations/runs/${id}/report.${format}`;
