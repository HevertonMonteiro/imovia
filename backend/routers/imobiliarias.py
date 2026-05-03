from fastapi import APIRouter, HTTPException, Depends, Header, Query
from typing import Optional, List
from models.schemas import (
    ImobiliáriaCreate, 
    ImobiliáriaUpdate, 
    ImobiliáriaResponse,
    ImobiliáriaStatus,
    Plano
)
from auth_utils import decode_access_token, generate_imobiliaria_id
from database import get_memory_db
from datetime import datetime, timedelta

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
    """Verifica se o usuário é admin_master"""
    user_tipo = current_user.get("tipo", "")
    if user_tipo not in ["admin_master"]:
        raise HTTPException(status_code=403, detail="Acesso restrito ao administrador master")
    return current_user


@router.get("", response_model=List[ImobiliáriaResponse])
async def list_imobiliarias(
    current_user: dict = Depends(require_admin),
    status: Optional[ImobiliáriaStatus] = None,
    limit: int = Query(50, le=100),
    offset: int = Query(0)
):
    """Lista todas as imobiliárias (apenas admin)"""
    db = get_memory_db()
    imobilirias = list(db["imobiliarias"].values())
    
    # Filtrar por status
    if status:
        imobilirias = [i for i in imobilirias if i.get("status") == status.value]
    
    # Ordenar por criação
    imobilirias.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Paginar
    imobilirias = imobilirias[offset:offset + limit]
    
    return [ImobiliáriaResponse(**i) for i in imobilirias]


@router.get("/{imobiliaria_id}", response_model=ImobiliáriaResponse)
async def get_imobiliaria(
    imobiliaria_id: str,
    current_user: dict = Depends(require_admin)
):
    """Obtém detalhes de uma imobiliária"""
    db = get_memory_db()
    imob = db["imobiliarias"].get(imobiliaria_id)
    
    if not imob:
        raise HTTPException(status_code=404, detail="Imobiliária não encontrada")
    
    return ImobiliáriaResponse(**imob)


@router.post("", response_model=ImobiliáriaResponse)
async def create_imobiliaria(
    imob: ImobiliáriaCreate,
    current_user: dict = Depends(require_admin)
):
    """Cria uma nova imobiliária (apenas admin_master)"""
    db = get_memory_db()

    # Verificar se email já existe
    for existing in db["imobiliarias"].values():
        if existing.get("email") == imob.email:
            raise HTTPException(status_code=400, detail="Email já cadastrado")

    # Verificar se já existe usuário com este email
    for existing_user in db["users"].values():
        if existing_user.get("email") == imob.email:
            raise HTTPException(status_code=400, detail="Email já cadastrado para um usuário")

    # Gerar ID único
    imob_id = generate_imobiliaria_id()
    now = str(datetime.now())

    # Calcular trial de 7 dias
    trial_end = datetime.now() + timedelta(days=7)

    new_imob = {
        "id": imob_id,
        "nome": imob.nome,
        "email": imob.email,
        "status": ImobiliáriaStatus.ATIVO.value,
        "plano": Plano.FREE.value,
        "data_pagamento": None,
        "trial_termino": str(trial_end),
        "created_at": now
    }

    db["imobiliarias"][imob_id] = new_imob

    # Criar automaticamente usuário admin_imobiliaria
    from auth_utils import get_password_hash, generate_user_id
    admin_user_id = generate_user_id()
    hashed_password = get_password_hash("123456")  # Senha padrão

    admin_user = {
        "id": admin_user_id,
        "email": imob.email,
        "name": f"Admin {imob.nome}",
        "password": hashed_password,
        "tipo": "admin_imobiliaria",
        "imobiliaria_id": imob_id,
        "ativo": True,
        "password_set": False,
        "created_at": now
    }

    db["users"][admin_user_id] = admin_user

    print(f"✅ Imobiliária criada: {imob.nome} ({imob.email})")
    print(f"✅ Admin criado: {imob.email} / 123456")

    return ImobiliáriaResponse(**new_imob)


@router.put("/{imobiliaria_id}", response_model=ImobiliáriaResponse)
async def update_imobiliaria(
    imobiliaria_id: str,
    imob_update: ImobiliáriaUpdate,
    current_user: dict = Depends(require_admin)
):
    """Atualiza uma imobiliária (apenas admin)"""
    db = get_memory_db()
    imob = db["imobiliarias"].get(imobiliaria_id)
    
    if not imob:
        raise HTTPException(status_code=404, detail="Imobiliária não encontrada")
    
    # Atualizar campos
    if imob_update.nome is not None:
        imob["nome"] = imob_update.nome
    if imob_update.email is not None:
        imob["email"] = imob_update.email
    if imob_update.status is not None:
        imob["status"] = imob_update.status.value
    if imob_update.plano is not None:
        imob["plano"] = imob_update.plano.value
    if imob_update.data_pagamento is not None:
        imob["data_pagamento"] = str(imob_update.data_pagamento)
    
    db["imobiliarias"][imobiliaria_id] = imob
    
    return ImobiliáriaResponse(**imob)


