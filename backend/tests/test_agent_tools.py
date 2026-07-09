from app.agents.hcp_agent import _compiled_graph, analyze_transcript


def test_analyze_transcript_extracts_basic_draft():
    draft = analyze_transcript("Met Dr. Sharma. Interested in product CardioMax but worried about pricing. Requested study material.")

    assert draft.hcp_name == "Dr. Sharma"
    assert draft.product == "CardioMax"
    assert draft.sentiment == "positive"
    assert draft.resource_request == "resource_follow_up_needed"
    assert draft.compliance_status == "clear"


def test_analyze_transcript_handles_plain_sales_note():
    draft = analyze_transcript("met Sharma discussed CardioMax pricing concern and requested study material")

    assert draft.hcp_name == "Dr. Sharma"
    assert draft.product == "CardioMax"
    assert draft.sentiment == "concerned"
    assert "Send requested resources" in draft.action_items


def test_hcp_agent_uses_compiled_langgraph():
    graph = _compiled_graph()

    assert hasattr(graph, "invoke")

def test_analyze_transcript_extracts_interaction_type_date_and_time():
    draft = analyze_transcript(
        "I had a phone call with Dr. Ananya Rao from Apollo Hospitals, Bengaluru on 22-05-2025 at 11:15. "
        "We discussed GlucoCare safety and patient adherence."
    )

    assert draft.interaction_type == "Call"
    assert draft.date == "22-05-2025"
    assert draft.time == "11:15"