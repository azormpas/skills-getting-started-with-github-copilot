"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI application"""
    return TestClient(app)


@pytest.fixture
def fresh_activities(monkeypatch):
    """Provide fresh activities state for each test to prevent cross-test contamination"""
    fresh_data = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice and compete in basketball games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Train and play soccer matches",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act in plays and improve theatrical skills",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["mason@mergington.edu", "charlotte@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["ethan@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["harper@mergington.edu", "logan@mergington.edu"]
        }
    }
    
    # Replace the module-level activities dict with fresh data
    monkeypatch.setattr("src.app.activities", fresh_data)
    return fresh_data


# ==================== GET /activities Tests ====================

def test_get_activities_returns_all_activities(client, fresh_activities):
    """Test that GET /activities returns all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 9
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Science Club" in data


def test_get_activities_response_structure(client, fresh_activities):
    """Test that each activity has the correct structure"""
    response = client.get("/activities")
    data = response.json()
    
    activity = data["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    
    assert isinstance(activity["description"], str)
    assert isinstance(activity["schedule"], str)
    assert isinstance(activity["max_participants"], int)
    assert isinstance(activity["participants"], list)


def test_get_activities_contains_correct_data(client, fresh_activities):
    """Test that activity data matches expected values"""
    response = client.get("/activities")
    data = response.json()
    
    chess_club = data["Chess Club"]
    assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
    assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert chess_club["max_participants"] == 12
    assert len(chess_club["participants"]) == 2
    assert "michael@mergington.edu" in chess_club["participants"]


# ==================== POST /activities/{activity_name}/signup Tests ====================

def test_signup_new_participant_happy_path(client, fresh_activities):
    """Test successful signup of a new participant"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "newstudent@mergington.edu" in data["message"]
    assert "Chess Club" in data["message"]
    
    # Verify participant was added
    activities_response = client.get("/activities")
    updated_activity = activities_response.json()["Chess Club"]
    assert "newstudent@mergington.edu" in updated_activity["participants"]
    assert len(updated_activity["participants"]) == 3


def test_signup_participant_to_different_activities(client, fresh_activities):
    """Test signing up same email to multiple different activities"""
    email = "multijoiner@mergington.edu"
    
    # Sign up for Chess Club
    response1 = client.post(
        "/activities/Chess Club/signup",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Sign up for Programming Class
    response2 = client.post(
        "/activities/Programming Class/signup",
        params={"email": email}
    )
    assert response2.status_code == 200
    
    # Verify both signups worked
    activities_response = client.get("/activities")
    data = activities_response.json()
    assert email in data["Chess Club"]["participants"]
    assert email in data["Programming Class"]["participants"]


def test_signup_nonexistent_activity_returns_404(client, fresh_activities):
    """Test signup to non-existent activity returns 404"""
    response = client.post(
        "/activities/Nonexistent Club/signup",
        params={"email": "student@mergington.edu"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_already_registered_returns_400(client, fresh_activities):
    """Test signup when student already registered returns 400"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_case_sensitive_email(client, fresh_activities):
    """Test that signup preserves email case (different case = different signup)"""
    response1 = client.post(
        "/activities/Soccer Club/signup",
        params={"email": "NewStudent@mergington.edu"}
    )
    assert response1.status_code == 200
    
    response2 = client.post(
        "/activities/Soccer Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    # Should succeed because case is different
    assert response2.status_code == 200


def test_signup_multiple_participants_to_same_activity(client, fresh_activities):
    """Test adding multiple different participants to same activity"""
    activity_name = "Art Club"
    emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
    
    for email in emails:
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify all were added
    activities_response = client.get("/activities")
    art_club = activities_response.json()["Art Club"]
    for email in emails:
        assert email in art_club["participants"]
    
    # Original had 1 participant, now should have 4
    assert len(art_club["participants"]) == 4


# ==================== DELETE /activities/{activity_name}/unregister Tests ====================

def test_unregister_existing_participant_happy_path(client, fresh_activities):
    """Test successful unregistration of an existing participant"""
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "michael@mergington.edu"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    assert "michael@mergington.edu" in data["message"]
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    updated_activity = activities_response.json()["Chess Club"]
    assert "michael@mergington.edu" not in updated_activity["participants"]
    assert len(updated_activity["participants"]) == 1


def test_unregister_all_participants_from_activity(client, fresh_activities):
    """Test unregistering all participants from an activity"""
    activity_name = "Basketball Team"
    email = "alex@mergington.edu"
    
    # Basketball Team has 1 participant
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify all participants removed
    activities_response = client.get("/activities")
    activity = activities_response.json()[activity_name]
    assert len(activity["participants"]) == 0


def test_unregister_from_nonexistent_activity_returns_404(client, fresh_activities):
    """Test unregister from non-existent activity returns 404"""
    response = client.delete(
        "/activities/Nonexistent Club/unregister",
        params={"email": "student@mergington.edu"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_nonexistent_participant_returns_400(client, fresh_activities):
    """Test unregister of non-participant returns 400"""
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "notregistered@mergington.edu"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]


def test_unregister_then_signup_again(client, fresh_activities):
    """Test unregistering and then signing up again"""
    email = "togglestudent@mergington.edu"
    activity_name = "Programming Class"
    
    # Sign up
    response1 = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Unregister
    response2 = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    assert response2.status_code == 200
    
    # Sign up again
    response3 = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert response3.status_code == 200
    
    # Verify final state
    activities_response = client.get("/activities")
    activity = activities_response.json()[activity_name]
    assert email in activity["participants"]


def test_unregister_one_of_multiple_participants(client, fresh_activities):
    """Test unregistering one participant when multiple are signed up"""
    activity_name = "Drama Club"
    
    # Initially has 2: mason@mergington.edu, charlotte@mergington.edu
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": "mason@mergington.edu"}
    )
    assert response.status_code == 200
    
    # Verify only one removed
    activities_response = client.get("/activities")
    activity = activities_response.json()[activity_name]
    assert "mason@mergington.edu" not in activity["participants"]
    assert "charlotte@mergington.edu" in activity["participants"]
    assert len(activity["participants"]) == 1


# ==================== Integration Tests ====================

def test_signup_and_unregister_flow(client, fresh_activities):
    """Test complete signup and unregister flow"""
    email = "flowtest@mergington.edu"
    activity = "Science Club"
    
    # Initial state
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()[activity]["participants"])
    
    # Sign up
    signup_response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert signup_response.status_code == 200
    
    # Verify signup
    after_signup = client.get("/activities")
    assert len(after_signup.json()[activity]["participants"]) == initial_count + 1
    assert email in after_signup.json()[activity]["participants"]
    
    # Unregister
    unregister_response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    assert unregister_response.status_code == 200
    
    # Verify unregister
    after_unregister = client.get("/activities")
    assert len(after_unregister.json()[activity]["participants"]) == initial_count
    assert email not in after_unregister.json()[activity]["participants"]
