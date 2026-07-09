import re
from typing import Any, Protocol


class InteractionExtractor(Protocol):
    def extract_interaction(self, transcript: str, defaults: dict[str, Any]) -> dict[str, Any]:
        ...


STOP_WORDS = {
    "he", "she", "they", "it", "we", "i", "the", "a", "an", "new", "pricing", "sample",
    "study", "material", "brochure", "positive", "neutral", "concerned", "worried", "interested"
}

NAME_STOP_WORDS = (
    "from|at|on|in|with|about|for|to|interaction|discussed|discuss|called|"
    "phone|email|meeting|call|visited|spoke|update|change|product|sentiment|date|time"
)
NAME_TOKEN = rf"(?!(?:{NAME_STOP_WORDS})\b)[A-Za-z][A-Za-z'-]*"
NAME_PATTERN = rf"{NAME_TOKEN}(?:\s+{NAME_TOKEN}){{0,3}}"
NAME_TERMINATOR = rf"(?=$|\s*(?:[,.;:]|\b(?:{NAME_STOP_WORDS})\b))"


# Sales tool 1: Log Interaction. The LLM path extracts core fields and summarizes the note.
def log_interaction(transcript: str, llm_client: InteractionExtractor | None = None) -> dict:
    # Local fallback keeps extraction usable without an LLM/API key.
    defaults = {
        "hcp_name": _find_hcp_name(transcript),
        "product": _find_product(transcript),
        "sentiment": _find_sentiment(transcript),
        "interaction_type": _find_interaction_type(transcript),
        "date": _find_date(transcript),
        "time": _find_time(transcript),
        "attendees": _find_attendees(transcript),
        "topics": _find_topics(transcript),
        "outcomes": _find_outcomes(transcript),
        "materials": _find_materials(transcript),
        "samples": _find_samples(transcript),
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
        "attendees": extracted.get("attendees") or defaults["attendees"],
        "topics": extracted.get("topics") or defaults["topics"],
        "outcomes": extracted.get("outcomes") or defaults["outcomes"],
        "materials": extracted.get("materials") or defaults["materials"],
        "samples": extracted.get("samples") or defaults["samples"],
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
    # Accept dates even when pasted text inserts spaces or line breaks around dashes.
    match = re.search(r"\b(\d{1,2})\s*[-/]\s*(\d{1,2})\s*[-/]\s*(\d{4})\b", transcript)
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


def _find_attendees(transcript: str) -> str:
    hcp_name = _find_hcp_name(transcript)
    return "" if hcp_name == "Unknown HCP" else hcp_name


def _find_topics(transcript: str) -> str:
    # Topics are treated as the first sentence after "discussed".
    match = re.search(r"\bdiscussed\s+(.+?)(?:\.|$)", transcript, re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    topics = re.sub(r"\s+", " ", match.group(1)).strip(" .")
    return topics


def _find_materials(transcript: str) -> str:
    text = transcript.lower()
    materials = []
    if "brochure" in text:
        materials.append("Brochure")
    if "clinical data" in text:
        materials.append("Clinical data")
    if "study" in text or "studies" in text:
        materials.append("Study material")
    return ", ".join(dict.fromkeys(materials))


def _find_samples(transcript: str) -> str:
    return "Samples requested" if "sample" in transcript.lower() else ""


def _find_outcomes(transcript: str) -> str:
    # Outcome-like sentences feed the editable Outcomes field.
    sentences = [re.sub(r"\s+", " ", item).strip() for item in re.split(r"(?<=[.!?])\s+", transcript) if item.strip()]
    outcome_sentences = [
        sentence.strip(" .")
        for sentence in sentences
        if re.search(r"\b(requested|follow up|follow-up|agreed|outcome|consider|review)\b", sentence, re.IGNORECASE)
    ]
    return ". ".join(outcome_sentences)


def _find_hcp_name(transcript: str) -> str:
    patterns = [
        rf"\bdr\.?\s+({NAME_PATTERN}){NAME_TERMINATOR}",
        rf"\b(?:met|visited|called|spoke with|meeting with)\s+(?:dr\.?\s+)?({NAME_PATTERN}){NAME_TERMINATOR}",
        rf"\bhcp\s*(?:name)?\s*[:\-]\s*(?:dr\.?\s+)?({NAME_PATTERN}){NAME_TERMINATOR}",
    ]
    for pattern in patterns:
        match = re.search(pattern, transcript, re.IGNORECASE)
        if match:
            name = match.group(1) if match.lastindex else match.group(0)
            return _format_hcp_name(name)
    return "Unknown HCP"


def _find_product(transcript: str) -> str:
    patterns = [
        r"\b(?:product|drug|medicine|therapy)\s*(?:discussed|is|was)?\s*[:\-]?\s*([A-Z][a-zA-Z0-9-]+)",
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
    if any(word in text for word in ["worried", "concern", "concerned", "negative", "unhappy", "not interested", "hesitant", "pricing", "risk"]):
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
        return _titlecase_hcp_name(cleaned)
    return f"Dr. {_titlecase_hcp_name(cleaned)}"


def _titlecase_hcp_name(name: str) -> str:
    parts = name.split()
    if parts and parts[0].lower().rstrip(".") == "dr":
        return " ".join(["Dr.", *[_titlecase_name_part(part) for part in parts[1:]]])
    return " ".join(_titlecase_name_part(part) for part in parts)


def _titlecase_name_part(part: str) -> str:
    if part.islower() or part.isupper():
        return part[:1].upper() + part[1:].lower()
    return part

