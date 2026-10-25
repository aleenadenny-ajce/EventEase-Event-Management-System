"""Pytest fixtures and test database setup for EventEase."""

import os
import tempfile
import sqlite3
from pathlib import Path
from datetime import date, timedelta
import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from config import TestConfig


@pytest.fixture
def app():
    """Create and configure a new app instance for each test with an isolated SQLite database."""
    # Create a unique temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    class CustomTestConfig(TestConfig):
        DATABASE = Path(db_path)
        TESTING = True
        WTF_CSRF_ENABLED = False
        SECRET_KEY = "test-secret-key"

    # Initialize schema
    schema_path = Path(__file__).resolve().parent.parent / "database" / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(schema_sql)

    # Seed baseline testing accounts
    cursor = conn.cursor()
    admin_pw = generate_password_hash("Admin@Password123")
    org_pw = generate_password_hash("Organizer@Password123")
    part_pw = generate_password_hash("User@Password123")

    cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                   ("Test Admin", "admin@test.local", admin_pw, "admin"))
    cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                   ("Test Organizer", "organizer@test.local", org_pw, "organizer"))
    cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                   ("Test Participant", "participant@test.local", part_pw, "participant"))
    cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                   ("Second Participant", "participant2@test.local", part_pw, "participant"))

    # Seed Categories
    cursor.execute("INSERT INTO categories (name, description) VALUES ('Technical', 'Tech events')")
    cursor.execute("INSERT INTO categories (name, description) VALUES ('Workshop', 'Hands-on workshops')")

    # Seed a standard open test event (capacity 2, deadline 10 days in future)
    future_date = (date.today() + timedelta(days=10)).isoformat()
    future_deadline = (date.today() + timedelta(days=9)).isoformat()
    past_date = (date.today() - timedelta(days=10)).isoformat()
    past_deadline = (date.today() - timedelta(days=5)).isoformat()

    # Event 1: Open upcoming event with capacity 2
    cursor.execute("""
        INSERT INTO events (title, description, category, date, start_time, end_time, venue, capacity, registration_deadline, status, organizer_id)
        VALUES ('Cloud Computing Workshop', 'Learn Kubernetes and Docker', 'Technical', ?, '10:00', '16:00', 'Lab 1', 2, ?, 'Upcoming', 2)
    """, (future_date, future_deadline))

    # Event 2: Expired deadline event
    cursor.execute("""
        INSERT INTO events (title, description, category, date, start_time, end_time, venue, capacity, registration_deadline, status, organizer_id)
        VALUES ('Past AI Seminar', 'Past event overview', 'Workshop', ?, '11:00', '13:00', 'Seminar Hall', 50, ?, 'Upcoming', 2)
    """, (future_date, past_deadline))

    # Event 3: Full capacity event (capacity 1, 1 confirmed registration already)
    cursor.execute("""
        INSERT INTO events (title, description, category, date, start_time, end_time, venue, capacity, registration_deadline, status, organizer_id)
        VALUES ('Exclusive Masterclass', 'Single seat masterclass', 'Technical', ?, '14:00', '16:00', 'Room 101', 1, ?, 'Upcoming', 2)
    """, (future_date, future_deadline))

    # Register participant2 in Event 3 to fill it to capacity
    cursor.execute("""
        INSERT INTO registrations (registration_code, user_id, event_id, status)
        VALUES ('EVT-TEST-FULL-01', 4, 3, 'Confirmed')
    """)

    conn.commit()
    conn.close()

    app_instance = create_app(CustomTestConfig)

    yield app_instance

    # Cleanup temporary test database
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass


@pytest.fixture
def client(app):
    """A test client for sending HTTP requests to the application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the application's Click commands."""
    return app.test_cli_runner()


class AuthActions:
    """Helper class to authenticate test requests."""
    def __init__(self, client):
        self._client = client

    def login(self, email="participant@test.local", password="User@Password123"):
        return self._client.post(
            "/auth/login",
            data={"email": email, "password": password},
            follow_redirects=True
        )

    def login_admin(self):
        return self.login(email="admin@test.local", password="Admin@Password123")

    def login_organizer(self):
        return self.login(email="organizer@test.local", password="Organizer@Password123")

    def logout(self):
        return self._client.get("/auth/logout", follow_redirects=True)


@pytest.fixture
def auth(client):
    return AuthActions(client)
