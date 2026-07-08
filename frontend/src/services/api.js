const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function analyzeInteraction(form) {
  // Send the full form so chat notes and structured fields both work.
  const response = await fetch(`${API_URL}/api/interactions/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(form)
  });

  if (!response.ok) {
    let message = "Unable to analyze interaction right now.";
    try {
      const errorBody = await response.json();
      message = errorBody.detail || message;
    } catch {
      // Keep the friendly fallback when the backend returns a non-JSON error.
    }
    throw new Error(message);
  }

  return response.json();
}
