"""
Test cases for unregister functionality
"""
import pytest


def test_unregister_success(client, reset_activities):
    """Test successful unregistration from an activity"""
    email = "michael@mergington.edu"  # Already in Chess Club
    activity = "Chess Club"
    
    # Get initial participant count
    response = client.get("/activities")
    initial_data = response.json()
    initial_participants = len(initial_data[activity]["participants"])
    assert email in initial_data[activity]["participants"]
    
    # Unregister from activity
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity in data["message"]
    
    # Verify participant was removed
    response = client.get("/activities")
    updated_data = response.json()
    updated_participants = updated_data[activity]["participants"]
    
    assert len(updated_participants) == initial_participants - 1
    assert email not in updated_participants


def test_unregister_nonexistent_activity(client, reset_activities):
    """Test unregister from non-existent activity"""
    email = "student@mergington.edu"
    activity = "Non-existent Club"
    
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 404
    
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_not_signed_up(client, reset_activities):
    """Test unregister when student is not signed up"""
    email = "notstudent@mergington.edu"  # Not in any activity
    activity = "Chess Club"
    
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 400
    
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]


def test_unregister_and_resign_up(client, reset_activities):
    """Test unregister followed by signup again"""
    email = "daniel@mergington.edu"  # Already in Chess Club
    activity = "Chess Club"
    
    # First unregister
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    
    # Verify removal
    response = client.get("/activities")
    data = response.json()
    assert email not in data[activity]["participants"]
    
    # Then sign up again
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    
    # Verify addition
    response = client.get("/activities")
    data = response.json()
    assert email in data[activity]["participants"]


def test_unregister_url_encoding(client, reset_activities):
    """Test unregister with special characters in activity name"""
    email = "emma@mergington.edu"  # Already in Programming Class
    activity = "Programming Class"  # Contains space
    encoded_activity = "Programming%20Class"
    
    response = client.delete(f"/activities/{encoded_activity}/unregister?email={email}")
    assert response.status_code == 200
    
    # Verify participant was removed
    response = client.get("/activities")
    data = response.json()
    assert email not in data[activity]["participants"]


def test_unregister_multiple_activities(client, reset_activities):
    """Test unregistering from multiple activities"""
    email = "newstudent@mergington.edu"
    activities = ["Chess Club", "Programming Class", "Art Club"]
    
    # First sign up for multiple activities
    for activity in activities:
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
    
    # Then unregister from all of them
    for activity in activities:
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify student was removed from this activity
        response = client.get("/activities")
        data = response.json()
        assert email not in data[activity]["participants"]


def test_unregister_preserves_other_participants(client, reset_activities):
    """Test that unregistering one participant doesn't affect others"""
    activity = "Chess Club"
    email_to_remove = "michael@mergington.edu"
    email_to_keep = "daniel@mergington.edu"
    
    # Get initial state
    response = client.get("/activities")
    initial_data = response.json()
    initial_participants = set(initial_data[activity]["participants"])
    
    assert email_to_remove in initial_participants
    assert email_to_keep in initial_participants
    
    # Unregister one participant
    response = client.delete(f"/activities/{activity}/unregister?email={email_to_remove}")
    assert response.status_code == 200
    
    # Verify only the target participant was removed
    response = client.get("/activities")
    updated_data = response.json()
    updated_participants = set(updated_data[activity]["participants"])
    
    assert email_to_remove not in updated_participants
    assert email_to_keep in updated_participants
    assert len(updated_participants) == len(initial_participants) - 1