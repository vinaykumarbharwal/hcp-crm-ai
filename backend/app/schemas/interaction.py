from pydantic import BaseModel, ConfigDict, Field


class InteractionAnalyzeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    transcript: str = ""
    hcp_name: str = Field(default="", alias="hcpName")
    product: str = ""
    interaction_type: str = Field(default="", alias="interactionType")
    date: str = ""
    time: str = ""
    attendees: str = ""
    topics: str = ""
    sentiment: str = "neutral"
    outcomes: str = ""
    follow_ups: str = Field(default="", alias="followUps")

    def has_interaction_content(self) -> bool:
        """Return true only when the user entered meaningful interaction details."""
        fields = [
            self.transcript,
            self.hcp_name,
            self.product,
            self.attendees,
            self.topics,
            self.outcomes,
            self.follow_ups,
        ]
        return any(field.strip() for field in fields)

    def combined_transcript(self) -> str:
        """Build one readable note from chat text and structured form fields."""
        parts = [
            self.transcript,
            f"Met {self.hcp_name}" if self.hcp_name else "",
            f"Interaction type: {self.interaction_type}" if self.interaction_type else "",
            f"Product discussed: {self.product}" if self.product else "",
            f"Attendees: {self.attendees}" if self.attendees else "",
            f"Topics discussed: {self.topics}" if self.topics else "",
            f"Observed sentiment: {self.sentiment}" if self.has_interaction_content() and self.sentiment else "",
            f"Outcomes: {self.outcomes}" if self.outcomes else "",
            f"Follow-up actions: {self.follow_ups}" if self.follow_ups else "",
        ]
        return ". ".join(part.strip(" .") for part in parts if part and part.strip())


class InteractionDraft(BaseModel):
    hcp_name: str
    product: str
    sentiment: str
    action_items: list[str]
    compliance_status: str
    resource_request: str | None = None
    competitive_intelligence: str | None = None
    draft_summary: str
