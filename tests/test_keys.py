import pytest
from fastapi import status


def test_create_api_key_success(client, test_user_data, test_api_key_data):
    """Test successful API key creation."""
    # Signup and get token
    signup_response = client.post("/api/v1/auth/signup", json=test_user_data)
    token = signup_response.json()["tokens"]["access_token"]
    
    # Create API key
    response = client.post(
        "/api/v1/keys/create",
        json=test_api_key_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    assert "api_key" in data
    assert data["service_name"] == test_api_key_data["service_name"]
    assert data["permissions"] == test_api_key_data["permissions"]
    assert data["is_active"] is True


def test_create_api_key_no_auth(client, test_api_key_data):
    """Test API key creation without authentication."""
    response = client.post("/api/v1/keys/create", json=test_api_key_data)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_api_keys(client, test_user_data, test_api_key_data):
    """Test listing user's API keys."""
    # Signup and get token
    signup_response = client.post("/api/v1/auth/signup", json=test_user_data)
    token = signup_response.json()["tokens"]["access_token"]
    
    # Create API key
    client.post(
        "/api/v1/keys/create",
        json=test_api_key_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # List API keys
    response = client.get(
        "/api/v1/keys/list",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["service_name"] == test_api_key_data["service_name"]


def test_get_api_key(client, test_user_data, test_api_key_data):
    """Test getting specific API key details."""
    # Signup and get token
    signup_response = client.post("/api/v1/auth/signup", json=test_user_data)
    token = signup_response.json()["tokens"]["access_token"]
    
    # Create API key
    create_response = client.post(
        "/api/v1/keys/create",
        json=test_api_key_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    key_id = create_response.json()["id"]
    
    # Get API key details
    response = client.get(
        f"/api/v1/keys/{key_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["id"] == key_id
    assert data["service_name"] == test_api_key_data["service_name"]


def test_revoke_api_key(client, test_user_data, test_api_key_data):
    """Test revoking an API key."""
    # Signup and get token
    signup_response = client.post("/api/v1/auth/signup", json=test_user_data)
    token = signup_response.json()["tokens"]["access_token"]
    
    # Create API key
    create_response = client.post(
        "/api/v1/keys/create",
        json=test_api_key_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    key_id = create_response.json()["id"]
    
    # Revoke API key
    response = client.patch(
        f"/api/v1/keys/{key_id}/revoke",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["is_active"] is False


def test_renew_api_key(client, test_user_data, test_api_key_data):
    """Test renewing an API key."""
    # Signup and get token
    signup_response = client.post("/api/v1/auth/signup", json=test_user_data)
    token = signup_response.json()["tokens"]["access_token"]
    
    # Create API key
    create_response = client.post(
        "/api/v1/keys/create",
        json=test_api_key_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    key_id = create_response.json()["id"]
    original_expiry = create_response.json()["expires_at"]
    
    # Renew API key
    response = client.patch(
        f"/api/v1/keys/{key_id}/renew",
        json={"expires_in_days": 120},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # New expiration should be different
    assert data["expires_at"] != original_expiry


def test_delete_api_key(client, test_user_data, test_api_key_data):
    """Test deleting an API key."""
    # Signup and get token
    signup_response = client.post("/api/v1/auth/signup", json=test_user_data)
    token = signup_response.json()["tokens"]["access_token"]
    
    # Create API key
    create_response = client.post(
        "/api/v1/keys/create",
        json=test_api_key_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    key_id = create_response.json()["id"]
    
    # Delete API key
    response = client.delete(
        f"/api/v1/keys/{key_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's deleted
    get_response = client.get(
        f"/api/v1/keys/{key_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_verify_api_key(client, test_user_data, test_api_key_data):
    """Test API key verification endpoint."""
    # Signup and get token
    signup_response = client.post("/api/v1/auth/signup", json=test_user_data)
    token = signup_response.json()["tokens"]["access_token"]
    
    # Create API key
    create_response = client.post(
        "/api/v1/keys/create",
        json=test_api_key_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    api_key = create_response.json()["api_key"]
    
    # Verify API key
    response = client.get(
        "/api/v1/keys/verify/test",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["service_name"] == test_api_key_data["service_name"]
    assert data["permissions"] == test_api_key_data["permissions"]


def test_api_key_access_other_user_key(client, test_user_data, test_api_key_data):
    """Test that users cannot access other users' API keys."""
    # Create first user and API key
    signup_response1 = client.post("/api/v1/auth/signup", json=test_user_data)
    token1 = signup_response1.json()["tokens"]["access_token"]
    
    create_response = client.post(
        "/api/v1/keys/create",
        json=test_api_key_data,
        headers={"Authorization": f"Bearer {token1}"}
    )
    key_id = create_response.json()["id"]
    
    # Create second user
    test_user_data2 = {
        "email": "user2@example.com",
        "name": "User Two",
        "password": "password123",
    }
    signup_response2 = client.post("/api/v1/auth/signup", json=test_user_data2)
    token2 = signup_response2.json()["tokens"]["access_token"]
    
    # Try to access first user's API key with second user's token
    response = client.get(
        f"/api/v1/keys/{key_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
