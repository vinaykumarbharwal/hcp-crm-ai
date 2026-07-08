import { createSlice } from "@reduxjs/toolkit";

// One slice owns the full draft workflow: user input, request status, and agent output.
const initialState = {
  loading: false,
  error: "",
  form: {
    transcript: "",
    hcpName: "",
    product: "",
    sentiment: "neutral"
  },
  draft: null
};

const interactionSlice = createSlice({
  name: "interaction",
  initialState,
  reducers: {
    updateField(state, action) {
      // Field names come from controlled inputs, keeping the form reducer reusable.
      state.form[action.payload.field] = action.payload.value;
    },
    setDraft(state, action) {
      state.draft = action.payload;
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
