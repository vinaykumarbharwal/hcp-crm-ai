import re

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


def _split_action_items(value: str) -> list[str]:
    return [item.strip() for item in value.splitlines() if item.strip()]


def _extract_labeled_value(transcript: str, label: str) -> str:
    match = re.search(rf"\b{label}\s*:\s*([^\.\n]+)", transcript, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _extract_transcript_updates(transcript: str) -> dict:
    if not transcript.strip():
        return {}

    extracted = analyze_transcript(transcript)
    text = transcript.lower()
    updates = {}

    if extracted.hcp_name != "Unknown HCP":
        updates["hcp_name"] = extracted.hcp_name
    if extracted.product != "General discussion":
        updates["product"] = extracted.product
    if re.search(r"\b(positive|neutral|concerned|negative|unhappy|hesitant|not interested)\b", text):
        updates["sentiment"] = extracted.sentiment
    if re.search(r"\b(meeting|call|phone|telephonic|email|mailed|conference|congress|symposium)\b", text):
        updates["interaction_type"] = extracted.interaction_type
    if extracted.date:
        updates["date"] = extracted.date
    if extracted.time:
        updates["time"] = extracted.time

    outcomes = _extract_labeled_value(transcript, "outcomes?")
    if outcomes:
        updates["draft_summary"] = outcomes

    follow_up = _extract_labeled_value(transcript, "follow-?ups?")
    if follow_up:
        updates["action_items"] = [follow_up]
    elif extracted.action_items and extracted.action_items != ["Review and confirm interaction log"]:
        updates["action_items"] = extracted.action_items

    return updates


def _form_updates_to_draft_fields(payload: InteractionAnalyzeRequest) -> dict:
    updates = {
        "hcp_name": payload.hcp_name,
        "product": payload.product,
        "interaction_type": payload.interaction_type,
        "date": payload.date,
        "time": payload.time,
    }
    if payload.has_explicit_sentiment():
        updates["sentiment"] = payload.sentiment
    if payload.follow_ups:
        updates["action_items"] = _split_action_items(payload.follow_ups)
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
    if payload.interaction_type:
        draft.interaction_type = payload.interaction_type
    if payload.date:
        draft.date = payload.date
    if payload.time:
        draft.time = payload.time
    if payload.has_explicit_sentiment():
        draft.sentiment = payload.sentiment
    if payload.follow_ups:
        for item in _split_action_items(payload.follow_ups):
            if item not in draft.action_items:
                draft.action_items.append(item)

    _refresh_summary(draft)
    return save_interaction_draft(db, draft, transcript)


@router.post("/edit", response_model=InteractionDraft)
def edit_interaction_draft(payload: InteractionUpdateRequest, db: Session = Depends(get_db)) -> InteractionDraft:
    updates = _form_updates_to_draft_fields(payload.updates)
    updates.update(_extract_transcript_updates(payload.updates.transcript))
    updated = edit_interaction(payload.existing.model_dump(), updates)
    draft = InteractionDraft(**updated)

    # Outcomes can intentionally replace the visible summary; otherwise keep it consistent.
    if "draft_summary" not in updates:
        _refresh_summary(draft)

    transcript = payload.updates.combined_transcript() or draft.draft_summary
    return persist_interaction_update(db, draft, transcript)

