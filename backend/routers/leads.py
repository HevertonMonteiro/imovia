from fastapi import APIRouter, HTTPException, Depends, Query, Header
from typing import Optional, List
from models.schemas import LeadCreate, LeadResponse, LeadWithIntelligence, LeadUpdate, LeadStatus, LeadTransferRequest
from auth_utils import generate_lead_id, decode_access_token
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


def calculate_interest_score(lead, property_data) -> int:
    """
    Calcula score de interesse do lead (0-10).
    
    Fatores:
    - Tem email (sim = +1)
    - Tem mensagem detalhada (sim = +2)
    - Já visitou o imóvel (views > 0 = +2)
    - Fonte quente (whatsapp, indicate = +2)
    - Tipo de imóvel combina = +1
    """
    score = 0
    
    # Tem email
    if lead.get("client_email"):
        score += 1
    
    # Tem mensagem (indica interesse maior)
    if lead.get("message") and len(lead.get("message", "")) > 20:
        score += 2
    
    # Já visualizou o imóvel
    if property_data and property_data.get("views", 0) > 0:
        score += 2
    
    # Fonte quente
    source = lead.get("source", "")
    if source in ["whatsapp", "indication", "referral"]:
        score += 2
    elif source == "website":
        score += 1
    
    return min(score, 10)


@router.get("", response_model=List[LeadResponse])
async def list_leads(
    current_user_id: str = Depends(get_current_user_id),
    property_id: Optional[str] = None,
    corretor_id: Optional[str] = None,
    status_contato: Optional[str] = None,
    limit: int = Query(50, le=100),
    offset: int = 0
):
    db = get_memory_db()
    leads = list(db["leads"].values())
    
    # Filtrar por usuário/imobiliaria
    leads = [l for l in leads if l.get("user_id") == current_user_id]
    
    # Filtrar por imóvel
    if property_id:
        leads = [l for l in leads if l.get("imovel_id") == property_id]
    
    # Filtrar por corretor
    if corretor_id:
        leads = [l for l in leads if l.get("corretor_id") == corretor_id]
    
    # Filtrar por status
    if status_contato:
        leads = [l for l in leads if l.get("status_contato") == status_contato]
    
    # Ordenar por data contato > data criacao
    leads.sort(key=lambda x: x.get("data_contato") or x.get("data_criacao", ""), reverse=True)
    
    # Paginar
    leads = leads[offset:offset + limit]
    
    return [LeadResponse.model_validate(l) for l in leads]


@router.get("/inteligente", response_model=List[LeadWithIntelligence])
async def list_leads_with_intelligence(
    current_user_id: str = Depends(get_current_user_id),
    property_id: Optional[str] = None,
    limit: int = Query(50, le=100),
    offset: int = 0
):
    """
    Lista leads com dados de inteligência (score de interesse, histórico, etc).
    """
    db = get_memory_db()
    leads = list(db["leads"].values())
    properties = db["properties"]
    
    # Filtrar por usuário
    leads = [l for l in leads if l.get("user_id") == current_user_id]
    
    # Filtrar por imóvel
    if property_id:
        leads = [l for l in leads if l.get("property_id") == property_id]
    
    # Adicionar dados de inteligência
    intelligent_leads = []
    for lead in leads:
        property_data = properties.get(lead.get("property_id"))
        
        # Calcular score de interesse
        interest_score = calculate_interest_score(lead, property_data)
        
        # Contar visualizações do imóvel
        views_count = property_data.get("views", 0) if property_data else 0
        
        # Criar resposta com inteligência
        intelligent_lead = {
            **lead,
            "interest_score": interest_score,
            "views_count": views_count,
            "preferences": lead.get("preferences"),
            "properties_viewed": lead.get("properties_viewed", [])
        }
        intelligent_leads.append(intelligent_lead)
    
    # Ordenar por score (mais interessados primeiro)
    intelligent_leads.sort(key=lambda x: x.get("interest_score", 0), reverse=True)
    
    # Paginar
    intelligent_leads = intelligent_leads[offset:offset + limit]
    
    return [LeadWithIntelligence(**l) for l in intelligent_leads]


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: str, current_user_id: str = Depends(get_current_user_id)):
    db = get_memory_db()
    lead = db["leads"].get(lead_id)
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    
    if lead.get("user_id") != current_user_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return LeadResponse(**lead)


