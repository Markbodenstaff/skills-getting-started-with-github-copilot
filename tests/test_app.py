import pytest
from fastapi.testclient import TestClient
from src.app import app


def test_get_root_redirect():
    """Test that GET / redirects to the static frontend"""
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    """Test that GET /activities returns all activities"""
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Based on hardcoded activities
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Verify structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_success():
    """Test successful signup for an activity"""
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data == {"message": f"Signed up {email} for {activity_name}"}
    # Verify email was added to participants
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email in activities_data[activity_name]["participants"]


def test_signup_duplicate_email():
    """Test signup fails when student is already signed up"""
    # Arrange
    client = TestClient(app)
    activity_name = "Programming Class"
    email = "duplicate@mergington.edu"

    # First signup (should succeed)
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act - Second signup with same email
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student already signed up"


def test_signup_invalid_activity():
    """Test signup fails for non-existent activity"""
    # Arrange
    client = TestClient(app)
    invalid_activity = "NonExistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{invalid_activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"