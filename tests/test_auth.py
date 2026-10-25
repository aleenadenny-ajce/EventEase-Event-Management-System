"""Unit and integration tests for Authentication and Role-Based Access Control."""

def test_register_success(client):
    """Test successful registration of a new participant."""
    response = client.post("/auth/register", data={
        "name": "New Student",
        "email": "newstudent@test.local",
        "password": "SecretPassword123",
        "confirm_password": "SecretPassword123"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Registration successful" in response.data


def test_register_duplicate_email(client):
    """Test that registering an existing email fails."""
    response = client.post("/auth/register", data={
        "name": "Duplicate Student",
        "email": "participant@test.local",  # Already in seeded db
        "password": "Password123",
        "confirm_password": "Password123"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"already exists" in response.data


def test_register_password_mismatch(client):
    """Test rejection when password and confirm_password do not match."""
    response = client.post("/auth/register", data={
        "name": "Mismatch Student",
        "email": "mismatch@test.local",
        "password": "Password123",
        "confirm_password": "DifferentPassword123"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Passwords do not match" in response.data


def test_login_success(auth):
    """Test successful login with valid credentials."""
    response = auth.login(email="participant@test.local", password="User@Password123")
    assert response.status_code == 200
    assert b"Welcome back, Test Participant" in response.data


def test_login_invalid_password(auth):
    """Test login rejection with incorrect password."""
    response = auth.login(email="participant@test.local", password="WrongPassword999")
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_logout(auth):
    """Test logout clears the session state."""
    auth.login()
    response = auth.logout()
    assert response.status_code == 200
    assert b"logged out" in response.data


def test_role_access_control(client, auth):
    """Test that unauthorized roles cannot access administrative endpoints."""
    # 1. Unauthenticated user redirected to login
    response = client.get("/admin/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]

    # 2. Participant role gets 403 Forbidden on admin dashboard
    auth.login(email="participant@test.local", password="User@Password123")
    response = client.get("/admin/dashboard")
    assert response.status_code == 403

    # 3. Participant role gets 403 Forbidden on user management
    response = client.get("/admin/users")
    assert response.status_code == 403

    # 4. Admin role has full access
    auth.logout()
    auth.login_admin()
    response = client.get("/admin/dashboard")
    assert response.status_code == 200
    assert b"System Administration" in response.data
