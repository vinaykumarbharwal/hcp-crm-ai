from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.hcp_agent import analyze_transcript
from app.agents.tools import edit_interaction
from app.schemas.interaction import InteractionAnalyzeRequest, InteractionDraft, InteractionUpdateRequest
from app.services.database import get_db
from app.services.interactions import persist_interaction_update, save_interaction_draft

router = APIRouter()


def _refresh_summary(draft: InteractionDraft) -> None:
    draft.draft_summary = (
        f"{draft.hcp_name} discussed {draft.product} with "
        f"{draft.sentiment} sentiment. Compliance status: {draft.compliance_status}."
    )


def _form_updates_to_draft_fields(payload: InteractionAnalyzeRequest) -> dict:
    updates = {
        "hcp_name": payload.hcp_name,
        "product": payload.product,
        "sentiment": payload.sentiment,
    }
    if payload.follow_ups:
        updates["action_items"] = [item.strip() for item in payload.follow_ups.splitlines() if item.strip()]
    if payload.outcomes:
        updates["draft_summary"] = payload.outcomes
    return updates


@router.post("/analyze", response_model=InteractionDraft)
def analyze_interaction(payload: InteractionAnalyzeRequest, db: Session = Depends(get_db)) -> InteractionDraft:
    if not payload.has_interaction_content():
        raise HTTPException(status_code=400, detail="Enter interaction notes or fill at least one interaction field.")

    transcript = payload.combined_transcript()
    draft = analyze_transcript(transcript)

    # Prefer explicit form fields over extracted values when the rep supplied them.
    if payload.hcp_name:
        draft.hcp_name = payload.hcp_name
    if payload.product:
        draft.product = payload.product
    if payload.sentiment:
        draft.sentiment = payload.sentiment
    if payload.follow_ups and payload.follow_ups not in draft.action_items:
        draft.action_items.append(payload.follow_ups)

    _refresh_summary(draft)
    return save_interaction_draft(db, draft, transcript)


@router.post("/edit", response_model=InteractionDraft)
def edit_interaction_draft(payload: InteractionUpdateRequest, db: Session = Depends(get_db)) -> InteractionDraft:
    updates = _form_updates_to_draft_fields(payload.updates)
    updated = edit_interaction(payload.existing.model_dump(), updates)
    draft = InteractionDraft(**updated)

    # Outcomes can intentionally replace the visible summary; otherwise keep it consistent.
    if not payload.updates.outcomes:
        _refresh_summary(draft)

    transcript = payload.updates.combined_transcript() or draft.draft_summary
    return persist_interaction_update(db, draft, transcript)