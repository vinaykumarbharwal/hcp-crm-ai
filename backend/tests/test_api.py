from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_includes_documented_routes():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/health" in paths
    assert "/api/interactions/analyze" in paths
    assert "/api/interactions/edit" in paths


def test_analyze_interaction_accepts_transcript():
    response = client.post(
        "/api/interactions/analyze",
        json={"transcript": "Met Dr. Sharma. Discussed product CardioMax and requested study material."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["hcp_name"] == "Dr. Sharma"
    assert body["product"] == "CardioMax"
    assert body["resource_request"] == "resource_follow_up_needed"
    assert isinstance(body["id"], int)


def test_analyze_interaction_rejects_empty_payload():
    response = client.post("/api/interactions/analyze", json={"transcript": ""})

    assert response.status_code == 400
    assert response.json() == {"detail": "Enter interaction notes or fill at least one interaction field."}


def test_analyze_interaction_accepts_structured_form_fields():
    response = client.post(
        "/api/interactions/analyze",
        json={
            "hcpName": "Dr. Smith",
            "product": "Product X",
            "interactionType": "Meeting",
            "topics": "efficacy and samples",
            "sentiment": "positive",
            "followUps": "Send brochure",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["hcp_name"] == "Dr. Smith"
    assert body["product"] == "Product X"
    assert body["sentiment"] == "positive"
    assert "Send brochure" in body["action_items"]
    assert isinstance(body["id"], int)


def test_edit_interaction_updates_existing_draft_without_erasing_blank_fields():
    response = client.post(
        "/api/interactions/edit",
        json={
            "existing": {
                "hcp_name": "Dr. Sharma",
                "product": "CardioMax",
                "sentiment": "neutral",
                "action_items": ["Send requested resources"],
                "compliance_status": "clear",
                "resource_request": "resource_follow_up_needed",
                "competitive_intelligence": None,
                "draft_summary": "Original summary",
            },
            "updates": {
                "hcpName": "Dr. Sharma",
                "product": "",
                "sentiment": "positive",
                "followUps": "Send updated brochure\nSchedule follow-up",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["hcp_name"] == "Dr. Sharma"
    assert body["product"] == "CardioMax"
    assert body["sentiment"] == "positive"
    assert body["action_items"] == ["Send updated brochure", "Schedule follow-up"]
    assert body["draft_summary"] == "Dr. Sharma discussed CardioMax with positive sentiment. Compliance status: clear."
    assert isinstance(body["id"], int)


def test_analyze_interaction_preserves_extracted_sentiment_without_form_override():
    response = client.post(
        "/api/interactions/analyze",
        json={"transcript": "Met Dr. Sharma, discussed CardioMax, positive sentiment, follow up next week."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["hcp_name"] == "Dr. Sharma"
    assert body["product"] == "CardioMax"
    assert body["sentiment"] == "positive"
    assert "Schedule follow-up" in body["action_items"]
    assert body["draft_summary"] == "Dr. Sharma discussed CardioMax with positive sentiment. Compliance status: clear."


def test_analyze_interaction_returns_extracted_interaction_type_date_and_time():
    response = client.post(
        "/api/interactions/analyze",
        json={
            "transcript": "I had a phone call with Dr. Ananya Rao from Apollo Hospitals, Bengaluru on 22-05-2025 at 11:15. We discussed GlucoCare safety."
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["interactionType"] == "Call"
    assert body["date"] == "22-05-2025"
    assert body["time"] == "11:15"

def test_edit_interaction_refreshes_summary_when_sentiment_changes_without_outcomes_override():
    response = client.post(
        "/api/interactions/edit",
        json={
            "existing": {
                "hcp_name": "Dr. Sharma",
                "product": "CardioMax",
                "sentiment": "positive",
                "interactionType": "Meeting",
                "date": "22-05-2025",
                "time": "11:15",
                "action_items": ["Review and confirm interaction log"],
                "compliance_status": "clear",
                "resource_request": None,
                "competitive_intelligence": None,
                "draft_summary": "Dr. Sharma discussed CardioMax with positive sentiment. Compliance status: clear.",
            },
            "updates": {
                "hcpName": "Dr. Sharma",
                "product": "CardioMax",
                "sentiment": "concerned",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["sentiment"] == "concerned"
    assert body["draft_summary"] == "Dr. Sharma discussed CardioMax with concerned sentiment. Compliance status: clear."

def test_edit_interaction_extracts_updates_from_chat_instruction():
    response = client.post(
        "/api/interactions/edit",
        json={
            "existing": {
                "hcp_name": "Dr. Ananya Rao",
                "product": "GlucoCare",
                "sentiment": "concerned",
                "interactionType": "Call",
                "date": "22-05-2025",
                "time": "11:15",
                "action_items": ["Schedule follow-up"],
                "compliance_status": "clear",
                "resource_request": "resource_follow_up_needed",
                "competitive_intelligence": "competitor_or_alternative_mentioned",
                "draft_summary": "Dr. Ananya Rao discussed GlucoCare with concerned sentiment. Compliance status: clear.",
            },
            "updates": {
                "transcript": "Update Dr. Ananya Rao interaction to Email on 24-05-2025 at 16:30. Change sentiment to positive. Product is GlucoCare. Follow-up: send updated brochure and schedule a call next week.",
                "hcpName": "Dr. Ananya Rao",
                "product": "GlucoCare",
                "interactionType": "Call",
                "date": "22-05-2025",
                "time": "11:15",
                "sentiment": "concerned",
                "followUps": "Schedule follow-up",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["interactionType"] == "Email"
    assert body["date"] == "24-05-2025"
    assert body["time"] == "16:30"
    assert body["sentiment"] == "positive"
    assert body["action_items"] == ["send updated brochure and schedule a call next week"]
    assert body["draft_summary"] == "Dr. Ananya Rao discussed GlucoCare with positive sentiment. Compliance status: clear."

def test_analyze_interaction_returns_form_detail_fields_from_multiline_note():
    response = client.post(
        "/api/interactions/analyze",
        json={
            "transcript": (
                "I had a phone call with Dr. Ananya Rao from Apollo Hospitals, Bengaluru on 22-\n"
                "  05-2025 at 11:15. We discussed GlucoCare safety, patient adherence, and\n"
                "  competitor MedicoPlus. She was negative about pricing but requested study\n"
                "  material and samples. Follow up next week with brochure and clinical data."
            )
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["date"] == "22-05-2025"
    assert body["attendees"] == "Dr. Ananya Rao"
    assert body["topics"] == "GlucoCare safety, patient adherence, and competitor MedicoPlus"
    assert body["samples"] == "Samples requested"
    assert body["materials"] == "Brochure, Clinical data, Study material"
    assert "requested study material and samples" in body["outcomes"]

