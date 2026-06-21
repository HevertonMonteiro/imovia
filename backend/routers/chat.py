from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime

from auth_utils import decode_access_token
from database import get_memory_db

router = APIRouter()


def get_current_user_id(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Não autorizado")

    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Token inválido")

    return payload.get("sub")


# =====================
# Schemas do chat (MVP)
# =====================

class ChatConversationCreate(BaseModel):
    property_id: str
    lead_id: Optional[str] = None


class ChatMessageCreate(BaseModel):
    text: str
    # opcional: qual conversa ativa
    property_id: Optional[str] = None


class ChatActionRequest(BaseModel):
    # "catalogo" ou "transfer_visit" (quero prosseguir / falar responsável)
    action: str


# =====================
# Helpers
# =====================


def _now_str():
    return str(datetime.now())


def _ensure_tables(db: Dict):
    db.setdefault("chat_conversations", {})
    db.setdefault("chat_messages", {})
    db.setdefault("chat_conversation_index", {})


def _get_user(db, user_id: str):
    return db["users"].get(user_id)


def _conversation_key(user_id: str, property_id: str, lead_id: Optional[str]):
    # evita duplicar conversas do mesmo cliente no mesmo imóvel
    return f"{user_id}:{lead_id or 'none'}:{property_id}"


async def _select_best_corretor_for_user(db: Dict) -> Optional[dict]:
    """Seleciona corretor com melhor ranking (usando dashboard/ranking já existente).

    Como é MVP e tudo roda em memória, calculamos a métrica aqui.
    Preferência: corretor ativo com maior conversão (aprox.) e mais leads.
    """
    users = db["users"]
    properties = db["properties"]
    leads = db["leads"]

    corretores = [u for u in users.values() if u.get("tipo") == "corretor" and u.get("ativo", True)]
    if not corretores:
        return None

    best = None
    best_score = None

    for c in corretores:
        corretor_id = c["id"]
        props = [p for p in properties.values() if p.get("user_id") == corretor_id]
        sold = len([p for p in props if p.get("status") == "vendido"])
        total_leads = len([l for l in leads.values() if l.get("user_id") == corretor_id])
        conversion = (sold / total_leads) * 100 if total_leads > 0 else 0.0
        total_views = sum(p.get("views", 0) for p in props)
        total_properties = len(props)

        # score simples (MVP)
        score = conversion * 3 + total_leads * 1 + total_properties * 0.5 + total_views * 0.0001
        if best is None or score > best_score:
            best = c
            best_score = score

    return best


# =====================
# Endpoints
# =====================


@router.post("/conversations", response_model=dict)
async def create_conversation(
    payload: ChatConversationCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    db = get_memory_db()
    _ensure_tables(db)

    user_id = current_user_id
    property_id = payload.property_id

    if payload.lead_id:
        # valida lead que pertence ao usuário
        lead = db["leads"].get(payload.lead_id)
        if not lead or lead.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Lead não pertence ao usuário")

    key = _conversation_key(user_id, property_id, payload.lead_id)
    existing = db["chat_conversation_index"].get(key)
    if existing:
        return existing

    conversation_id = f"conv_{len(db['chat_conversations']) + 1}_{int(datetime.now().timestamp())}"

    conversation = {
        "id": conversation_id,
        "client_user_id": user_id,
        "corretor_user_id": None,
        "property_id": property_id,
        "lead_id": payload.lead_id,
        "created_at": _now_str(),
        "updated_at": _now_str(),
        "status": "aberta"  # aberta, transferida, encerrada
    }

    db["chat_conversations"][conversation_id] = conversation
    db["chat_conversation_index"][key] = conversation
    db["chat_messages"].setdefault(conversation_id, [])

    return conversation


@router.get("/conversations", response_model=List[dict])
async def list_conversations(current_user_id: str = Depends(get_current_user_id)):
    db = get_memory_db()
    _ensure_tables(db)

    convs = [
        c for c in db["chat_conversations"].values()
        if c.get("client_user_id") == current_user_id
    ]
    convs.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return convs


@router.get("/conversations/{conversation_id}/messages", response_model=List[dict])
async def list_messages(conversation_id: str, current_user_id: str = Depends(get_current_user_id)):
    db = get_memory_db()
    _ensure_tables(db)

    conv = db["chat_conversations"].get(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")

    user = _get_user(db, current_user_id)
    if not user:
        raise HTTPException(status_code=403, detail="Acesso negado")

    role = user.get("tipo")

    if role == "corretor":
        # corretor pode ver se é o correto designado OU se a conversa ainda não foi designada
        if conv.get("corretor_user_id") not in (None, current_user_id):
            raise HTTPException(status_code=403, detail="Acesso negado")
    else:
        if conv.get("client_user_id") != current_user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")

    return db["chat_messages"].get(conversation_id, [])


@router.post("/conversations/{conversation_id}/messages", response_model=dict)
async def post_message(
    conversation_id: str,
    payload: ChatMessageCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    db = get_memory_db()
    _ensure_tables(db)

    conv = db["chat_conversations"].get(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")

    user = _get_user(db, current_user_id)
    if not user:
        raise HTTPException(status_code=403, detail="Acesso negado")

    # valida permissão básica
    if user.get("tipo") == "corretor":
        if conv.get("corretor_user_id") not in (None, current_user_id):
            raise HTTPException(status_code=403, detail="Acesso negado")
    else:
        if conv.get("client_user_id") != current_user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")

    msg = {
        "id": f"msg_{len(db['chat_messages'].get(conversation_id, [])) + 1}_{int(datetime.now().timestamp())}",
        "conversation_id": conversation_id,
        "sender_user_id": current_user_id,
        "sender_type": user.get("tipo"),
        "text": payload.text,
        "created_at": _now_str(),
    }

    db["chat_messages"][conversation_id].append(msg)

    conv["updated_at"] = _now_str()
    db["chat_conversations"][conversation_id] = conv

    return msg


@router.post("/conversations/{conversation_id}/action", response_model=dict)
async def chat_action(
    conversation_id: str,
    payload: ChatActionRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Ação do chat (MVP): decide redirecionamento e/ou transfere pro corretor."""
    db = get_memory_db()
    _ensure_tables(db)

    conv = db["chat_conversations"].get(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")

    user = _get_user(db, current_user_id)
    if not user:
        raise HTTPException(status_code=403, detail="Acesso negado")

    if user.get("tipo") != "cliente":
        raise HTTPException(status_code=403, detail="Somente cliente pode acionar ações")

    action = (payload.action or "").strip().lower()

    if action in ["catalogo", "other_property", "outro_imovel", "choose_other"]:
        return {"type": "redirect", "to": "/catalogo"}

    if action in ["transfer_visit", "prosseguir", "visita", "falar_responsavel", "responsavel"]:
        # escolhe corretor e marca conversa como transferida
        best = await _select_best_corretor_for_user(db)
        if not best:
            return {"type": "redirect", "to": "/leads"}

        conv["corretor_user_id"] = best["id"]
        conv["status"] = "transferida"
        conv["updated_at"] = _now_str()
        db["chat_conversations"][conversation_id] = conv

        # cria lead (ou reusa) no sistema de leads para manter histórico/transfer
        # Se houver lead_id, atualiza corretor no lead.
        if conv.get("lead_id"):
            lead = db["leads"].get(conv["lead_id"])
            if lead:
                lead["corretor_id"] = best["id"]
                lead["data_contato"] = lead.get("data_contato") or _now_str()
                db["leads"][lead["id"]] = lead

        return {
            "type": "redirect",
            "to": f"/leads?chat_corretor_id={best['id']}",
            "corretor": {"id": best["id"], "name": best.get("name")}
        }

    raise HTTPException(status_code=400, detail="Ação inválida")


@router.get("/corretores/queue", response_model=List[dict])
async def corretor_queue(current_user_id: str = Depends(get_current_user_id)):
    """Fila do corretor: retorna conversas pendentes (corretor_user_id é None).
    Ordena priorizando ranking (conversas mais recentes + melhor score aproximado).
    """
    db = get_memory_db()
    _ensure_tables(db)

    user = _get_user(db, current_user_id)
    if not user or user.get("tipo") != "corretor":
        raise HTTPException(status_code=403, detail="Somente corretor")

    convs = [
        c for c in db["chat_conversations"].values()
        if c.get("corretor_user_id") in (None, "") and c.get("status") == "aberta"
    ]

    convs.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    # MVP: fila simples (sem transfer por corretor ranking por conversa individual)
    return convs[:20]

