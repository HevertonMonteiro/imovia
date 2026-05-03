from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from fastapi import Header, HTTPException
from config import settings
import uuid
from typing import Optional


def _normalize_role_for_jwt(role_value: Optional[str]) -> Optional[str]:
    if not role_value:
        return None

    normalized = role_value.upper()
    if normalized == "ADMIN":
        return "ADMIN_MASTER"
    if normalized == "ADMIN_MASTER":
        return "ADMIN_MASTER"
    if normalized in ["ADMIN_IMOBILIARIA", "IMOBILIARIA"]:
        return "IMOBILIARIA"
    if normalized == "CORRETOR":
        return "CORRETOR"
    if normalized == "CLIENTE":
        return "CLIENTE"
    return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def get_invitation_token(email: str, user_type: str, imobiliaria_id: Optional[str] = None):
    return create_access_token(data={
        "email": email,
        "user_type": user_type,
        "imobiliaria_id": imobiliaria_id,
        "invitation": True
    }, expires_delta=datetime.timedelta(days=7))

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()

    # Normalizar claims para compatibilidade com RLS
    if "role" not in to_encode:
        if "tipo" in to_encode:
            to_encode["role"] = _normalize_role_for_jwt(to_encode.get("tipo"))
        elif "user_type" in to_encode:
            to_encode["role"] = _normalize_role_for_jwt(to_encode.get("user_type"))

    if "imobiliaria_id" not in to_encode and "imob_id" in to_encode:
        to_encode["imobiliaria_id"] = to_encode.get("imob_id")

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


def generate_user_id():
    return str(uuid.uuid4())


def generate_property_id():
    return str(uuid.uuid4())


def generate_client_id():
    return str(uuid.uuid4())


def generate_lead_id():
    return str(uuid.uuid4())


def generate_imobiliaria_id():
    return str(uuid.uuid4())


def generate_verification_code() -> str:
    """Gera código de verificação de 6 dígitos"""
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


def get_user_role(user_id: str) -> str:
    """Obtém role do usuário do DB"""
    from database import get_memory_db
    db = get_memory_db()
    user = db["users"].get(user_id)
    return user.get("tipo", "cliente") if user else "cliente"


def require_role(required_roles: list, user_id: str):
    """Verifica se usuário tem role necessária"""
    role = get_user_role(user_id)
    if role not in required_roles:
        raise Exception(f"Role necessária: {required_roles}. Usuário tem: {role}")
    return True


def get_current_user_role(authorization: Optional[str] = Header(None)):
    """Dependência FastAPI para role do usuário atual"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requerido")
    
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user_id = payload.get("sub")
    role = get_user_role(user_id)
    
    return {"user_id": user_id, "role": role}
