"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    
    # Store original state
    original = {
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
        "Soccer Team": {
            "description": "Competitive soccer training and matches",
            "schedule": "Mondays, Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 22,
            "participants": ["noah@mergington.edu", "liam@mergington.edu"]
        },
        "Track & Field": {
            "description": "Running, jumping and throwing events; conditioning and meets",
            "schedule": "Tuesdays, Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["ava@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Club": {
            "description": "Drawing, painting, and mixed-media workshops",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["charlotte@mergington.edu", "amelia@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, stagecraft, and production of school plays",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["mason@mergington.edu", "lucas@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate practice and tournament preparation",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["grace@mergington.edu", "henry@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments, research projects, and science fairs",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["mia@mergington.edu", "jack@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original)
    
    yield
    
    # Reset again after test
    activities.clear()
    activities.update(original)


class TestRoot:
    """Tests for the root endpoint"""
    
    def test_root_redirects(self, client):
        """Test that root endpoint redirects to static HTML"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities_data = response.json()
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data
        assert activities_data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    
    def test_activity_has_required_fields(self, client):
        """Test that activities have all required fields"""
        response = client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_info in activities_data.items():
            assert "description" in activity_info
            assert "schedule" in activity_info
            assert "max_participants" in activity_info
            assert "participants" in activity_info
            assert isinstance(activity_info["participants"], list)


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_duplicate_signup_prevention(self, client):
        """Test that duplicate signups are prevented"""
        # Try to sign up an already-registered student
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_activity_full_prevention(self, client):
        """Test that signup is prevented when activity is full"""
        # Create a nearly-full activity for testing
        response = client.get("/activities")
        activities_data = response.json()
        
        # Find an activity we can fill up
        # Soccer Team has max 22 and 2 participants, so we need to add 20 more
        for i in range(20):
            client.post(
                f"/activities/Soccer Team/signup?email=student{i}@mergington.edu"
            )
        
        # Now try to add one more (should still work - at capacity)
        response = client.post(
            "/activities/Soccer Team/signup?email=full@mergington.edu"
        )
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()
    
    def test_signup_multiple_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "multiplesignup@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify both signups
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Programming Class"]["participants"]


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_successful_unregister(self, client):
        """Test successful unregistration from an activity"""
        # Sign up first
        client.post("/activities/Chess Club/signup?email=temp@mergington.edu")
        
        # Then unregister
        response = client.delete(
            "/activities/Chess Club/unregister?email=temp@mergington.edu"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Verify removal
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "temp@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
    
    def test_unregister_not_signed_up_student(self, client):
        """Test unregister for student not signed up returns 400"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notstudent@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()
    
    def test_unregister_original_participant(self, client):
        """Test unregistering an originally registered participant"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify removal
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]


class TestIntegration:
    """Integration tests for signup and unregister workflows"""
    
    def test_signup_and_unregister_workflow(self, client):
        """Test complete signup and unregister workflow"""
        email = "integration@mergington.edu"
        activity = "Programming Class"
        
        # Initial check
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == initial_count + 1
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == initial_count
        assert email not in response.json()[activity]["participants"]
    
    def test_capacity_management(self, client):
        """Test that capacity is properly managed during signup and unregister"""
        activity = "Debate Team"
        
        # Get initial info
        response = client.get("/activities")
        initial_participants = len(response.json()[activity]["participants"])
        max_participants = response.json()[activity]["max_participants"]
        spots_available = max_participants - initial_participants
        
        # Fill up remaining spots
        emails = []
        for i in range(spots_available):
            email = f"capacity_test{i}@mergington.edu"
            emails.append(email)
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify activity is full
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == max_participants
        
        # Try to add one more (should fail)
        response = client.post(
            "/activities/Debate Team/signup?email=extra@mergington.edu"
        )
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()
        
        # Unregister one participant
        response = client.delete(
            f"/activities/{activity}/unregister?email={emails[0]}"
        )
        assert response.status_code == 200
        
        # Now signup should work again
        response = client.post(
            "/activities/Debate Team/signup?email=extra@mergington.edu"
        )
        assert response.status_code == 200
