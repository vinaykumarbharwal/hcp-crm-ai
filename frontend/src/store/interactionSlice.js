import { createSlice } from "@reduxjs/toolkit";

// One slice owns the full draft workflow: user input, request status, and agent output.
const initialState = {
  loading: false,
  error: "",
  form: {
    transcript: "",
    hcpName: "",
    product: "",
    interactionType: "Meeting",
    date: "19-04-2025",
    time: "19:36",
    attendees: "",
    topics: "",
    sentiment: "neutral",
    outcomes: "",
    followUps: ""
  },
  draft: null
};

function shouldUseExtractedValue(value, emptyValue) {
  return value && value !== emptyValue;
}

const interactionSlice = createSlice({
  name: "interaction",
  initialState,
  reducers: {
    updateField(state, action) {
      // Field names come from controlled inputs, keeping the form reducer reusable.
      state.form[action.payload.field] = action.payload.value;
    },
    setDraft(state, action) {
      const draft = action.payload;
      state.draft = draft;

      // When the AI assistant extracts useful details, copy them into the editable form.
      if (shouldUseExtractedValue(draft.hcp_name, "Unknown HCP")) {
        state.form.hcpName = draft.hcp_name;
      }
      if (shouldUseExtractedValue(draft.product, "General discussion")) {
        state.form.product = draft.product;
      }
      if (draft.sentiment) {
        state.form.sentiment = draft.sentiment;
      }
      if (draft.interaction_type || draft.interactionType) {
        state.form.interactionType = draft.interaction_type || draft.interactionType;
      }
      if (draft.action_items?.length) {
        state.form.followUps = draft.action_items.join("\n");
      }
      if (!state.form.outcomes && draft.draft_summary) {
        state.form.outcomes = draft.draft_summary;
      }
    },
    setLoading(state, action) {
      state.loading = action.payload;
    },
    setError(state, action) {
      state.error = action.payload;
    }
  }
});

export const { updateField, setDraft, setLoading, setError } = interactionSlice.actions;
export default interactionSlice.reducer;