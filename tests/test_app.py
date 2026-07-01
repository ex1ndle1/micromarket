from unittest.mock import MagicMock, AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError


class TestProductAPI:
    async def test_create_product_success(self, app_client: AsyncClient):
        payload = {"title": "test product", "price": 99.99}
        response = await app_client.post("/market/product", json=payload)
        assert response.status_code == 201
        assert response.json() == ["created"]

    async def test_create_product_invalid_title(self, app_client: AsyncClient):
        payload = {"title": "", "price": 99.99}
        response = await app_client.post("/market/product", json=payload)
        assert response.status_code == 422

    async def test_create_product_invalid_price_negative(self, app_client: AsyncClient):
        payload = {"title": "test", "price": -1}
        response = await app_client.post("/market/product", json=payload)
        assert response.status_code == 422

    async def test_create_product_invalid_price_zero(self, app_client: AsyncClient):
        payload = {"title": "test", "price": 0}
        response = await app_client.post("/market/product", json=payload)
        assert response.status_code == 422

    async def test_create_product_missing_title(self, app_client: AsyncClient):
        payload = {"price": 50.0}
        response = await app_client.post("/market/product", json=payload)
        assert response.status_code == 422
    
    async def test_create_product_missing_price(self, app_client: AsyncClient):
        payload = {"title": "test"}
        response = await app_client.post("/market/product", json=payload)
        assert response.status_code == 422

    async def test_get_product_not_found(self, app_client: AsyncClient):
        response = await app_client.get("/market/product", params={"id": 999})
        assert response.status_code == 404

    async def test_create_product_integrity_error(self, app_client: AsyncClient):
        for val in app_client._transport.app.dependency_overrides.values():
            session = val()
            session.commit = AsyncMock(side_effect=IntegrityError("mock", "mock", "mock"))
            break
                  
        payload = {"title": "dupe", "price": 10.0}
        response = await app_client.post("/market/product", json=payload)
        assert response.status_code == 409
        assert "conflict" in response.text.lower()

    async def test_get_product_invalid_id(self, app_client: AsyncClient):
        response = await app_client.get("/market/product", params={"id": "abc"})
        assert response.status_code == 422

    async def test_get_product_missing_id(self, app_client: AsyncClient):
        response = await app_client.get("/market/product")
        assert response.status_code == 422
