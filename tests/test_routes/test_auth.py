from fastapi import status


async def test_register_and_login(async_client):
    register_data = {
        "user_email": "u@example.com",
        "password": "password123",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
    }
    response = await async_client.post("/register", params=register_data)
    assert response.status_code == 200

    login_data = {
        "username": register_data["user_email"],
        "password": register_data["password"],
    }
    response = await async_client.post("/login", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    json_resp = response.json()
    assert "access_token" in json_resp
    assert json_resp["token_type"] == "bearer"
