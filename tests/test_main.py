"""Tests for the main FastAPI application."""

from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest


@pytest.mark.unit
def test_root_endpoint(client: TestClient) -> None:
    """Test the root endpoint returns expected response."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Project Thalassa API is running"}


@pytest.mark.unit
def test_health_check_endpoint(client: TestClient) -> None:
    """Test the health check endpoint returns expected response."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "thalassa-api"
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_root_endpoint_async(async_client: AsyncClient) -> None:
    """Test the root endpoint returns expected response using async client."""
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Project Thalassa API is running"}


@pytest.mark.asyncio
@pytest.mark.unit
async def test_health_check_endpoint_async(async_client: AsyncClient) -> None:
    """Test the health check endpoint returns expected response using async client."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "thalassa-api"
    assert data["version"] == "0.1.0"