@router.delete("/{imobiliaria_id}")
async def delete_imobiliaria(
    imobiliaria_id: str,
    current_user: dict = Depends(require_admin)
):
    """Exclui uma imobiliária (apenas admin)"""
    db = get_memory_db()
    imob = db["imobiliarias"].get(imobiliaria_id)
    
    if not imob:
        raise HTTPException(status_code=404, detail="Imobiliária não encontrada")
    
    # Verificar se existem corretores vinculados
    corretores = [u for u in db["users"].values() if u.get("imobiliaria_id") == imobiliaria_id]
    if corretores:
        raise HTTPException(
            status_code=400, 
            detail="Não é possível excluir. Existem corretores vinculados."
        )
    
    del db["imobiliarias"][imobiliaria_id]
    
    return {"message": "Imobiliária excluída com sucesso"}


@router.post("/{imobiliaria_id}/activate")
async def activate_imobiliaria(
    imobiliaria_id: str,
    current_user: dict = Depends(require_admin)
):
    """Ativa uma imobiliária"""
    db = get_memory_db()
    imob = db["imobiliarias"].get(imobiliaria_id)
    
    if not imob:
        raise HTTPException(status_code=404, detail="Imobiliária não encontrada")
    
    imob["status"] = ImobiliáriaStatus.ATIVO.value
    db["imobiliarias"][imobiliaria_id] = imob
    
    return {"message": "Imobiliária ativada com sucesso"}


@router.post("/{imobiliaria_id}/deactivate")
async def deactivate_imobiliaria(
    imobiliaria_id: str,
    current_user: dict = Depends(require_admin)
):
    """Desativa uma imobiliária"""
    db = get_memory_db()
    imob = db["imobiliarias"].get(imobiliaria_id)
    
    if not imob:
        raise HTTPException(status_code=404, detail="Imobiliária não encontrada")
    
    imob["status"] = ImobiliáriaStatus.INATIVO.value
    db["imobiliarias"][imobiliaria_id] = imob
    
    return {"message": "Imobiliária desativada com sucesso"}


@router.post("/{imobiliaria_id}/upgrade")
async def upgrade_plan(
    imobiliaria_id: str,
    plano: str,
    current_user: dict = Depends(require_admin)
):
    """Atualiza o plano da imobiliária"""
    db = get_memory_db()
    imob = db["imobiliarias"].get(imobiliaria_id)
    
    if not imob:
        raise HTTPException(status_code=404, detail="Imobiliária não encontrada")
    
    # Validar plano
    if plano not in ["free", "premium", "enterprise"]:
        raise HTTPException(status_code=400, detail="Plano inválido")
    
    imob["plano"] = plano
    imob["data_pagamento"] = str(datetime.now())
    db["imobiliarias"][imobiliaria_id] = imob
    
    return {
        "message": f"Plano atualizado para {plano}",
        "plano": plano
    }


@router.get("/{imobiliaria_id}/stats")
async def get_imobiliaria_stats(
    imobiliaria_id: str,
    current_user: dict = Depends(require_admin)
):
    """Obtém estatísticas da imobiliária"""
    db = get_memory_db()
    imob = db["imobiliarias"].get(imobiliaria_id)
    
    if not imob:
        raise HTTPException(status_code=404, detail="Imobiliária não encontrada")
    
    # Contar corretores
    corretores = [u for u in db["users"].values() if u.get("imobiliaria_id") == imobiliaria_id]
    
    # Contar imóveis
    imoveis = [p for p in db["properties"].values() if p.get("user_id") in [c["id"] for c in corretores]]
    
# Contar leads
    leads = [l for l in db["leads"].values() if l.get("user_id") in [c["id"] for c in corretores]]
    
    return {
        "imobiliaria_id": imobiliaria_id,
        "nome": imob.get("nome"),
        "status": imob.get("status"),
        "plano": imob.get("plano"),
        "total_corretores": len(corretores),
        "total_imoveis": len(imoveis),
        "total_leads": len(leads),
        "created_at": imob.get("created_at")
    }


# ===== REMOÇÃO DE IMOBILIÁRIA =====

@router.delete("/{imobiliaria_id}")
async def delete_imobiliaria(
    imobiliaria_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Remove uma imobiliária e todos os seus dados vinculados.
    
    Isso remove:
    - A imobiliária
    - Todos os corretores vinculados
    - Todos os imóveis dos corretores
    """
    db = get_memory_db()
    
    # Verificar permissão
    if current_user.get("tipo") != "admin":
        raise HTTPException(status_code=403, detail="Apenas admin pode remover imobiliárias")
    
    # Verificar se imobiliária existe
    imob = db["imobiliarias"].get(imobiliaria_id)
    if not imob:
        raise HTTPException(status_code=404, detail="Imobiliária não encontrada")
    
    # Buscar corretores vinculados
    corretores = [
        user_id for user_id, u in db["users"].items() 
        if u.get("imobiliaria_id") == imobiliaria_id
    ]
    
    # Remover imóveis de cada corretor
    properties_to_remove = [
        prop_id for prop_id, p in db["properties"].items()
        if p.get("user_id") in corretores
    ]
    for prop_id in properties_to_remove:
        del db["properties"][prop_id]
    
    # Remover corretores (inativar)
    for corretor_id in corretores:
        if corretor_id in db["users"]:
            db["users"][corretor_id]["ativo"] = False
            db["users"][corretor_id]["removed_at"] = str(datetime.now())
    
    # Remover a imobiliária
    del db["imobiliarias"][imobiliaria_id]
    
    return {
        "message": "Imobiliária removida com sucesso.",
        "imobiliaria_id": imobiliaria_id,
        "corretores_inativados": len(corretores),
        "imoveis_removidos": len(properties_to_remove)
    }
