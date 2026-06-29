"""Test spend API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_get_spend_summary(client: AsyncClient) -> None:
    """Test spend summary endpoint."""
    response = await client.get("/me/spend/summary?period=month")
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "period" in data
    assert "currency" in data
    assert "spend" in data
    assert "budget" in data
    assert "remaining" in data
    assert "budget_used_percent" in data


@pytest.mark.asyncio
async def test_get_spend_by_model(client: AsyncClient) -> None:
    """Test spend by model endpoint."""
    response = await client.get("/me/spend/by-model?period=month")
    assert response.status_code == 200
    data = response.json()
    assert "period" in data
    assert "currency" in data
    assert "models" in data
    assert isinstance(data["models"], list)


@pytest.mark.asyncio
async def test_get_spend_by_project(client: AsyncClient) -> None:
    """Test spend by project endpoint."""
    response = await client.get("/me/spend/by-project?period=month")
    assert response.status_code == 200
    data = response.json()
    assert "period" in data
    assert "currency" in data
    assert "projects" in data
    assert isinstance(data["projects"], list)


@pytest.mark.asyncio
async def test_get_spend_daily(client: AsyncClient) -> None:
    """Test daily spend endpoint."""
    response = await client.get("/me/spend/daily?period=month")
    assert response.status_code == 200
    data = response.json()
    assert "period" in data
    assert "currency" in data
    assert "days" in data
    assert isinstance(data["days"], list)


@pytest.mark.asyncio
async def test_get_budget(client: AsyncClient) -> None:
    """Test budget endpoint."""
    response = await client.get("/me/budget")
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "monthly_budget" in data
    assert "currency" in data
    assert "spent" in data
    assert "remaining" in data
    assert "used_percent" in data
    assert "state" in data
    assert "warning_threshold" in data
    assert "exceeded_threshold" in data
