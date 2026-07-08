const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function analyzeInteraction(transcript) {
  // The backend returns a draft only; final save/approval should use a separate endpoint.
  const response = await fetch(`${API_URL}/api/interactions/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ transcript })
  });

  if (!response.ok) {
    throw new Error("Unable to analyze interaction right now.");
  }

  return response.json();
}
