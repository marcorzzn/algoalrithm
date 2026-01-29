import pytest

def test_register_user(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"

def test_login_user(client):
    # Registra prima
    client.post(
        "/api/auth/register",
        json={
            "email": "login@test.com",
            "password": "password123",
            "full_name": "Login User"
        }
    )
    
    # Login
    response = client.post(
        "/api/auth/login",
        data={
            "username": "login@test.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_current_user(client):
    # Registra
    reg_response = client.post(
        "/api/auth/register",
        json={
            "email": "current@test.com",
            "password": "password123",
            "full_name": "Current User"
        }
    )
    token = reg_response.json()["access_token"]
    
    # Get me
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "current@test.com"