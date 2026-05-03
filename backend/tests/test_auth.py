import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import get_memory_db
from auth_utils import create_access_token


@pytest.fixture
def mock_db():
    """Fixture para limpar o banco de dados em memória"""
    db = get_memory_db()
    db["users"].clear()
    db["properties"].clear()
    db["clients"].clear()
    db["leads"].clear()
    yield db
    # Cleanup after test
    db["users"].clear()
    db["properties"].clear()
    db["clients"].clear()
    db["leads"].clear()


@pytest.fixture
def auth_token(mock_db):
    """Fixture para criar um token de autenticação"""
    # Create a test user
    db = mock_db
    user_id = "test-user-1"
    db["users"][user_id] = {
        "id": user_id,
        "email": "test@example.com",
        "name": "Test User",
        "password": "$2b$12$test_hash",
        "created_at": str(datetime.now())
    }
    
    # Create token
    token = create_access_token(data={"sub": user_id, "email": "test@example.com"})
    return token


@pytest.fixture
def auth_headers(auth_token):
    """Fixture para cabeçalhos de autenticação"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.mark.asyncio
class TestAuth:
    """Testes para o router de autenticação"""
    
    async def test_register_success(self, mock_db):
        """Testa registro de usuário com sucesso"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/auth/register",
                json={
                    "email": "newuser@example.com",
                    "name": "New User",
                    "password": "password123"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["name"] == "New User"
    
    async def test_register_duplicate_email(self, mock_db):
        """Testa registro com email duplicado"""
        # Create existing user
        db = mock_db
        db["users"]["existing-user"] = {
            "id": "existing-user",
            "email": "existing@example.com",
            "name": "Existing User",
            "password": "$2b$12$test_hash",
            "created_at": str(datetime.now())
        }
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/auth/register",
                json={
                    "email": "existing@example.com",
                    "name": "Another User",
                    "password": "password123"
                }
            )
        
        assert response.status_code == 400
        assert "Email já cadastrado" in response.json()["detail"]
    
    async def test_login_success(self, mock_db):
        """Testa login com sucesso"""
        # Create user with hashed password
        db = mock_db
        from auth_utils import get_password_hash
        db["users"]["login-user"] = {
            "id": "login-user",
            "email": "login@example.com",
            "name": "Login User",
            "password": get_password_hash("password123"),
            "created_at": str(datetime.now())
        }
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/auth/login?email=login@example.com&password=password123"
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "login@example.com"
    
    async def test_login_invalid_credentials(self, mock_db):
        """Testa login com credenciais inválidas"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/auth/login?email=nonexistent@example.com&password=wrongpassword"
            )
        
        assert response.status_code == 401
        assert "Email ou senha incorretos" in response.json()["detail"]
    
    async def test_get_me(self, auth_headers, mock_db):
        """Testa obtaining dados do usuário atual"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
    
    async def test_get_me_unauthorized(self):
        """Testa obtaining dados sem autenticação"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/auth/me")
        
        assert response.status_code == 401
