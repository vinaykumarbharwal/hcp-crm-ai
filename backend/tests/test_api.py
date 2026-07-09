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
