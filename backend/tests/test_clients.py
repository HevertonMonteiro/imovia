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
class TestClients:
    """Testes para o router de clientes"""
    
    async def test_create_client(self, auth_headers, mock_db):
        """Testa criação de cliente"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/clients",
                headers=auth_headers,
                json={
                    "name": "João Silva",
                    "email": "joao@example.com",
                    "phone": "+5511999999999",
                    "interest": "Apartamento",
                    "notes": "Interessado em imóvel no centro"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "João Silva"
        assert data["email"] == "joao@example.com"
        assert "id" in data
    
    async def test_list_clients(self, auth_headers, mock_db):
        """Testa listagem de clientes"""
        db = mock_db
        user_id = "test-user-1"
        
        # Create test clients
        db["clients"]["client-1"] = {
            "id": "client-1",
            "user_id": user_id,
            "name": "Cliente 1",
            "email": "cliente1@example.com",
            "phone": "+5511999999999",
            "interest": "Casa",
            "notes": "",
            "created_at": str(datetime.now())
        }
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/clients", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    async def test_get_client(self, auth_headers, mock_db):
        """Testa obtenção de cliente específico"""
        db = mock_db
        user_id = "test-user-1"
        
        db["clients"]["client-test"] = {
            "id": "client-test",
            "user_id": user_id,
            "name": "Cliente Teste",
            "email": "teste@example.com",
            "phone": "+5511888888888",
            "interest": "Terreno",
            "notes": "Teste",
            "created_at": str(datetime.now())
        }
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/clients/client-test", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Cliente Teste"
    
    async def test_update_client(self, auth_headers, mock_db):
        """Testa atualização de cliente"""
        db = mock_db
        user_id = "test-user-1"
        
        db["clients"]["client-update"] = {
            "id": "client-update",
            "user_id": user_id,
            "name": "Nome Antigo",
            "email": "antigo@example.com",
            "phone": "+5511777777777",
            "interest": "Apartamento",
            "notes": "Notas antigas",
            "created_at": str(datetime.now())
        }
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.put(
                "/clients/client-update",
                headers=auth_headers,
                json={
                    "name": "Nome Novo",
                    "email": "novo@example.com",
                    "phone": "+5511666666666",
                    "interest": "Casa",
                    "notes": "Notas novas"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Nome Novo"
    
    async def test_delete_client(self, auth_headers, mock_db):
        """Testa exclusão de cliente"""
        db = mock_db
        user_id = "test-user-1"
        
        db["clients"]["client-delete"] = {
            "id": "client-delete",
            "user_id": user_id,
            "name": "Cliente Deletar",
            "email": "delete@example.com",
            "phone": "+5511555555555",
            "interest": "Loja",
            "notes": "",
            "created_at": str(datetime.now())
        }
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete("/clients/client-delete", headers=auth_headers)
        
        assert response.status_code == 200
        assert "deletado com sucesso" in response.json()["message"]
    
    async def test_search_clients(self, auth_headers, mock_db):
        """Testa busca de clientes"""
        db = mock_db
        user_id = "test-user-1"
        
        db["clients"]["client-search"] = {
            "id": "client-search",
            "user_id": user_id,
            "name": "Maria Santos",
            "email": "maria@example.com",
            "phone": "+5511444444444",
            "interest": "Apartamento",
            "notes": "",
            "created_at": str(datetime.now())
        }
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/clients?search=maria", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert any("maria" in c["name"].lower() for c in data)
