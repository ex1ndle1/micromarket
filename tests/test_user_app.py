from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError


class TestUserAPI:
    async def test_register_user_success(self, user_client: AsyncClient):
        payload = {"username": "john_doe", "card_number": 1234567890123456}
        response = await user_client.post("/user/register", json=payload)
        assert response.status_code == 200
        assert response.json() == ["created"]

    async def test_register_user_short_username(self, user_client: AsyncClient):
        payload = {"username": "a", "card_number": 1234567890123456}
        response = await user_client.post("/user/register", json=payload)
        assert response.status_code == 422

    async def test_register_user_invalid_card_length(self, user_client: AsyncClient):
        payload = {"username": "jane", "card_number": 123}
        response = await user_client.post("/user/register", json=payload)
        assert response.status_code == 422

    async def test_register_user_missing_username(self, user_client: AsyncClient):
        payload = {"card_number": 1234567890123456}
        response = await user_client.post("/user/register", json=payload)
        assert response.status_code == 422

    async def test_register_user_missing_card(self, user_client: AsyncClient):
        payload = {"username": "jane"}
        response = await user_client.post("/user/register", json=payload)
        assert response.status_code == 422

    async def test_register_user_card_too_small(self, user_client: AsyncClient):
        payload = {"username": "jane", "card_number": 1}
        response = await user_client.post("/user/register", json=payload)
        assert response.status_code == 422

    async def test_register_user_card_too_large(self, user_client: AsyncClient):
        payload = {"username": "jane", "card_number": 99999999999999999}
        response = await user_client.post("/user/register", json=payload)
        assert response.status_code == 422

    async def test_register_duplicate(self, user_client: AsyncClient):
        for val in user_client._transport.app.dependency_overrides.values():
            session = val()
            session.commit = AsyncMock(side_effect=IntegrityError("mock", "mock", "mock"))
            break

        payload = {"username": "dup_user", "card_number": 1111222233334444}
        response = await user_client.post("/user/register", json=payload)
        assert response.status_code == 409
