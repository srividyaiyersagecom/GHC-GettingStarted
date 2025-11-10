"""
Test cases for the root endpoint and activities endpoint
"""
import pytest


def test_root_redirect(client, reset_activities):
    """Test that root endpoint redirects to static/index.html"""
    response = client.get("/")
    assert response.status_code == 200
    # FastAPI's RedirectResponse returns 200 when followed by TestClient


def test_get_activities(client, reset_activities):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    
    # Check that we have the expected activities
    expected_activities = [
        "Chess Club", "Programming Class", "Gym Class", "Soccer Team",
        "Basketball Club", "Art Club", "Drama Society", "Mathletes", "Science Club"
    ]
    
    for activity in expected_activities:
        assert activity in data
    
    # Check structure of an activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)
    assert chess_club["max_participants"] == 12
    assert "michael@mergington.edu" in chess_club["participants"]


def test_activities_data_integrity(client, reset_activities):
    """Test that activities have all required fields with correct data types"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    
    for activity_name, activity_data in data.items():
        # Check required fields exist
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        
        # Check data types
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)
        
        # Check that max_participants is positive
        assert activity_data["max_participants"] > 0
        
        # Check that all participants are email strings
        for participant in activity_data["participants"]:
            assert isinstance(participant, str)
            assert "@" in participant