@router.get("/{lead_id}/inteligente")
async def get_lead_intelligence(
    lead_id: str, 
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Obtém dados de inteligência de um lead específico.
    """
    db = get_memory_db()
    lead = db["leads"].get(lead_id)
    properties = db["properties"]
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    
    if lead.get("user_id") != current_user_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    property_data = properties.get(lead.get("property_id"))
    interest_score = calculate_interest_score(lead, property_data)
    
    return {
        "lead": lead,
        "property": property_data,
        "interest_score": interest_score,
        "score_label": get_score_label(interest_score)
    }


def get_score_label(score: int) -> str:
    """Retorna label do score de interesse."""
    if score <= 2:
        return "Frio"
    elif score <= 5:
        return "Morno"
    elif score <= 7:
        return "Quente"
    else:
        return "Muito Quente"


@router.post("", response_model=LeadResponse)
async def create_lead(
    lead: LeadCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    db = get_memory_db()
    imobiliaria_id = None
    
    # Buscar imobiliaria do user atual
    for user in db["users"].values():
        if user["id"] == current_user_id:
            imobiliaria_id = user.get("imobiliaria_id")
            break
    
    if not imobiliaria_id:
        imobiliaria_id = "default_imobiliaria"  # fallback
    
    lead_id = generate_lead_id()
    now = str(datetime.now())
    
    new_lead = {
        "id": lead_id,
        "user_id": current_user_id,
        "cliente_id": lead.client_id,
        "imovel_id": lead.property_id,
        "corretor_id": lead.corretor_id,
        "imobiliaria_id": imobiliaria_id,
        "client_name": lead.client_name,
        "client_email": lead.client_email,
        "client_phone": lead.client_phone,
        "message": lead.message,
        "source": lead.source,
        "status_contato": lead.status_contato,
        "data_criacao": now,
        "data_contato": None
    }
    
    db["leads"][lead_id] = new_lead
    
    # Atualizar contagem de leads do imóvel
    property = db["properties"].get(lead.property_id)
    if property:
        property["leads"] = property.get("leads", 0) + 1
        db["properties"][lead.property_id] = property
    
    return LeadResponse(**new_lead)


@router.post("/{lead_id}/contato")
async def marcar_contactado(
    lead_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Marca lead como contactado"""
    db = get_memory_db()
    lead = db["leads"].get(lead_id)
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    
    if lead.get("user_id") != current_user_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    lead["status_contato"] = LeadStatus.CONTACTADO
    lead["data_contato"] = str(datetime.now())
    
    db["leads"][lead_id] = lead
    return {"message": "Lead marcado como contactado", "lead": LeadResponse(**lead)}


@router.post("/{lead_id}/transferir")
async def transferir_lead(
    lead_id: str,
    request: LeadTransferRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Transfere lead para corretor"""
    db = get_memory_db()
    lead = db["leads"].get(lead_id)
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    
    if lead.get("user_id") != current_user_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Verificar se corretor existe e pertence à imobiliária
    corretor = db["users"].get(request.corretor_id)
    if not corretor or corretor.get("tipo") != "corretor":
        raise HTTPException(status_code=404, detail="Corretor não encontrado")
    
    if corretor.get("imobiliaria_id") != lead.get("imobiliaria_id"):
        raise HTTPException(status_code=400, detail="Corretor não pertence à sua imobiliária")
    
    lead["corretor_id"] = request.corretor_id
    db["leads"][lead_id] = lead
    
    return {"message": f"Lead transferido para {corretor.get('name', 'Corretor')}", "lead": LeadResponse(**lead)}


@router.delete("/{lead_id}")
async def delete_lead(lead_id: str, current_user_id: str = Depends(get_current_user_id)):
    db = get_memory_db()
    lead = db["leads"].get(lead_id)
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    
    if lead.get("user_id") != current_user_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    del db["leads"][lead_id]
    
    return {"message": "Lead deletado com sucesso"}
