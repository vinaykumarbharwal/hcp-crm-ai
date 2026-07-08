from fastapi import APIRouter

from app.agents.hcp_agent import analyze_transcript
from app.schemas.interaction import InteractionAnalyzeRequest, InteractionDraft

router = APIRouter()


@router.post("/analyze", response_model=InteractionDraft)
def analyze_interaction(payload: InteractionAnalyzeRequest) -> InteractionDraft:
    # This endpoint only builds a draft; approved persistence should be a separate action.
    return analyze_transcript(payload.transcript)
