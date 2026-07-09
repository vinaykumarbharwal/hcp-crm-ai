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

def test_analyze_transcript_maps_negative_sentiment_to_concerned():
    draft = analyze_transcript("Met Dr. Sharma, discussed CardioMax, negative sentiment about pricing.")

    assert draft.sentiment == "concerned"

def test_analyze_transcript_extracts_form_details_from_multiline_note():
    draft = analyze_transcript(
        "I had a phone call with Dr. Ananya Rao from Apollo Hospitals, Bengaluru on 22-\n"
        "  05-2025 at 11:15. We discussed GlucoCare safety, patient adherence, and\n"
        "  competitor MedicoPlus. She was negative about pricing but requested study\n"
        "  material and samples. Follow up next week with brochure and clinical data."
    )

    assert draft.interaction_type == "Call"
    assert draft.date == "22-05-2025"
    assert draft.time == "11:15"
    assert draft.attendees == "Dr. Ananya Rao"
    assert draft.topics == "GlucoCare safety, patient adherence, and competitor MedicoPlus"
    assert draft.samples == "Samples requested"
    assert draft.materials == "Brochure, Clinical data, Study material"
    assert "requested study material and samples" in draft.outcomes
    assert "Follow up next week with brochure and clinical data" in draft.outcomes



def test_analyze_transcript_extracts_lowercase_dr_name():
    draft = analyze_transcript("met dr. vinay discussed CardioMax safety and requested samples")

    assert draft.hcp_name == "Dr. Vinay"
    assert draft.attendees == "Dr. Vinay"
    assert draft.product == "CardioMax"
