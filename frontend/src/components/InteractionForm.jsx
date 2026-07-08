import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { analyzeInteraction } from "../services/api.js";
import { setDraft, setError, setLoading, updateField } from "../store/interactionSlice.js";

const aiSuggestions = [
  "Schedule follow-up meeting in 2 weeks",
  "Send OncoBoost Phase III PDF",
  "Add Dr. Sharma to advisory board invite list"
];

export function InteractionForm() {
  const dispatch = useDispatch();
  const { form, loading, error, draft } = useSelector((state) => state.interaction);

  const fieldValue = (field, fallback = "") => form[field] ?? fallback;

  async function handleAnalyze(event) {
    event.preventDefault();
    dispatch(setLoading(true));
    dispatch(setError(""));

    try {
      const result = await analyzeInteraction(form.transcript);
      dispatch(setDraft(result));
    } catch (err) {
      dispatch(setError(err.message));
    } finally {
      dispatch(setLoading(false));
    }
  }

  function update(field) {
    return (event) => dispatch(updateField({ field, value: event.target.value }));
  }

  return (
    <form className="log-screen" onSubmit={handleAnalyze}>
      <section className="form-pane" aria-label="Interaction details">
        <h1>Log HCP Interaction</h1>

        <div className="details-card">
          <h2>Interaction Details</h2>

          <div className="field-grid two-columns">
            <label>
              HCP Name
              <input value={fieldValue("hcpName")} onChange={update("hcpName")} placeholder="Search or select HCP..." />
            </label>

            <label>
              Interaction Type
              <select value={fieldValue("interactionType", "Meeting")} onChange={update("interactionType")}>
                <option>Meeting</option>
                <option>Call</option>
                <option>Email</option>
                <option>Conference</option>
              </select>
            </label>

            <label>
              Date
              <input type="text" value={fieldValue("date", "19-04-2025")} onChange={update("date")} />
            </label>

            <label>
              Time
              <input type="text" value={fieldValue("time", "19:36")} onChange={update("time")} />
            </label>
          </div>

          <label>
            Attendees
            <input value={fieldValue("attendees")} onChange={update("attendees")} placeholder="Enter names or search..." />
          </label>

          <label>
            Topics Discussed
            <textarea
              className="topics-input"
              value={fieldValue("topics")}
              onChange={update("topics")}
              placeholder="Enter key discussion points..."
            />
          </label>

          <button className="voice-button" type="button">
            Summarize from Voice Note (Requires Consent)
          </button>

          <div className="section-label">Materials Shared / Samples Distributed</div>
          <div className="resource-list">
            <div className="resource-row">
              <div>
                <strong>Materials Shared</strong>
                <span>No materials added.</span>
              </div>
              <button type="button">Search/Add</button>
            </div>
            <div className="resource-row">
              <div>
                <strong>Samples Distributed</strong>
                <span>No samples added.</span>
              </div>
              <button type="button">Add Sample</button>
            </div>
          </div>

          <fieldset className="sentiment-group">
            <legend>Observed/Inferred HCP Sentiment</legend>
            <label>
              <input type="radio" name="sentiment" value="positive" checked={fieldValue("sentiment", "neutral") === "positive"} onChange={update("sentiment")} />
              Positive
            </label>
            <label>
              <input type="radio" name="sentiment" value="neutral" checked={fieldValue("sentiment", "neutral") === "neutral"} onChange={update("sentiment")} />
              Neutral
            </label>
            <label>
              <input type="radio" name="sentiment" value="negative" checked={fieldValue("sentiment", "neutral") === "negative"} onChange={update("sentiment")} />
              Negative
            </label>
          </fieldset>

          <label>
            Outcomes
            <textarea className="short-textarea" value={fieldValue("outcomes")} onChange={update("outcomes")} placeholder="Key outcomes or agreements..." />
          </label>

          <label>
            Follow-up Actions
            <textarea className="short-textarea" value={fieldValue("followUps")} onChange={update("followUps")} placeholder="Enter next steps or tasks..." />
          </label>

          <div className="suggestions">
            <strong>AI Suggested Follow-ups:</strong>
            {aiSuggestions.map((item) => (
              <button type="button" key={item}>+ {item}</button>
            ))}
          </div>
        </div>
      </section>

      <aside className="assistant-pane" aria-label="AI assistant">
        <div className="assistant-header">
          <span className="assistant-icon">AI</span>
          <div>
            <h2>AI Assistant</h2>
            <p>Log interaction via chat</p>
          </div>
        </div>

        <div className="assistant-body">
          <div className="prompt-card">
            Log interaction details here (e.g., "Met Dr. Smith, discussed Product X efficacy, positive sentiment, shared brochure") or ask for help.
          </div>

          {draft && (
            <div className="draft-card">
              <strong>Draft captured</strong>
              <span>{draft.hcp_name || "HCP"} - {draft.sentiment || "neutral"}</span>
              <p>{draft.competitive_intelligence || "No competitor mention found."}</p>
            </div>
          )}
        </div>

        {error && <p className="error">{error}</p>}

        <div className="assistant-input-row">
          <input
            value={form.transcript}
            onChange={update("transcript")}
            placeholder="Describe interaction..."
            aria-label="Describe interaction"
          />
          <button className="log-button" type="submit" disabled={loading || !form.transcript.trim()}>
            {loading ? "..." : "Log"}
          </button>
        </div>
      </aside>
    </form>
  );
}
