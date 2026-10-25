"""Unit and integration tests for Registration Engine, Concurrency, and Capacity Limits."""

def test_successful_registration(client, auth):
    """Test standard registration flow for open event."""
    auth.login(email="participant@test.local", password="User@Password123")

    response = client.post("/events/1/register", follow_redirects=True)
    assert response.status_code == 200
    assert b"Registration Confirmed" in response.data
    assert b"EVT-" in response.data


def test_duplicate_registration_prevention(client, auth):
    """Test that a user cannot register twice for the same event."""
    auth.login(email="participant@test.local", password="User@Password123")

    # First registration
    client.post("/events/1/register", follow_redirects=True)

    # Second registration attempt
    second_response = client.post("/events/1/register", follow_redirects=True)
    assert second_response.status_code == 200
    assert b"already registered" in second_response.data


def test_full_capacity_rejection(client, auth):
    """Test rejection when event capacity is exhausted."""
    # Event 3 has capacity 1, and participant2 is already registered
    auth.login(email="participant@test.local", password="User@Password123")

    response = client.post("/events/3/register", follow_redirects=True)
    assert response.status_code == 200
    assert b"full capacity" in response.data


def test_expired_deadline_rejection(client, auth):
    """Test registration rejection when deadline has expired."""
    # Event 2 has past registration deadline
    auth.login(email="participant@test.local", password="User@Password123")

    response = client.post("/events/2/register", follow_redirects=True)
    assert response.status_code == 200
    assert b"deadline for this event has passed" in response.data


def test_cancel_registration(client, auth):
    """Test cancelling an existing registration."""
    auth.login(email="participant@test.local", password="User@Password123")

    # Register first
    client.post("/events/1/register", follow_redirects=True)

    # Cancel registration (Participant 1 registration id 2)
    response = client.post("/registrations/2/cancel", follow_redirects=True)
    assert response.status_code == 200
    assert b"Registration has been cancelled" in response.data


def test_csv_export_roster(client, auth):
    """Test attendee roster CSV export for organizer."""
    auth.login_organizer()

    response = client.get("/events/3/export-csv")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/csv")
    assert b"Registration Code,Participant Name,Email Address,Status,Registered At" in response.data
    assert b"participant2@test.local" in response.data
