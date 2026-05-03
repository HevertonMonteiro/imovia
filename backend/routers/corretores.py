from fastapi import APIRouter, HTTPException, Depends, Header, Query, Request
from typing import Optional, List
from models.schemas import UserResponse, UserRole, UserCreate
from auth_utils import decode_access_token, generate_user_id, get_password_hash
from database import get_memory_db
from middleware import get_current_user_from_request
from datetime import datetime

router = APIRouter()


def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Não autorizado")

    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Token inválido")

    return payload


def require_admin(current_user: dict = Depends(get_current_user)):
    """Verifica se o usuário é admin_master ou admin_imobiliaria"""
    user_tipo = current_user.get("tipo", "")
    if user_tipo not in ["admin_master", "admin_imobiliaria"]:
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return current_user


def _can_manage_corretor(user_info: dict, corretor: dict) -> bool:
    if user_info.get("role") == "admin_master":
        return corretor.get("created_by") == user_info.get("user_id")

    if user_info.get("role") == "admin_imobiliaria":
        return corretor.get("imobiliaria_id") == user_info.get("imobiliaria_id")

    return False


@router.get("", response_model=List[UserResponse])
async def list_corretores(
    request: Request,
    imobiliaria_id: Optional[str] = Query(None),
    ativo: Optional[bool] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0)
):
    """Lista todos os corretores (com filtros RBAC)"""
    db = get_memory_db()
    user_info = get_current_user_from_request(request)
    corretores = []

    for user_id, user in db["users"].items():
        if user.get("tipo") != "corretor":
            continue

        if not _can_manage_corretor(user_info, user):
            continue

        if imobiliaria_id and user.get("imobiliaria_id") != imobiliaria_id:
            continue

        # Filtrar por status ativo se especificado
        if ativo is not None and user.get("ativo", True) != ativo:
            continue

        corretores.append(UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            tipo=UserRole(user.get("tipo", "cliente")),
            imobiliaria_id=user.get("imobiliaria_id"),
            ativo=user.get("ativo", True),
            created_at=datetime.fromisoformat(user.get("created_at", str(datetime.now())))
        ))

    return corretores[offset:offset + limit]


@router.get("/{corretor_id}", response_model=UserResponse)
async def get_corretor(
    corretor_id: str,
    request: Request
):
    """Obtém detalhes de um corretor específico"""
    db = get_memory_db()
    user_info = get_current_user_from_request(request)
    user = db["users"].get(corretor_id)

    if not user or user.get("tipo") != "corretor":
        raise HTTPException(status_code=404, detail="Corretor não encontrado")

    if not _can_manage_corretor(user_info, user):
        raise HTTPException(status_code=403, detail="Acesso negado")

    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        tipo=UserRole(user.get("tipo")),
        imobiliaria_id=user.get("imobiliaria_id"),
        ativo=user.get("ativo", True),
        created_at=datetime.fromisoformat(user.get("created_at"))
    )


@router.post("", response_model=UserResponse)
async def create_corretor(
    corretor: UserCreate,
    request: Request
):
    """Cria um novo corretor (admin_master ou admin_imobiliaria)"""
    db = get_memory_db()
    user_info = get_current_user_from_request(request)
    role = user_info.get("role")

    if role not in ["admin_master", "admin_imobiliaria"]:
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")

    if role == "admin_imobiliaria":
        imobiliaria_id = user_info.get("imobiliaria_id")
        if not imobiliaria_id:
            raise HTTPException(status_code=400, detail="Imobiliária não encontrada")
    else:
        imobiliaria_id = None

    for existing_user in db["users"].values():
        if existing_user.get("email") == corretor.email:
            raise HTTPException(status_code=400, detail="Email já cadastrado")

    corretor_id = generate_user_id()
    hashed_password = get_password_hash("123456")
    now = str(datetime.now())

    new_corretor = {
        "id": corretor_id,
        "email": corretor.email,
        "name": corretor.name,
        "password": hashed_password,
        "tipo": "corretor",
        "imobiliaria_id": imobiliaria_id,
        "created_by": user_info.get("user_id"),
        "ativo": True,
        "password_set": False,
        "created_at": now
    }

    db["users"][corretor_id] = new_corretor

    return UserResponse(
        id=corretor_id,
        email=corretor.email,
        name=corretor.name,
        tipo=UserRole.CORRETOR,
        imobiliaria_id=imobiliaria_id,
        ativo=True,
        created_at=datetime.fromisoformat(now)
    )


@router.post("/{corretor_id}/deactivate")
async def deactivate_corretor(
    corretor_id: str,
    request: Request
):
    """Desativa um corretor"""
    db = get_memory_db()
    user_info = get_current_user_from_request(request)
    user = db["users"].get(corretor_id)

    if not user or user.get("tipo") != "corretor":
        raise HTTPException(status_code=404, detail="Corretor não encontrado")

    if not _can_manage_corretor(user_info, user):
        raise HTTPException(status_code=403, detail="Acesso negado")

    user["ativo"] = False
    db["users"][corretor_id] = user
    return {"message": "Corretor desativado com sucesso"}


@router.post("/{corretor_id}/activate")
async def activate_corretor(
    corretor_id: str,
    request: Request
):
    """Ativa um corretor"""
    db = get_memory_db()
    user_info = get_current_user_from_request(request)
    user = db["users"].get(corretor_id)

    if not user or user.get("tipo") != "corretor":
        raise HTTPException(status_code=404, detail="Corretor não encontrado")

    if not _can_manage_corretor(user_info, user):
        raise HTTPException(status_code=403, detail="Acesso negado")

    user["ativo"] = True
    db["users"][corretor_id] = user
    return {"message": "Corretor ativado com sucesso"}


@router.delete("/{corretor_id}")
async def delete_corretor(
    corretor_id: str,
    request: Request
):
    """Exclui um corretor"""
    db = get_memory_db()
    user_info = get_current_user_from_request(request)
    user = db["users"].get(corretor_id)

    if not user or user.get("tipo") != "corretor":
        raise HTTPException(status_code=404, detail="Corretor não encontrado")

    if not _can_manage_corretor(user_info, user):
        raise HTTPException(status_code=403, detail="Acesso negado")

    properties = [p for p in db["properties"].values() if p.get("user_id") == corretor_id]
    if properties:
        raise HTTPException(
            status_code=400,
            detail=f"Não é possível excluir. Existem {len(properties)} imóveis vinculados a este corretor."
        )

    leads = [l for l in db["leads"].values() if l.get("user_id") == corretor_id]
    if leads:
        raise HTTPException(
            status_code=400,
            detail=f"Não é possível excluir. Existem {len(leads)} leads vinculados a este corretor."
        )

    del db["users"][corretor_id]
    return {"message": "Corretor excluído com sucesso"}
