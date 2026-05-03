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
    """Fixture para limpar o banco de dados em memória"""
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
    """Fixture para criar um token de autenticação"""
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
    """Fixture para cabeçalhos de autenticação"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.mark.asyncio
class TestProperties:
    """Testes para o router de propriedades"""
    
    async def test_create_property(self, auth_headers, mock_db):
        """Testa criação de propriedade"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/properties",
                headers=auth_headers,
                json={
                    "title": "Apartamento Luxo",
                    "description": "Apartamento de luxo no centro",
                    "property_type": "apartamento",
                    "value": 500000.00,
                    "address": "Rua Principal, 100",
                    "city": "São Paulo",
                    "state": "SP",
                    "bedrooms": 2,
                    "bathrooms": 2,
                    "area": 80.0,
                    "garage_spaces": 1,
                    "status": "disponível"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Apartamento Luxo"
        assert data["value"] == 500000.00
        assert "id" in data
    
    async def test_list_properties(self, auth_headers, mock_db):
        """Testa listagem de propriedades"""
        db = mock_db
        user_id = "test-user-1"
        
        # Create test properties
        db["properties"]["prop-1"] = {
            "id": "prop-1",
            "user_id": user_id,
            "title": "Casa 1",
            "description": "Casa com piscina",
            "property_type": "casa",
            "value": 300000.00,
            "address": "Rua 1",
            "city": "São Paulo",
            "state": "SP",
            "bedrooms": 3,
            "bathrooms": 2,
            "area": 150.0,
            "garage_spaces": 2,
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
            response = await client.get("/properties", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    async def test_get_property(self, auth_headers, mock_db):
        """Testa obtenção de propriedade específica"""
        db = mock_db
        user_id = "test-user-1"
        
        # Create test property
        db["properties"]["prop-test"] = {
            "id": "prop-test",
            "user_id": user_id,
            "title": "Apartamento Teste",
            "description": "Descrição teste",
            "property_type": "apartamento",
            "value": 200000.00,
            "address": "Rua Teste, 50",
            "city": "Rio de Janeiro",
            "state": "RJ",
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
            response = await client.get("/properties/prop-test", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Apartamento Teste"
    
    async def test_get_property_not_found(self, auth_headers, mock_db):
        """Testa obtenção de propriedade inexistente"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/properties/nonexistent", headers=auth_headers)
        
        assert response.status_code == 404
    
    async def test_update_property(self, auth_headers, mock_db):
        """Testa atualização de propriedade"""
        db = mock_db
        user_id = "test-user-1"
        
        # Create test property
        db["properties"]["prop-update"] = {
            "id": "prop-update",
            "user_id": user_id,
            "title": "Título Antigo",
            "description": "Descrição antiga",
            "property_type": "apartamento",
            "value": 100000.00,
            "address": "Rua Antiga",
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
            response = await client.put(
                "/properties/prop-update",
                headers=auth_headers,
                json={
                    "title": "Novo Título",
                    "value": 150000.00
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Novo Título"
        assert data["value"] == 150000.00
    
    async def test_delete_property(self, auth_headers, mock_db):
        """Testa exclusão de propriedade"""
        db = mock_db
        user_id = "test-user-1"
        
        # Create test property
        db["properties"]["prop-delete"] = {
            "id": "prop-delete",
            "user_id": user_id,
            "title": "Propriedade para deletar",
            "description": "Descrição",
            "property_type": "casa",
            "value": 100000.00,
            "address": "Rua",
            "city": "Cidade",
            "state": "ST",
            "bedrooms": 2,
            "bathrooms": 1,
            "area": 100.0,
            "garage_spaces": 1,
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
            response = await client.delete("/properties/prop-delete", headers=auth_headers)
        
        assert response.status_code == 200
        assert "deletado com sucesso" in response.json()["message"]
        
        # Verify deletion
        assert "prop-delete" not in db["properties"]
    
    async def test_filter_by_property_type(self, auth_headers, mock_db):
        """Testa filtro por tipo de propriedade"""
        db = mock_db
        user_id = "test-user-1"
        
        # Create properties with different types
        db["properties"]["prop-apt"] = {
            "id": "prop-apt",
            "user_id": user_id,
            "title": "Apartamento",
            "description": "Desc",
            "property_type": "apartamento",
            "value": 100000.00,
            "address": "Rua 1",
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
        
        db["properties"]["prop-house"] = {
            "id": "prop-house",
            "user_id": user_id,
            "title": "Casa",
            "description": "Desc",
            "property_type": "casa",
            "value": 200000.00,
            "address": "Rua 2",
            "city": "São Paulo",
            "state": "SP",
            "bedrooms": 3,
            "bathrooms": 2,
            "area": 150.0,
            "garage_spaces": 1,
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
            response = await client.get("/properties?property_type=apartamento", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert all(p["property_type"] == "apartamento" for p in data)
