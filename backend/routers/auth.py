from fastapi import APIRouter, HTTPException, Depends, Header, Query
from typing import Optional
from datetime import datetime
from models.schemas import UserCreate, UserResponse, TokenResponse, UserRole, ImobiliáriaStatus
from auth_utils import verify_password, get_password_hash, create_access_token, decode_access_token, generate_user_id, generate_verification_code, get_invitation_token
from database import get_memory_db
import uuid

router = APIRouter()


def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Não autorizado")
    
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    return payload


def get_invitation_token(email: str, user_type: str, imobiliaria_id: Optional[str] = None):
    """Gera token de convite para criação de senha"""
    return create_access_token(data={
        "email": email,
        "user_type": user_type,
        "imobiliaria_id": imobiliaria_id,
        "invitation": True
    }, expires_delta=datetime.timedelta(days=7))


@router.post("/register", response_model=TokenResponse)
async def register(
    user: UserCreate,
    tipo: str = "cliente"
):

    db = get_memory_db()

    # Verificar se usuário já existe
    for existing_user in db["users"].values():
        if existing_user.get("email") == user.email:
            raise HTTPException(status_code=400, detail="Email já cadastrado")

    # Criar novo usuário
    user_id = generate_user_id()
    hashed_password = get_password_hash(user.password)

    # Vinculação especial para admin geral
    imobiliaria_id = None
    if tipo == "admin":
        # Admin geral não precisa de imobiliária
        imobiliaria_id = None
    elif tipo == "corretor":
        # Corretor precisa de uma imobiliária (será vinculada depois)
        imobiliaria_id = None

    new_user = {
        "id": user_id,
        "email": user.email,
        "name": user.name,
        "password": hashed_password,
        "tipo": tipo,
        "imobiliaria_id": imobiliaria_id,
        "ativo": True,  # Usuário ativo por padrão
        "email_verified": False,  # Pendente de verificação
        "created_at": str(datetime.now())
    }
    
    db["users"][user_id] = new_user
    
    # Gerar código de verificação
    code = generate_verification_code()
    db["verification_codes"][user_id] = {
        "code": code,
        "email": user.email,
        "expires": str(datetime.now())  # TODO: adicionar 10 minutos
    }
    
    # TODO: Enviar email (simulado no console)
    print(f"📧 Código de verificação para {user.email}: {code}")
    
    # Criar token

    access_token = create_access_token(data={
        "sub": user_id,
        "email": user.email,
        "tipo": new_user["tipo"],
        "imobiliaria_id": imobiliaria_id
    })
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            id=user_id,
            email=user.email,
            name=user.name,
            tipo=UserRole(tipo),
            imobiliaria_id=imobiliaria_id,
            ativo=True,
            created_at=datetime.now()
        )
    )


@router.post("/verify-email")
async def verify_email(user_id: str, code: str):
    """Verifica o email do usuário com o código"""
    db = get_memory_db()
    
    # Verificar código
    stored = db["verification_codes"].get(user_id)
    if not stored:
        raise HTTPException(status_code=400, detail="Código não encontrado ou expirado")
    
    # Verificar expiração (10 minutos)
    from datetime import datetime, timedelta
    code_time = datetime.fromisoformat(stored["expires"].replace(":", "-"))
    now = datetime.now()
    if now > code_time + timedelta(minutes=10):
        del db["verification_codes"][user_id]
        raise HTTPException(status_code=400, detail="Código expirado. Solicite um novo código.")
    
    if stored["code"] != code:
        raise HTTPException(status_code=400, detail="Código inválido")
    
    # Ativar usuário
    user = db["users"].get(user_id)
    if user:
        user["email_verified"] = True
        db["users"][user_id] = user
    
    # Remover código usado
    del db["verification_codes"][user_id]
    
    return {"message": "Email verificado com sucesso!"}


@router.post("/resend-code/{user_id}")
async def resend_code(user_id: str):
    """Reenvia o código de verificação"""
    db = get_memory_db()
    
    user = db["users"].get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Gerar novo código
    code = generate_verification_code()
    db["verification_codes"][user_id] = {
        "code": code,
        "email": user["email"],
        "expires": str(datetime.now())
    }
    
    print(f"📧 Novo código de verificação para {user['email']}: {code}")
    
    return {"message": "Código reenviado!"}


# ===== SISTEMA DE CONVITE PARA CRIAÇÃO DE SENHA =====

