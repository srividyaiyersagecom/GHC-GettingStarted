"""
Test cases for signup functionality
"""
import pytest


def test_signup_success(client, reset_activities):
    """Test successful signup for an activity"""
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    
    # Get initial participant count
    response = client.get("/activities")
    initial_data = response.json()
    initial_participants = len(initial_data[activity]["participants"])
    
    # Sign up for activity
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity in data["message"]
    
    # Verify participant was added
    response = client.get("/activities")
    updated_data = response.json()
    updated_participants = updated_data[activity]["participants"]
    
    assert len(updated_participants) == initial_participants + 1
    assert email in updated_participants


def test_signup_nonexistent_activity(client, reset_activities):
    """Test signup for non-existent activity"""
    email = "student@mergington.edu"
    activity = "Non-existent Club"
    
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 404
    
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_duplicate_email(client, reset_activities):
    """Test signup with email that's already registered"""
    email = "michael@mergington.edu"  # Already in Chess Club
    activity = "Chess Club"
    
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_signup_multiple_activities(client, reset_activities):
    """Test that a student can sign up for multiple activities"""
    email = "multistudent@mergington.edu"
    activities = ["Chess Club", "Programming Class", "Art Club"]
    
    for activity in activities:
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify student was added to this activity
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity]["participants"]


def test_signup_url_encoding(client, reset_activities):
    """Test signup with special characters in activity name"""
    # Create a URL-encoded activity name
    email = "student@mergington.edu"
    activity = "Chess Club"  # Contains space
    encoded_activity = "Chess%20Club"
    
    response = client.post(f"/activities/{encoded_activity}/signup?email={email}")
    assert response.status_code == 200
    
    # Verify participant was added
    response = client.get("/activities")
    data = response.json()
    assert email in data[activity]["participants"]


def test_signup_empty_email(client, reset_activities):
    """Test signup with empty email parameter"""
    activity = "Chess Club"
    
    response = client.post(f"/activities/{activity}/signup?email=")
    # This should still work as an empty string is a valid parameter value
    assert response.status_code == 200
    
    # Verify empty string was added (though not realistic)
    response = client.get("/activities")
    data = response.json()
    assert "" in data[activity]["participants"]