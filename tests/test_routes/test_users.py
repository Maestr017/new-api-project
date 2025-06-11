import pytest
from fastapi import status
from httpx import AsyncClient, ASGITransport

from src.models.models import UserOrm
from src.schemas.users import UserCreate
from main import app


@pytest.mark.asyncio
class TestUserAPI:

    async def test_register_user(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            response = await client.post(
                "/register",
                json={"email": "newuser@example.com", "password": "newpassword123"}
            )
        assert response.status_code == status.HTTP_201_CREATED or response.status_code == status.HTTP_200_OK

    async def test_login_user(self, async_client: AsyncClient, created_user: UserOrm, test_user_data: UserCreate):
        response = await async_client.post(
            "/auth/login",
            data={"username": test_user_data.email, "password": test_user_data.password}
        )
        assert response.status_code == status.HTTP_200_OK
        json_data = response.json()
        assert "access_token" in json_data
        assert json_data["token_type"] == "bearer"

    async def test_get_current_user(self, async_client: AsyncClient, created_user: UserOrm, access_token: str):
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await async_client.get("/users/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == created_user.email