@router.post("/invite")
async def send_invitation(
    email: str,
    user_type: str,
    imobiliaria_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Envia convite por email para criar senha
    Only admin_master or admin_imobiliaria can send invitations
    """
    db = get_memory_db()
    user = db["users"].get(current_user.get("sub"))
    
    # Verificar permissão
    user_role = user.get("tipo", "")
    if user_role not in ["admin_master", "admin_imobiliaria"]:
        raise HTTPException(status_code=403, detail="Sem permissão para enviar convite")
    
    # Verificar se usuário já existe
    for existing in db["users"].values():
        if existing.get("email") == email:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Gerar token de convite
    invitation_token = get_invitation_token(email, user_type, imobiliaria_id)
    
    # Criar usuário temporário (sem senha)
    user_id = generate_user_id()
    new_user = {
        "id": user_id,
        "email": email,
        "name": "",  # Será preenchido ao definir senha
        "password": "",  # Não tem senha ainda
        "tipo": user_type,
        "imobiliaria_id": imobiliaria_id,
        "ativo": True,
        "password_set": False,  # Senha ainda não definida
        "created_at": str(datetime.now())
    }
    
    db["users"][user_id] = new_user
    
    # Simular envio de email
    print(f"📧========================================")
    print(f"📧 E-mail de convite enviado!")
    print(f"📧 Para: {email}")
    print(f"📧 Tipo: {user_type}")
    print(f"📧========================================")
    print(f"📧 Token de convite: {invitation_token}")
    print(f"📧 Link: /set-password?token={invitation_token}")
    print(f"📧========================================")
    
    return {
        "message": "Convite enviado com sucesso!",
        "user_id": user_id,
        "token": invitation_token
    }


@router.post("/set-password")
async def set_password_from_invitation(
    token: str,
    password: str,
    name: str
):
    """
    Define senha através do token de convite
    """
    db = get_memory_db()
    
    # Decodificar token
    payload = decode_access_token(token)
    if not payload or not payload.get("invitation"):
        raise HTTPException(status_code=400, detail="Token de convite inválido ou expirado")
    
    email = payload.get("email")
    
    # Buscar usuário
    user = None
    for u in db["users"].values():
        if u.get("email") == email and u.get("password_set") == False:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado ou senha já definida")
    
    # Verificar senha
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Senha deve ter pelo menos 6 caracteres")
    
    # Definir senha
    user["password"] = get_password_hash(password)
    user["name"] = name
    user["password_set"] = True
    
    db["users"][user["id"]] = user
    
    # Criar token de acesso
    access_token = create_access_token(data={
        "sub": user["id"],
        "email": user["email"],
        "tipo": user["tipo"],
        "imobiliaria_id": user.get("imobiliaria_id")
    })
    
    # Gerar código de verificação de email
    code = generate_verification_code()
    db["verification_codes"][user["id"]] = {
        "code": code,
        "email": user["email"],
        "expires": str(datetime.now())
    }
    
    print(f"✅ Usuário {email} definiu sua senha com sucesso!")
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            tipo=UserRole(user.get("tipo", "cliente")),
            imobiliaria_id=user.get("imobiliaria_id"),
            ativo=user.get("ativo", True),
            created_at=datetime.now()
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    email: str = Query(...),
    password: str = Query(...)
):
    db = get_memory_db()
    
    # Buscar usuário
    user = None
    for u in db["users"].values():
        if u["email"] == email:
            user = u
            break
    
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    
    # Verificar se usuário está ativo
    if not user.get("ativo", True):
        raise HTTPException(status_code=403, detail="Usuário inativo. Entre em contato com o suporte.")
    
    # Verificar se é corretor/admin e verificar status da imobiliária
    user_tipo = user.get("tipo", "cliente")
    imob_status = None
    
    if user_tipo in ["corretor", "admin"] and user.get("imobiliaria_id"):
        imob = db["imobiliarias"].get(user["imobiliaria_id"])
        if imob:
            imob_status = imob.get("status")
    
    # Criar token
    access_token = create_access_token(data={
        "sub": user["id"],
        "email": user["email"],
        "tipo": user_tipo,
        "imobiliaria_id": user.get("imobiliaria_id"),
        "imob_status": imob_status
    })
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            tipo=UserRole(user.get("tipo", "cliente")),
            imobiliaria_id=user.get("imobiliaria_id"),
            ativo=user.get("ativo", True),
            created_at=datetime.now()
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    db = get_memory_db()
    user = db["users"].get(current_user.get("sub"))
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        tipo=UserRole(user.get("tipo", "cliente")),
        imobiliaria_id=user.get("imobiliaria_id"),
        ativo=user.get("ativo", True),
        created_at=datetime.now()
    )


@router.get("/permissions")
async def get_permissions(current_user: dict = Depends(get_current_user)):
    """Retorna as permissões do usuário com base no tipo e status"""
    db = get_memory_db()
    user = db["users"].get(current_user.get("sub"))
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    user_tipo = user.get("tipo", "cliente")
    imob_id = user.get("imobiliaria_id")
    
    # Permissões padrão para cliente
    permissions = {
        "can_view_catalog": True,
        "can_create_properties": False,
        "can_edit_properties": False,
        "can_delete_properties": False,
        "can_view_leads": False,
        "can_view_dashboard": False,
        "can_manage_corretors": False,
        "can_manage_imobiliaria": False,
        "plan_status": "free"
    }
    
    # Se for corretor ou admin, verificar status da imobiliária
    if user_tipo in ["corretor", "admin"] and imob_id:
        imob = db["imobiliarias"].get(imob_id)
        if imob:
            imob_status = imob.get("status", "trial")
            if imob_status == "ativo":
                permissions = {
                    "can_view_catalog": True,
                    "can_create_properties": True,
                    "can_edit_properties": True,
                    "can_delete_properties": True,
                    "can_view_leads": True,
                    "can_view_dashboard": True,
                    "can_manage_corretors": user_tipo == "admin",
                    "can_manage_imobiliaria": user_tipo == "admin",
                    "plan_status": imob.get("plano", "free")
                }
            else:
                # Inativo - modo visualização
                permissions = {
                    "can_view_catalog": True,
                    "can_create_properties": False,
                    "can_edit_properties": False,
                    "can_delete_properties": False,
                    "can_view_leads": False,
                    "can_view_dashboard": False,
                    "can_manage_corretors": False,
                    "can_manage_imobiliaria": False,
                    "plan_status": imob_status,
                    "warning": "Seu plano está inativo. Regularize o pagamento para liberar todas as funcionalidades."
                }
    elif user_tipo == "cliente":
        permissions = {
            "can_view_catalog": True,
            "can_create_properties": False,
            "can_edit_properties": False,
            "can_delete_properties": False,
            "can_view_leads": False,
            "can_view_dashboard": False,
            "can_manage_corretors": False,
            "can_manage_imobiliaria": False,
"plan_status": "cliente"
        }
    
    return permissions


# ===== PERFIL DO USUÁRIO =====

from pydantic import BaseModel


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile: ProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Atualiza informações básicas do usuário logado."""


@router.put("/profile", include_in_schema=False)
async def _update_profile_deprecated(profile: ProfileUpdate, current_user: dict = Depends(get_current_user)):
    """Compatibilidade interna (mantida por segurança)."""
    return await update_profile(profile=profile, current_user=current_user)


@router.put("/profile", response_model=UserResponse)
async def update_profile_alias(
    profile: ProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Alias legado para o frontend (PUT /auth/profile)."""
    db = get_memory_db()
    user_id = current_user.get("sub")
    user = db["users"].get(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    update_data = profile.model_dump(exclude_none=True)

    if "name" in update_data:
        user["name"] = update_data["name"]
    if "phone" in update_data:
        user["phone"] = update_data["phone"]

    db["users"][user_id] = user

    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user.get("name"),
        tipo=UserRole(user.get("tipo", "cliente")),
        imobiliaria_id=user.get("imobiliaria_id"),
        ativo=user.get("ativo", True),
        created_at=datetime.now()
    )

    db = get_memory_db()
    user_id = current_user.get("sub")
    user = db["users"].get(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    update_data = profile.model_dump(exclude_none=True)

    if "name" in update_data:
        user["name"] = update_data["name"]
    if "phone" in update_data:
        user["phone"] = update_data["phone"]

    db["users"][user_id] = user

    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user.get("name"),
        tipo=UserRole(user.get("tipo", "cliente")),
        imobiliaria_id=user.get("imobiliaria_id"),
        ativo=user.get("ativo", True),
        created_at=datetime.now()
    )


# ===== SISTEMA DE REMOÇÃO DE USUÁRIOS =====

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Remove um usuário (apenas admin pode remover).
    
    Para corretores: mantém histórico mas marca como inativo.
    Para cliente: remove completamente.
    """
    db = get_memory_db()
    
    # Verificar permissão (apenas admin)
    user_role = current_user.get("tipo", "")
    if user_role not in ["admin_master", "admin"]:
        raise HTTPException(status_code=403, detail="Sem permissão para remover usuários")
    
    # Verificar se usuário existe
    target_user = db["users"].get(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Não permite auto-remoção
    if user_id == current_user.get("sub"):
        raise HTTPException(status_code=400, detail="Não é possível remover a si mesmo")
    
    user_type = target_user.get("tipo", "")
    
    if user_type == "corretor":
        # Corretor: apenas inativar (mantém histórico)
        target_user["ativo"] = False
        target_user["removed_at"] = str(datetime.now())
        db["users"][user_id] = target_user
        
        return {
            "message": "Corretor inativado com sucesso. Histórico preservado.",
            "user_id": user_id,
            "status": "inativo"
        }
    elif user_type == "cliente":
        # Cliente: remove completamente
        del db["users"][user_id]
        
        return {
            "message": "Cliente removido com sucesso.",
            "user_id": user_id,
            "status": "removido"
        }
    else:
        raise HTTPException(status_code=400, detail="Tipo de usuário não suportado para remoção")
