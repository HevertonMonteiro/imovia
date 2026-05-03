import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import get_memory_db
from auth_utils import create_access_token, get_password_hash


@pytest.fixture
def mock_db():
    db = get_memory_db()
    db["users"].clear()
    db["properties"].clear()
    db["clients"].clear()
    db["leads"].clear()
    yield db
    db["users"].clear()
    db["properties"].clear()
    db["clients"].clear()
    db["leads"].clear()


@pytest.fixture
def auth_token(mock_db):
    db = mock_db
    user_id = "test-user-1"
    db["users"][user_id] = {
        "id": user_id,
        "email": "test@example.com",
        "name": "Test User",
        "password": get_password_hash("password123"),
        "created_at": str(datetime.now())
    }
    token = create_access_token(data={"sub": user_id, "email": "test@example.com"})
    return token


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.mark.asyncio
class TestLeads:
    """Testes para o router de leads"""
    
    async def test_create_lead(self, auth_headers, mock_db):
        """Testa criação de lead"""
        db = mock_db
        user_id = "test-user-1"
        
        # Create property first
        db["properties"]["prop-lead"] = {
            "id": "prop-lead",
            "user_id": user_id,
            "title": "Imóvel para Lead",
            "description": "Desc",
            "property_type": "apartamento",
            "value": 200000.00,
            "address": "Rua",
            "city": "São Paulo",
            "state": "SP",
            "bedrooms": 1,
            "bathrooms": 1,
            "area": 50.0,
            "garage_spaces": 0,
            "status": "disponível",
            "images": [],
            "ai_title": None,
            "ai_description": None,
            "ai_highlights": [],
            "image_analysis": None,
            "views": 0,
            "clicks": 0,
            "leads": 0,
            "created_at": str(datetime.now()),
            "updated_at": str(datetime.now())
        }
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/leads",
                headers=auth_headers,
                json={
                    "property_id": "prop-lead",
                    "client_name": "Carlos Oliveira",
                    "client_email": "carlos@example.com",
                    "client_phone": "+5511999999999",
                    "message": "Gostaria de agendar uma visita",
                    "source": "website"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["client_name"] == "Carlos Oliveira"
        assert data["property_id"] == "prop-lead"
        assert "id" in data
    
    async def test_list_leads(self, auth_headers, mock_db):
        """Testa listagem de leads"""
        db = mock_db
        user_id = "test-user-1"
        
        # Create test lead
        db["leads"]["lead-1"] = {
            "id": "lead-1",
            "user_id": user_id,
            "property_id": "prop-1",
            "client_name": "Lead 1",
            "client_email": "lead1@example.com",
            "client_phone": "+5511999999999",
            "message": "Teste",
            "source": "website",
            "created_at": str(datetime.now())
        }
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/leads", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    async def test_get_lead(self, auth_headers, mock_db):
        """Testa obtenção de lead específico"""
        db = mock_db
        user_id = "test-user-1"
        
        db["leads"]["lead-test"] = {
            "id": "lead-test",
            "user_id": user_id,
            "property_id": "prop-1",
            "client_name": "Lead Teste",
            "client_email": "teste@example.com",
            "client_phone": "+5511888888888",
            "message": "Mensagem teste",
            "source": "website",
            "created_at": str(datetime.now())
        }
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/leads/lead-test", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["client_name"] == "Lead Teste"
    
    async def test_delete_lead(self, auth_headers, mock_db):
        """Testa exclusão de lead"""
        db = mock_db
        user_id = "test-user-1"
        
        db["leads"]["lead-delete"] = {
            "id": "lead-delete",
            "user_id": user_id,
            "property_id": "prop-1",
            "client_name": "Lead Deletar",
            "client_email": "delete@example.com",
            "client_phone": "+5511777777777",
            "message": "Teste",
            "source": "website",
            "created_at": str(datetime.now())
        }
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete("/leads/lead-delete", headers=auth_headers)
        
        assert response.status_code == 200
        assert "deletado com sucesso" in response.json()["message"]
    
    async def test_filter_leads_by_property(self, auth_headers, mock_db):
        """Testa filtro de leads por propriedade"""
        db = mock_db
        user_id = "test-user-1"
        
        db["leads"]["lead-prop-1"] = {
            "id": "lead-prop-1",
            "user_id": user_id,
            "property_id": "prop-1",
            "client_name": "Cliente 1",
            "client_email": "cliente1@example.com",
            "client_phone": "+5511999999999",
            "message": "",
            "source": "website",
            "created_at": str(datetime.now())
        }
        
        db["leads"]["lead-prop-2"] = {
            "id": "lead-prop-2",
            "user_id": user_id,
            "property_id": "prop-2",
            "client_name": "Cliente 2",
            "client_email": "cliente2@example.com",
            "client_phone": "+5511888888888",
            "message": "",
            "source": "website",
            "created_at": str(datetime.now())
        }
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/leads?property_id=prop-1", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert all(l["property_id"] == "prop-1" for l in data)
