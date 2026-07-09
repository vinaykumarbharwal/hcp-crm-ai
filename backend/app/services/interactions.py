import json

from sqlalchemy.orm import Session

from app.models.interaction import Interaction
from app.schemas.interaction import InteractionDraft
from app.services.database import init_db


def save_interaction_draft(db: Session, draft: InteractionDraft, transcript: str) -> InteractionDraft:
    init_db()
    row = Interaction(
        hcp_name=draft.hcp_name,
        product=draft.product,
        sentiment=draft.sentiment,
        interaction_type=draft.interaction_type,
        interaction_date=draft.date,
        interaction_time=draft.time,
        transcript=transcript,
        action_items=json.dumps(draft.action_items),
        compliance_status=draft.compliance_status,
        resource_request=draft.resource_request,
        competitive_intelligence=draft.competitive_intelligence,
        draft_summary=draft.draft_summary,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    draft.id = row.id
    return draft


def persist_interaction_update(db: Session, draft: InteractionDraft, transcript: str) -> InteractionDraft:
    init_db()
    row = db.get(Interaction, draft.id) if draft.id else None
    if row is None:
        return save_interaction_draft(db, draft, transcript)

    row.hcp_name = draft.hcp_name
    row.product = draft.product
    row.sentiment = draft.sentiment
    row.interaction_type = draft.interaction_type
    row.interaction_date = draft.date
    row.interaction_time = draft.time
    row.transcript = transcript or row.transcript
    row.action_items = json.dumps(draft.action_items)
    row.compliance_status = draft.compliance_status
    row.resource_request = draft.resource_request
    row.competitive_intelligence = draft.competitive_intelligence
    row.draft_summary = draft.draft_summary
    db.commit()
    db.refresh(row)
    draft.id = row.id
    return draft