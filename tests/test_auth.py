import pytest
from fastapi import status


def test_signup_success(client, test_user_data):
    """Test successful user signup."""
    response = client.post("/api/v1/auth/signup", json=test_user_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    assert "user" in data
    assert "tokens" in data
    assert data["user"]["email"] == test_user_data["email"]
    assert data["user"]["name"] == test_user_data["name"]
    assert "access_token" in data["tokens"]
    assert "refresh_token" in data["tokens"]


def test_signup_duplicate_email(client, test_user_data):
    """Test signup with duplicate email."""
    # First signup
    client.post("/api/v1/auth/signup", json=test_user_data)
    
    # Try to signup again with same email
    response = client.post("/api/v1/auth/signup", json=test_user_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"].lower()


def test_login_success(client, test_user_data):
    """Test successful user login."""
    # First signup
    client.post("/api/v1/auth/signup", json=test_user_data)
    
    # Then login
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"],
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "user" in data
    assert "tokens" in data
    assert data["user"]["email"] == test_user_data["email"]


def test_login_wrong_password(client, test_user_data):
    """Test login with wrong password."""
    # First signup
    client.post("/api/v1/auth/signup", json=test_user_data)
    
    # Try login with wrong password
    login_data = {
        "email": test_user_data["email"],
        "password": "wrongpassword",
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    """Test login with non-existent user."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "somepassword",
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(client, test_user_data):
    """Test getting current user info."""
    # Signup and get token
    signup_response = client.post("/api/v1/auth/signup", json=test_user_data)
    token = signup_response.json()["tokens"]["access_token"]
    
    # Get current user
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["email"] == test_user_data["email"]
    assert data["name"] == test_user_data["name"]


def test_get_current_user_no_token(client):
    """Test getting current user without token."""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_token(client, test_user_data):
    """Test refreshing access token."""
    # Signup and get tokens
    signup_response = client.post("/api/v1/auth/signup", json=test_user_data)
    refresh_token = signup_response.json()["tokens"]["refresh_token"]
    
    # Refresh token
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "access_token" in data
    assert "refresh_token" in data


def test_logout(client, test_user_data):
    """Test logout endpoint."""
    # Signup and get token
    signup_response = client.post("/api/v1/auth/signup", json=test_user_data)
    token = signup_response.json()["tokens"]["access_token"]
    
    # Logout
    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()
