import re


# These functions are intentionally small placeholders for the five planned CRM tools.
# In production, each function can call Groq/LangGraph while keeping the same contract.
def log_interaction(transcript: str) -> dict:
    return {
        "hcp_name": _find_hcp_name(transcript),
        "product": _find_product(transcript),
        "sentiment": _find_sentiment(transcript),
        "action_items": _find_action_items(transcript),
    }


def edit_interaction(existing: dict, updates: dict) -> dict:
    # Ignore empty updates so partial edits do not erase already verified values.
    updated = existing.copy()
    updated.update({key: value for key, value in updates.items() if value not in (None, "")})
    return updated


def verify_compliance_guidelines(transcript: str) -> str:
    # Simple keyword screening keeps the demo functional until a regulated rule set is added.
    risky_terms = ["guaranteed cure", "off-label", "no side effects", "100% safe"]
    return "review_required" if any(term in transcript.lower() for term in risky_terms) else "clear"


def log_resource_request(transcript: str) -> str | None:
    # Resource intent covers samples, clinical material, and study follow-ups.
    keywords = ["sample", "samples", "study", "studies", "brochure", "material"]
    return "resource_follow_up_needed" if any(word in transcript.lower() for word in keywords) else None


def extract_competitive_intelligence(transcript: str) -> str | None:
    # Broad competitor cues are enough for routing the draft to brand intelligence review.
    match = re.search(r"competitor|competing|alternative|versus|vs\.?\s+([\w-]+)", transcript, re.IGNORECASE)
    return "competitor_or_alternative_mentioned" if match else None


def _find_hcp_name(transcript: str) -> str:
    match = re.search(r"Dr\.?\s+[A-Z][a-zA-Z]+", transcript)
    return match.group(0) if match else "Unknown HCP"


def _find_product(transcript: str) -> str:
    match = re.search(r"(?:product|drug|medicine|therapy|trial)\s+([A-Z]?[a-zA-Z0-9-]+)", transcript, re.IGNORECASE)
    return match.group(1) if match else "General discussion"


def _find_sentiment(transcript: str) -> str:
    text = transcript.lower()
    if any(word in text for word in ["interested", "positive", "agreed", "liked"]):
        return "positive"
    if any(word in text for word in ["worried", "concern", "pricing", "risk"]):
        return "concerned"
    return "neutral"


def _find_action_items(transcript: str) -> list[str]:
    actions = []
    if log_resource_request(transcript):
        actions.append("Send requested resources")
    if "follow" in transcript.lower():
        actions.append("Schedule follow-up")
    return actions or ["Review and confirm interaction log"]
