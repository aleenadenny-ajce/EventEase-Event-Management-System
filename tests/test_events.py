"""Unit and integration tests for Event Management, CRUD, and Discovery."""

from datetime import date, timedelta


def test_browse_events(client):
    """Test public event browsing page."""
    response = client.get("/events")
    assert response.status_code == 200
    assert b"Cloud Computing Workshop" in response.data


def test_search_and_filter_events(client):
    """Test searching events by query parameter and category."""
    # Search by keyword
    response = client.get("/events?q=Kubernetes")
    assert response.status_code == 200
    assert b"Cloud Computing Workshop" in response.data
    assert b"Past AI Seminar" not in response.data

    # Filter by category
    response = client.get("/events?category=Workshop")
    assert response.status_code == 200
    assert b"Past AI Seminar" in response.data
    assert b"Cloud Computing Workshop" not in response.data


def test_event_detail_page(client):
    """Test event details view for existing and nonexistent events."""
    # Existing event (ID 1)
    response = client.get("/events/1")
    assert response.status_code == 200
    assert b"Cloud Computing Workshop" in response.data

    # Nonexistent event
    response = client.get("/events/9999")
    assert response.status_code == 404


def test_create_event_authorized(client, auth):
    """Test event creation by authenticated organizer."""
    auth.login_organizer()

    future_date = (date.today() + timedelta(days=20)).isoformat()
    deadline = (date.today() + timedelta(days=18)).isoformat()

    response = client.post("/events/create", data={
        "title": "National Hackathon 2026",
        "description": "Annual 24h coding marathon for cloud enthusiasts",
        "category": "Technical",
        "date": future_date,
        "start_time": "09:00",
        "end_time": "18:00",
        "venue": "Innovation Hub, Block B",
        "capacity": 75,
        "registration_deadline": deadline,
        "status": "Upcoming"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"National Hackathon 2026" in response.data
    assert b"created successfully" in response.data


def test_create_event_unauthorized_for_participant(client, auth):
    """Test that participant cannot create an event."""
    auth.login(email="participant@test.local", password="User@Password123")

    response = client.get("/events/create")
    assert response.status_code == 403


def test_edit_event(client, auth):
    """Test updating existing event attributes."""
    auth.login_organizer()

    future_date = (date.today() + timedelta(days=10)).isoformat()
    deadline = (date.today() + timedelta(days=8)).isoformat()

    response = client.post("/events/1/edit", data={
        "title": "Cloud Computing Workshop — Updated Edition",
        "description": "Updated deep dive into Kubernetes pods and services",
        "category": "Technical",
        "date": future_date,
        "start_time": "10:00",
        "end_time": "17:00",
        "venue": "Lab 1 & Zoom",
        "capacity": 80,
        "registration_deadline": deadline,
        "status": "Upcoming"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Event updated successfully" in response.data
    assert b"Updated Edition" in response.data


def test_delete_event(client, auth):
    """Test deleting an event."""
    auth.login_organizer()

    response = client.post("/events/2/delete", follow_redirects=True)
    assert response.status_code == 200
    assert b"deleted successfully" in response.data

    # Verify event no longer accessible
    detail_res = client.get("/events/2")
    assert detail_res.status_code == 404


def test_manage_events_access(client, auth):
    """Test organizer accessing manage_events table and filtering."""
    auth.login_organizer()
    response = client.get("/events/manage")
    assert response.status_code == 200
    assert b"Manage Campus Events" in response.data
    assert b"Cloud Computing Workshop" in response.data

    # Test filtering in manage_events
    filter_res = client.get("/events/manage?category=Technical")
    assert filter_res.status_code == 200
    assert b"Cloud Computing Workshop" in filter_res.data

