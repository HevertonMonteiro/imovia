from fastapi import APIRouter, HTTPException, Depends, Query, Header
from typing import Optional, List
from models.schemas import ClientCreate, ClientResponse, ClientPreferencesUpdate
from auth_utils import generate_client_id, decode_access_token
from database import get_memory_db
from datetime import datetime

router = APIRouter()


def get_current_user_id(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Não autorizado")
    
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    return payload.get("sub")


@router.get("", response_model=List[ClientResponse])
async def list_clients(
    current_user_id: str = Depends(get_current_user_id),
    search: Optional[str] = None,
    limit: int = Query(50, le=100),
    offset: int = 0
):
    db = get_memory_db()
    clients = list(db["clients"].values())
    
    # Filtrar por usuário
    clients = [c for c in clients if c.get("user_id") == current_user_id]
    
    # Filtrar por busca
    if search:
        search_lower = search.lower()
        clients = [c for c in clients if search_lower in c.get("name", "").lower() or 
                   search_lower in c.get("email", "").lower() or
                   search_lower in c.get("phone", "").lower()]
    
    # Ordenar por data
    clients.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Paginar
    clients = clients[offset:offset + limit]
    
    return [ClientResponse(**c) for c in clients]


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(client_id: str, current_user_id: str = Depends(get_current_user_id)):
    db = get_memory_db()
    client = db["clients"].get(client_id)
    
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    if client.get("user_id") != current_user_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return ClientResponse(**client)


@router.post("", response_model=ClientResponse)
async def create_client(
    client: ClientCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    db = get_memory_db()
    
    client_id = generate_client_id()
    now = str(datetime.now())
    
    new_client = {
        "id": client_id,
        "user_id": current_user_id,
        "name": client.name,
        "email": client.email,
        "phone": client.phone,
        "interest": client.interest,
        "notes": client.notes,
        "created_at": now
    }
    
    db["clients"][client_id] = new_client
    
    return ClientResponse(**new_client)


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    client: ClientCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    db = get_memory_db()
    existing_client = db["clients"].get(client_id)
    
    if not existing_client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    if existing_client.get("user_id") != current_user_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Atualizar campos
    existing_client.update(client.model_dump())
    db["clients"][client_id] = existing_client
    
    return ClientResponse(**existing_client)


@router.delete("/{client_id}")
async def delete_client(client_id: str, current_user_id: str = Depends(get_current_user_id)):
    db = get_memory_db()
    client = db["clients"].get(client_id)
    
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    if client.get("user_id") != current_user_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    del db["clients"][client_id]
    
    return {"message": "Cliente deletado com sucesso"}


@router.put("/preferences", response_model=ClientResponse)
async def update_client_preferences(
    preferences: ClientPreferencesUpdate,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Atualiza as preferências do cliente logado.
    Usado pela página de preferências do cliente.
    """
    db = get_memory_db()
    clients = list(db["clients"].values())
    
    # Procurar cliente pelo usuário logado
    client = None
    client_id = None
    for c in clients:
        if c.get("user_id") == current_user_id:
            client = c
            client_id = c.get("id")
            break
    
    # Se não existir, criar novo cliente com preferências
    if not client:
        client_id = generate_client_id()
        now = str(datetime.now())
        client = {
            "id": client_id,
            "user_id": current_user_id,
            "name": "Cliente",
            "email": None,
            "phone": None,
            "interest": None,
            "notes": None,
            "preferences": preferences.model_dump(exclude_none=True),
            "created_at": now
        }
        db["clients"][client_id] = client
    else:
        # Atualizar preferências
        prefs = client.get("preferences", {})
        prefs.update(preferences.model_dump(exclude_none=True))
        client["preferences"] = prefs
        db["clients"][client_id] = client
    
    return ClientResponse(**client)


from typing import Optional
from fastapi import Header
