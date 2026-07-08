const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function parseResponse(response, fallbackMessage) {
  if (!response.ok) {
    let message = fallbackMessage;
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

export async function analyzeInteraction(form) {
  // Send the full form so chat notes and structured fields both work.
  const response = await fetch(`${API_URL}/api/interactions/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(form)
  });

  return parseResponse(response, "Unable to analyze interaction right now.");
}

export async function updateInteractionDraft(existing, updates) {
  const response = await fetch(`${API_URL}/api/interactions/edit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ existing, updates })
  });

  return parseResponse(response, "Unable to update interaction draft right now.");
}
