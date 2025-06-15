from fastapi import status


async def test_get_current_user(async_client):
    await async_client.post("/register", params={
        "user_email": "a@b.com",
        "password": "pass123",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
    })

    response = await async_client.post("/login", data={"username": "a@b.com", "password": "pass123"})
    token = response.json()["access_token"]

    async_client.cookies.set("access_token", token)

    response = await async_client.get("/users/me")
    assert response.status_code == status.HTTP_200_OK
    user = response.json()
    assert user["email"] == "a@b.com"
