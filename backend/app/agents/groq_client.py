import json
import re
from typing import Any

from app.core.config import settings


class HcpGroqLLM:
    """Small adapter around Groq so the CRM tools do not depend on LangChain details."""

    def __init__(self) -> None:
        if not settings.groq_api_key or settings.groq_api_key == "replace_with_your_groq_api_key":
            raise RuntimeError("GROQ_API_KEY is required for LLM-backed extraction.")

        try:
            from langchain_groq import ChatGroq
        except ImportError as exc:
            raise RuntimeError("Install langchain-groq to use Groq-backed extraction.") from exc

        self.model_name = settings.primary_model
        self.chat = ChatGroq(
            model=settings.primary_model,
            temperature=0,
            groq_api_key=settings.groq_api_key,
        )

    def extract_interaction(self, transcript: str, defaults: dict[str, Any]) -> dict[str, Any]:
        prompt = _build_extraction_prompt(transcript, defaults)
        response = self.chat.invoke(prompt)
        payload = _parse_json_object(getattr(response, "content", str(response)))

        return {
            "hcp_name": _clean_string(payload.get("hcp_name")) or defaults["hcp_name"],
            "product": _clean_string(payload.get("product")) or defaults["product"],
            "sentiment": _normalize_sentiment(payload.get("sentiment")) or defaults["sentiment"],
            "interaction_type": _normalize_interaction_type(payload.get("interaction_type")) or defaults["interaction_type"],
            "date": _clean_string(payload.get("date")) or defaults["date"],
            "time": _clean_string(payload.get("time")) or defaults["time"],
            "action_items": _clean_action_items(payload.get("action_items")) or defaults["action_items"],
            "draft_summary": _clean_string(payload.get("draft_summary")) or None,
        }


def get_llm_client() -> HcpGroqLLM | None:
    if not settings.groq_api_key or settings.groq_api_key == "replace_with_your_groq_api_key":
        return None
    return HcpGroqLLM()


def _build_extraction_prompt(transcript: str, defaults: dict[str, Any]) -> str:
    return f"""
You are the AI agent inside an HCP CRM used by pharmaceutical field representatives.
Extract a concise interaction draft from the note below.
Return only valid JSON with these keys: hcp_name, product, sentiment, interaction_type, date, time, action_items, draft_summary.
Sentiment must be one of: positive, neutral, concerned.
Interaction type must be one of: Meeting, Call, Email, Conference.
Date must use DD-MM-YYYY format when present.
Time must use 24-hour HH:mm format when present.
Action items must be an array of short sales follow-up tasks.
Use the fallback JSON if the note does not include a value.

Fallback JSON:
{json.dumps(defaults, ensure_ascii=True)}

Interaction note:
{transcript}
""".strip()


def _parse_json_object(text: str) -> dict[str, Any]:
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return {}
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _clean_string(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _normalize_sentiment(value: Any) -> str:
    sentiment = _clean_string(value).lower()
    return sentiment if sentiment in {"positive", "neutral", "concerned"} else ""


def _normalize_interaction_type(value: Any) -> str:
    normalized = _clean_string(value).lower()
    option_map = {
        "meeting": "Meeting",
        "call": "Call",
        "email": "Email",
        "conference": "Conference",
    }
    return option_map.get(normalized, "")


def _clean_action_items(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]