"""
Integration tests that test multiple endpoints together
"""
import pytest


def test_full_signup_flow(client, reset_activities):
    """Test complete signup and unregister flow"""
    email = "flowtest@mergington.edu"
    activity = "Programming Class"
    
    # 1. Check initial state
    response = client.get("/activities")
    initial_data = response.json()
    initial_count = len(initial_data[activity]["participants"])
    assert email not in initial_data[activity]["participants"]
    
    # 2. Sign up
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    
    # 3. Verify signup
    response = client.get("/activities")
    after_signup_data = response.json()
    assert len(after_signup_data[activity]["participants"]) == initial_count + 1
    assert email in after_signup_data[activity]["participants"]
    
    # 4. Try to sign up again (should fail)
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    
    # 5. Unregister
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    
    # 6. Verify unregister
    response = client.get("/activities")
    after_unregister_data = response.json()
    assert len(after_unregister_data[activity]["participants"]) == initial_count
    assert email not in after_unregister_data[activity]["participants"]
    
    # 7. Try to unregister again (should fail)
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 400


def test_cross_activity_operations(client, reset_activities):
    """Test operations across different activities"""
    email = "crosstest@mergington.edu"
    activities_list = ["Chess Club", "Programming Class", "Art Club"]
    
    # Sign up for multiple activities
    for activity in activities_list:
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
    
    # Verify student is in all activities
    response = client.get("/activities")
    data = response.json()
    for activity in activities_list:
        assert email in data[activity]["participants"]
    
    # Unregister from middle activity only
    middle_activity = activities_list[1]  # Programming Class
    response = client.delete(f"/activities/{middle_activity}/unregister?email={email}")
    assert response.status_code == 200
    
    # Verify student is removed from middle activity but remains in others
    response = client.get("/activities")
    data = response.json()
    assert email not in data[middle_activity]["participants"]
    assert email in data[activities_list[0]]["participants"]  # Chess Club
    assert email in data[activities_list[2]]["participants"]  # Art Club


def test_activity_capacity_management(client, reset_activities):
    """Test that activities properly track participant counts"""
    activity = "Mathletes"  # Has max_participants: 10
    
    # Get initial state
    response = client.get("/activities")
    initial_data = response.json()
    max_participants = initial_data[activity]["max_participants"]
    initial_count = len(initial_data[activity]["participants"])
    
    # Calculate how many more students we can add
    available_spots = max_participants - initial_count
    
    # Add students up to capacity
    new_emails = [f"student{i}@mergington.edu" for i in range(available_spots)]
    
    for email in new_emails:
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
    
    # Verify all students were added
    response = client.get("/activities")
    final_data = response.json()
    final_participants = final_data[activity]["participants"]
    
    assert len(final_participants) == max_participants
    for email in new_emails:
        assert email in final_participants


def test_data_persistence_across_requests(client, reset_activities):
    """Test that data changes persist across multiple requests"""
    email1 = "persist1@mergington.edu"
    email2 = "persist2@mergington.edu"
    activity = "Drama Society"
    
    # Add first student
    response = client.post(f"/activities/{activity}/signup?email={email1}")
    assert response.status_code == 200
    
    # Add second student
    response = client.post(f"/activities/{activity}/signup?email={email2}")
    assert response.status_code == 200
    
    # Verify both are present in a new request
    response = client.get("/activities")
    data = response.json()
    participants = data[activity]["participants"]
    assert email1 in participants
    assert email2 in participants
    
    # Remove first student
    response = client.delete(f"/activities/{activity}/unregister?email={email1}")
    assert response.status_code == 200
    
    # Verify first is gone but second remains
    response = client.get("/activities")
    data = response.json()
    participants = data[activity]["participants"]
    assert email1 not in participants
    assert email2 in participants


def test_error_handling_consistency(client, reset_activities):
    """Test that error responses are consistent across endpoints"""
    nonexistent_activity = "Fake Club"
    valid_email = "test@mergington.edu"
    
    # Test 404 responses
    signup_response = client.post(f"/activities/{nonexistent_activity}/signup?email={valid_email}")
    unregister_response = client.delete(f"/activities/{nonexistent_activity}/unregister?email={valid_email}")
    
    assert signup_response.status_code == 404
    assert unregister_response.status_code == 404
    
    # Both should have similar error structure
    signup_data = signup_response.json()
    unregister_data = unregister_response.json()
    
    assert "detail" in signup_data
    assert "detail" in unregister_data
    assert "Activity not found" in signup_data["detail"]
    assert "Activity not found" in unregister_data["detail"]