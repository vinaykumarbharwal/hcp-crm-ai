from fastapi import APIRouter, HTTPException

from app.agents.hcp_agent import analyze_transcript
from app.schemas.interaction import InteractionAnalyzeRequest, InteractionDraft

router = APIRouter()


@router.post("/analyze", response_model=InteractionDraft)
def analyze_interaction(payload: InteractionAnalyzeRequest) -> InteractionDraft:
    # This endpoint only builds a draft; approved persistence should be a separate action.
    if not payload.has_interaction_content():
        raise HTTPException(status_code=400, detail="Enter interaction notes or fill at least one interaction field.")

    transcript = payload.combined_transcript()
    draft = analyze_transcript(transcript)

    # Prefer explicit form fields over heuristic extraction when the user supplied them.
    if payload.hcp_name:
        draft.hcp_name = payload.hcp_name
    if payload.product:
        draft.product = payload.product
    if payload.sentiment:
        draft.sentiment = payload.sentiment
    if payload.follow_ups and payload.follow_ups not in draft.action_items:
        draft.action_items.append(payload.follow_ups)

    draft.draft_summary = (
        f"{draft.hcp_name} discussed {draft.product} with "
        f"{draft.sentiment} sentiment. Compliance status: {draft.compliance_status}."
    )
    return draft
