import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_get_activities_returns_activity_details(client):
    response = client.get("/activities")

    assert response.status_code == 200
    result = response.json()
    assert "Soccer Team" in result
    assert result["Soccer Team"]["participants"] == []
    assert result["Soccer Team"]["max_participants"] == 18


def test_signup_adds_participant(client):
    email = "new-student@mergington.edu"

    response = client.post("/activities/Soccer Team/signup", params={"email": email})

    assert response.status_code == 200
    assert email in activities["Soccer Team"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    email = "new-student@mergington.edu"
    client.post("/activities/Soccer Team/signup", params={"email": email})

    response = client.post("/activities/Soccer Team/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_unknown_activity(client):
    response = client.post("/activities/Unknown Activity/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    email = "registered-student@mergington.edu"
    activities["Soccer Team"]["participants"].append(email)

    response = client.delete("/activities/Soccer Team/signup", params={"email": email})

    assert response.status_code == 200
    assert email not in activities["Soccer Team"]["participants"]


def test_unregister_rejects_unregistered_participant(client):
    response = client.delete(
        "/activities/Soccer Team/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"