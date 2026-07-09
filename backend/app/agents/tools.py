import re
from typing import Any, Protocol


class InteractionExtractor(Protocol):
    def extract_interaction(self, transcript: str, defaults: dict[str, Any]) -> dict[str, Any]:
        ...


STOP_WORDS = {
    "he", "she", "they", "it", "we", "i", "the", "a", "an", "new", "pricing", "sample",
    "study", "material", "brochure", "positive", "neutral", "concerned", "worried", "interested"
}


# Sales tool 1: Log Interaction. The LLM path extracts core fields and summarizes the note.
def log_interaction(transcript: str, llm_client: InteractionExtractor | None = None) -> dict:
    defaults = {
        "hcp_name": _find_hcp_name(transcript),
        "product": _find_product(transcript),
        "sentiment": _find_sentiment(transcript),
        "interaction_type": _find_interaction_type(transcript),
        "date": _find_date(transcript),
        "time": _find_time(transcript),
        "action_items": _find_action_items(transcript),
        "draft_summary": None,
    }

    if not llm_client:
        return defaults

    extracted = llm_client.extract_interaction(transcript, defaults)
    return {
        "hcp_name": extracted.get("hcp_name") or defaults["hcp_name"],
        "product": extracted.get("product") or defaults["product"],
        "sentiment": extracted.get("sentiment") or defaults["sentiment"],
        "interaction_type": extracted.get("interaction_type") or defaults["interaction_type"],
        "date": extracted.get("date") or defaults["date"],
        "time": extracted.get("time") or defaults["time"],
        "action_items": extracted.get("action_items") or defaults["action_items"],
        "draft_summary": extracted.get("draft_summary") or defaults["draft_summary"],
    }


# Sales tool 2: Edit Interaction. Partial updates preserve verified values.
def edit_interaction(existing: dict, updates: dict) -> dict:
    updated = existing.copy()
    updated.update({key: value for key, value in updates.items() if value not in (None, "")})
    return updated


# Sales tool 3: Verify Compliance Guidelines.
def verify_compliance_guidelines(transcript: str) -> str:
    risky_terms = ["guaranteed cure", "off-label", "no side effects", "100% safe"]
    return "review_required" if any(term in transcript.lower() for term in risky_terms) else "clear"


# Sales tool 4: Log Resource Request.
def log_resource_request(transcript: str) -> str | None:
    keywords = ["sample", "samples", "study", "studies", "brochure", "material"]
    return "resource_follow_up_needed" if any(word in transcript.lower() for word in keywords) else None


# Sales tool 5: Extract Competitive Intelligence.
def extract_competitive_intelligence(transcript: str) -> str | None:
    match = re.search(r"competitor|competing|alternative|versus|vs\.?\s+([\w-]+)", transcript, re.IGNORECASE)
    return "competitor_or_alternative_mentioned" if match else None


def _find_interaction_type(transcript: str) -> str:
    text = transcript.lower()
    if "conference" in text or "congress" in text or "symposium" in text:
        return "Conference"
    if "email" in text or "mailed" in text:
        return "Email"
    if "call" in text or "phone" in text or "telephonic" in text:
        return "Call"
    return "Meeting"


def _find_date(transcript: str) -> str:
    match = re.search(r"\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b", transcript)
    if not match:
        return ""
    day, month, year = match.groups()
    return f"{int(day):02d}-{int(month):02d}-{year}"


def _find_time(transcript: str) -> str:
    match = re.search(r"\b(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)?\b", transcript)
    if not match:
        return ""

    hour_text, minute, meridiem = match.groups()
    hour = int(hour_text)
    if meridiem:
        meridiem = meridiem.lower()
        if meridiem == "pm" and hour != 12:
            hour += 12
        if meridiem == "am" and hour == 12:
            hour = 0
    if hour > 23:
        return ""
    return f"{hour:02d}:{minute}"


def _find_hcp_name(transcript: str) -> str:
    patterns = [
        r"\bDr\.?\s+[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?",
        r"(?i:\b(?:met|visited|called|spoke with|meeting with))\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)",
        r"(?i:\bHCP\s*(?:name)?\s*[:\-]\s*)([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, transcript)
        if match:
            name = match.group(1) if match.lastindex else match.group(0)
            return _format_hcp_name(name)
    return "Unknown HCP"


def _find_product(transcript: str) -> str:
    patterns = [
        r"\b(?:product|drug|medicine|therapy)\s*(?:discussed)?\s*[:\-]?\s*([A-Z][a-zA-Z0-9-]+)",
        r"\bdiscussed\s+([A-Z][a-zA-Z0-9-]+)",
        r"\babout\s+([A-Z][a-zA-Z0-9-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, transcript, re.IGNORECASE)
        if match:
            product = match.group(1).strip(" .,:;\"'")
            if product.lower() not in STOP_WORDS:
                return product
    return "General discussion"


def _find_sentiment(transcript: str) -> str:
    text = transcript.lower()
    if any(word in text for word in ["interested", "positive", "agreed", "liked"]):
        return "positive"
    if any(word in text for word in ["worried", "concern", "concerned", "pricing", "risk"]):
        return "concerned"
    return "neutral"


def _find_action_items(transcript: str) -> list[str]:
    actions = []
    if log_resource_request(transcript):
        actions.append("Send requested resources")
    if "follow" in transcript.lower() or "call back" in transcript.lower():
        actions.append("Schedule follow-up")
    return actions or ["Review and confirm interaction log"]


def _format_hcp_name(name: str) -> str:
    cleaned = name.strip(" .,:;\"'")
    if cleaned.lower().startswith("dr"):
        cleaned = re.sub(r"^Dr\.?\s*", "Dr. ", cleaned, flags=re.IGNORECASE)
        return cleaned
    return f"Dr. {cleaned}"