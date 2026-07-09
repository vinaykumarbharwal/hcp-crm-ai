import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { analyzeInteraction, updateInteractionDraft } from "../services/api.js";
import { setDraft, setError, setLoading, updateField } from "../store/interactionSlice.js";
import { InteractionSummary } from "./InteractionSummary.jsx";

const aiSuggestions = [
  "Schedule follow-up meeting in 2 weeks",
  "Send OncoBoost Phase III PDF",
  "Add HCP to advisory board invite list"
];

const requiredInputFields = ["transcript", "hcpName", "product", "topics", "outcomes", "followUps"];

const assistantHint = 'Log interaction details here (e.g., "Met Dr. Smith, discussed Prodo-X efficacy, positive sentiment, shared brochure") or ask for help.';

function buildSuccessMessage(draft) {
  const hcpText = draft.hcp_name && draft.hcp_name !== "Unknown HCP" ? ` for ${draft.hcp_name}` : "";
  const productText = draft.product && draft.product !== "General discussion" ? ` ${draft.product}` : "";
  const sentimentText = draft.sentiment ? ` Sentiment is marked as ${draft.sentiment}.` : "";
  const materialText = draft.resource_request
    ? " Materials/resource follow-up has been flagged from your summary."
    : " Materials will be populated if the note mentions brochures, studies, or samples.";
  const followUpText = draft.action_items?.[0] || "scheduling a meeting";

  return `Interaction logged successfully${hcpText}! I populated the HCP Name, Date, Sentiment, and Materials from your${productText} summary.${sentimentText}${materialText} Would you like me to suggest a specific follow-up action, such as ${followUpText}?`;
}

export function InteractionForm() {
  const dispatch = useDispatch();
  const { form, loading, error, draft } = useSelector((state) => state.interaction);
  const [lastSubmittedMessage, setLastSubmittedMessage] = useState("");
  const [assistantSuccessMessage, setAssistantSuccessMessage] = useState("");

  const fieldValue = (field, fallback = "") => form[field] ?? fallback;
  const hasEnoughInput = requiredInputFields.some((field) => fieldValue(field).trim().length >= 3);

  function submittedMessageText() {
    const transcript = fieldValue("transcript").trim();
    if (transcript) {
      return transcript;
    }

    return [
      fieldValue("hcpName").trim() && `HCP: ${fieldValue("hcpName").trim()}`,
      fieldValue("product").trim() && `Product: ${fieldValue("product").trim()}`,
      fieldValue("topics").trim() && `Topics: ${fieldValue("topics").trim()}`,
      fieldValue("outcomes").trim() && `Outcomes: ${fieldValue("outcomes").trim()}`,
      fieldValue("followUps").trim() && `Follow-ups: ${fieldValue("followUps").trim()}`
    ].filter(Boolean).join(". ");
  }

  async function handleAnalyze(event) {
    event.preventDefault();
    dispatch(setError(""));

    if (!hasEnoughInput) {
      dispatch(setError("Enter a short chat note or fill at least one interaction field."));
      return;
    }

    const submittedMessage = submittedMessageText();
    dispatch(setLoading(true));

    try {
      const result = await analyzeInteraction(form);
      dispatch(setDraft(result));
      setLastSubmittedMessage(submittedMessage);
      setAssistantSuccessMessage(buildSuccessMessage(result));
      dispatch(updateField({ field: "transcript", value: "" }));
    } catch (err) {
      dispatch(setError(err.message));
    } finally {
      dispatch(setLoading(false));
    }
  }

  async function handleUpdate() {
    dispatch(setError(""));

    if (!draft) {
      dispatch(setError("Create a draft before updating it."));
      return;
    }

    dispatch(setLoading(true));

    try {
      const result = await updateInteractionDraft(draft, form);
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

  function applySuggestion(item) {
    const current = fieldValue("followUps");
    const nextValue = current ? `${current}\n${item}` : item;
    dispatch(updateField({ field: "followUps", value: nextValue }));
  }

  return (
    <form className="log-screen" onSubmit={handleAnalyze}>
      <section className="form-pane" aria-label="Interaction details">
        <div className="details-card">
          <h1>Log HCP Interaction</h1>

          <div className="field-grid two-columns">
            <label>
              HCP Name
              <input value={fieldValue("hcpName")} onChange={update("hcpName")} placeholder="Search or select HCP..." />
            </label>

            <label>
              Product Discussed
              <input value={fieldValue("product")} onChange={update("product")} placeholder="Enter product name..." />
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
              placeholder="Product X efficiency..."
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
                <span>{fieldValue("product") ? `${fieldValue("product")} brochure.` : "Brochures."}</span>
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
              <span className="sentiment-face" aria-hidden="true">:)</span>
              Positive
            </label>
            <label>
              <input type="radio" name="sentiment" value="neutral" checked={fieldValue("sentiment", "neutral") === "neutral"} onChange={update("sentiment")} />
              <span className="sentiment-face" aria-hidden="true">:|</span>
              Neutral
            </label>
            <label>
              <input type="radio" name="sentiment" value="concerned" checked={fieldValue("sentiment", "neutral") === "concerned"} onChange={update("sentiment")} />
              <span className="sentiment-face" aria-hidden="true">:(</span>
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
              <button type="button" key={item} onClick={() => applySuggestion(item)}>+ {item}</button>
            ))}
          </div>
        </div>
      </section>

      <aside className="assistant-pane" aria-label="AI assistant">
        <div className="assistant-header">
          <span className="assistant-icon" aria-hidden="true">AI</span>
          <div>
            <h2>AI Assistant</h2>
            <p>Log interaction details here via chat</p>
          </div>
        </div>

        <div className="assistant-body">
          <div className="chat-bubble hint-bubble">
            {assistantHint}
          </div>

          {lastSubmittedMessage && (
            <div className="chat-bubble user-bubble">
              {lastSubmittedMessage}
            </div>
          )}

          {assistantSuccessMessage && (
            <div className="chat-bubble success-bubble">
              {assistantSuccessMessage}
            </div>
          )}

          <InteractionSummary draft={draft} />
        </div>

        {error && <p className="error">{error}</p>}

        <div className="assistant-input-row">
          <input
            value={form.transcript}
            onChange={update("transcript")}
            placeholder="Describe Interaction..."
            aria-label="Describe interaction"
          />
          <button className="log-button" type="submit" disabled={loading || !hasEnoughInput}>
            <span>A</span>
            {loading ? "..." : "Log"}
          </button>
          {draft && (
            <button className="update-button" type="button" disabled={loading} onClick={handleUpdate}>
              Update
            </button>
          )}
        </div>
      </aside>
    </form>
  );
}