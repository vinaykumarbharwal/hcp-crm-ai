from app.agents.tools import (
    extract_competitive_intelligence,
    log_interaction,
    log_resource_request,
    verify_compliance_guidelines,
)
from app.schemas.interaction import InteractionDraft


def analyze_transcript(transcript: str) -> InteractionDraft:
    """Run the interaction through the agent workflow and return a reviewable draft."""
    # Keep these steps separate so each tool can later become a real LangGraph node.
    interaction = log_interaction(transcript)
    compliance_status = verify_compliance_guidelines(transcript)
    resource_request = log_resource_request(transcript)
    competitive_intel = extract_competitive_intelligence(transcript)

    # The frontend expects one compact draft object that a rep can verify before saving.
    return InteractionDraft(
        **interaction,
        compliance_status=compliance_status,
        resource_request=resource_request,
        competitive_intelligence=competitive_intel,
        draft_summary=(
            f"{interaction['hcp_name']} discussed {interaction['product']} with "
            f"{interaction['sentiment']} sentiment. Compliance status: {compliance_status}."
        ),
    )
