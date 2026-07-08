from pydantic import BaseModel, Field


class InteractionAnalyzeRequest(BaseModel):
    transcript: str = Field(min_length=3)


class InteractionDraft(BaseModel):
    hcp_name: str
    product: str
    sentiment: str
    action_items: list[str]
    compliance_status: str
    resource_request: str | None = None
    competitive_intelligence: str | None = None
    draft_summary: str
