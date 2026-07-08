from app.agents.hcp_agent import analyze_transcript


def test_analyze_transcript_extracts_basic_draft():
    draft = analyze_transcript("Met Dr. Sharma. Interested in product CardioMax but worried about pricing. Requested study material.")

    assert draft.hcp_name == "Dr. Sharma"
    assert draft.sentiment == "positive"
    assert draft.resource_request == "resource_follow_up_needed"
    assert draft.compliance_status == "clear"
