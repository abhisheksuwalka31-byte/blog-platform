def test_register_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword",
            "full_name": "New User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "newuser"
    assert data["user"]["email"] == "newuser@example.com"


def test_register_duplicate_username(client, test_users):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "alice",
            "email": "unique_email@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert "username already exists" in response.json()["detail"].lower()


def test_register_duplicate_email(client, test_users):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "unique_username",
            "email": "alice@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert "email already exists" in response.json()["detail"].lower()


def test_login_success(client, test_users):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username_or_email": "alice@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "alice"


def test_login_invalid_credentials(client, test_users):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username_or_email": "alice@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


def test_get_me_authenticated(client, alice_headers):
    response = client.get("/api/v1/auth/me", headers=alice_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "alice"


def test_get_me_unauthenticated(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
