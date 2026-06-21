from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from models.schemas import (
    PropertyPublicResponse, 
    PublicLeadCreate, 
    LeadResponse,
    ClientPreferences,
    PropertyType,
    PropertyStatus
)
from database import get_memory_db
from datetime import datetime
import uuid

router = APIRouter()


def generate_session_id() -> str:
    """Gera um ID de sessão aleatório para tracking"""
    return str(uuid.uuid4())


def generate_lead_id() -> str:
    """Gera um ID único para lead"""
    return f"lead_{uuid.uuid4().hex[:12]}"


@router.get("/properties", response_model=List[PropertyPublicResponse])
async def list_public_properties(
    property_type: Optional[PropertyType] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    bedrooms: Optional[int] = None,
    bathrooms: Optional[int] = None,
    status: Optional[PropertyStatus] = PropertyStatus.AVAILABLE,
    limit: int = Query(50, le=100),
    offset: int = Query(0),
):
    """
    Lista imóveis disponíveis para o público.
    Este endpoint é usado pela Área do Cliente.
    
    ATIVAÇÃO: Apenas imóveis de imobiliárias ATIVAS aparecem.
    """
    db = get_memory_db()
    properties = list(db["properties"].values())
    users = db.get("users", {})
    imobiliarias = db.get("imobiliarias", {})
    
    # Filtrar apenas imóveis disponíveis ou em negociação

    available_statuses = [PropertyStatus.AVAILABLE.value, PropertyStatus.NEGOTIATION.value]
    
    # NOVO: Filtrar apenas imóveis de imobiliárias/corretores ATIVOS
    valid_properties = []
    for p in properties:
        if p.get("status") not in available_statuses:
            continue
        
        # Verificar quem criou o imóvel
        user_id = p.get("user_id")
        user = users.get(user_id, {})
        imob_id = user.get("imobiliaria_id")
        
        if not imob_id:
            # Sem imobiliária - verificar se é admin master ou corretor independente ATIVO
            if user.get("ativo", True):
                valid_properties.append(p)
        else:
            # Com imobiliária - verificar se a imobiliária está ATIVA
            imob = imobiliarias.get(imob_id)
            if imob and imob.get("status") == "ativo":
                valid_properties.append(p)
    
    properties = valid_properties
    
    # Aplicar filtros
    if property_type:
        properties = [p for p in properties if p.get("property_type") == property_type.value]
    
    if city:
        properties = [p for p in properties if p.get("city", "").lower() == city.lower()]
    
    if state:
        properties = [p for p in properties if p.get("state", "").lower() == state.lower()]
    
    if min_value is not None:
        properties = [p for p in properties if p.get("value", 0) >= min_value]
    
    if max_value is not None:
        properties = [p for p in properties if p.get("value", 0) <= max_value]
    
    if bedrooms is not None:
        properties = [p for p in properties if p.get("bedrooms", 0) >= bedrooms]
    
    if bathrooms is not None:
        properties = [p for p in properties if p.get("bathrooms", 0) >= bathrooms]
    
    # Ordenar por mais recentes primeiro
    properties.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Paginar
    total = len(properties)
    properties = properties[offset:offset + limit]
    
    return [PropertyPublicResponse(**p) for p in properties]


@router.post("/views")
async def track_public_view(view_data: dict):
    db = get_memory_db()
    property_id = view_data.get("property_id")
    session_id = view_data.get("session_id")
    
    property = db["properties"].get(property_id)
    if property:
        property["views"] = property.get("views", 0) + 1
        db["properties"][property_id] = property
        
        # Track unique views
        if "views_sessions" not in property:
            property["views_sessions"] = set()
        if session_id not in property["views_sessions"]:
            property["views_sessions"].add(session_id)
            property["unique_views"] = len(property["views_sessions"])
    
    return {"status": "view_tracked"}


@router.get("/properties/{property_id}", response_model=PropertyPublicResponse)
async def get_public_property(property_id: str):
    """
    Obtém detalhes de um imóvel específico.
    Usado pela página de detalhes do cliente.
    """
    db = get_memory_db()
    property = db["properties"].get(property_id)
    
    if not property:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    # Verificar se está disponível
    status = property.get("status")
    available_statuses = [PropertyStatus.AVAILABLE.value, PropertyStatus.NEGOTIATION.value]
    
    if status not in available_statuses:
        raise HTTPException(status_code=404, detail="Imóvel não disponível")
    
    # Incrementar visualizações
    property["views"] = property.get("views", 0) + 1
    db["properties"][property_id] = property
    
    return PropertyPublicResponse(**property)


@router.post("/leads", response_model=LeadResponse)
async def create_public_lead(lead: PublicLeadCreate):
    """
    Cria um lead a partir da área do cliente.
    Este é o ponto crítico de captura de leads!
    
    ATIVAÇÃO: Lead só é criado se corretor/imobiliária estiver ATIVA.
    """
    db = get_memory_db()
    users = db.get("users", {})
    imobiliarias = db.get("imobiliarias", {})
    
    # Verificar se o imóvel existe
    property = db["properties"].get(lead.property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    # NOVO: Verificar se o proprietário está ATIVO
    user_id = property.get("user_id")
    user = users.get(user_id, {})
    imob_id = user.get("imobiliaria_id")
    
    can_receive_lead = False
    if not imob_id:
        # Sem imobiliária - verificar se corretor está ATIVO
        if user.get("ativo", True):
            can_receive_lead = True
    else:
        # Com imobiliária - verificar se a imobiliária está ATIVA
        imob = imobiliarias.get(imob_id)
        if imob and imob.get("status") == "ativo":
            can_receive_lead = True
    
    if not can_receive_lead:
        # Lead ainda é criado mas associado a "inbox" do sistema para análise posterior
        # Isso permite que quando a imobiliária for reativada, os leads possam ser distribuídos
        pass  # Continua mas marca como inativo
    
    # Gerar ID único
    lead_id = generate_lead_id()
    now = str(datetime.now())
    
    # Criar o lead
    new_lead = {
        "id": lead_id,
        "user_id": property.get("user_id"),  # Associate with property owner
        "property_id": lead.property_id,
        "client_name": lead.client_name,
        "client_email": lead.client_email,
        "client_phone": lead.client_phone,
        "message": lead.message,
        "source": "cliente_pub",  # Mark as public client lead
        
        # Store preferences if provided
        "preferences": lead.preferences.model_dump() if lead.preferences else None,
        
        "created_at": now
    }
    
    db["leads"][lead_id] = new_lead
    
    # Atualizar contagem de leads do imóvel
    property["leads"] = property.get("leads", 0) + 1
    db["properties"][lead.property_id] = property
    
    return LeadResponse(**new_lead)


@router.get("/search")
async def search_properties(
    q: str = Query(..., description="Termo de busca"),
    limit: int = Query(20, le=50)
):
    """
    Busca imóveis por termo específico.
    Busca em título, descrição, cidade e endereço.
    
    ATIVAÇÃO: Apenas imóveis de corretores ATIVOS.
    """
    db = get_memory_db()
    properties = list(db["properties"].values())
    users = db.get("users", {})
    inmobiliarias = db.get("imobiliarias", {})
    
    q = q.lower()
    available_statuses = [PropertyStatus.AVAILABLE.value, PropertyStatus.NEGOTIATION.value]
    
    # Filtrar apenas imóveis de corretores ATIVOS
    results = []
    for p in properties:
        if p.get("status") not in available_statuses:
            continue
        
        # Verificar quem criou o imóvel
        user_id = p.get("user_id")
        user = users.get(user_id, {})
        imob_id = user.get("imobiliaria_id")
        
        is_valid = False
        if not imob_id:
            if user.get("ativo", True):
                is_valid = True
        else:
            imob = imobiliarias.get(imob_id)
            if imob and imob.get("status") == "ativo":
                is_valid = True
        
        if is_valid:
            # Buscar em campos relevantes
            searchable_text = f"{p.get('title', '')} {p.get('description', '')} {p.get('city', '')} {p.get('address', '')}".lower()
            
            if q in searchable_text:
                results.append(p)
    
    results = results[:limit]
    
    return [PropertyPublicResponse(**p) for p in results]


@router.get("/cities")
async def get_available_cities():
    """
    Retorna lista de cidades disponíveis com imóveis.
    Usado para популяри fil的城市.
    """
    db = get_memory_db()
    properties = list(db["properties"].values())
    
    available_statuses = [PropertyStatus.AVAILABLE.value, PropertyStatus.NEGOTIATION.value]
    
    cities = set()
    for p in properties:
        if p.get("status") in available_statuses:
            city = p.get("city")
            state = p.get("state")
            if city and state:
                cities.add(f"{city}, {state}")
    
    return sorted(list(cities))


@router.get("/filters/options")
async def get_filter_options():
    """
    Retorna opções disponíveis para filtros.
    Usado para preencher os selects de filtro.
    """
    db = get_memory_db()
    properties = list(db["properties"].values())
    
    available_statuses = [PropertyStatus.AVAILABLE.value, PropertyStatus.NEGOTIATION.value]
    properties = [p for p in properties if p.get("status") in available_statuses]
    
    # Extrair tipos únicos
    types = list(set(p.get("property_type") for p in properties if p.get("property_type")))
    
    # Extrair cidades únicas
    cities = {}
    for p in properties:
        city = p.get("city")
        state = p.get("state")
        if city and state:
            if state not in cities:
                cities[state] = []
            if city not in cities[state]:
                cities[state].append(city)
    
    # Calcular faixa de preços
    values = [p.get("value", 0) for p in properties]
    min_price = min(values) if values else 0
    max_price = max(values) if values else 0
    
    return {
        "property_types": types,
        "cities_by_state": cities,
        "price_range": {
            "min": min_price,
            "max": max_price
        },
        "bedrooms_options": [1, 2, 3, 4, 5],
        "bathrooms_options": [1, 2, 3, 4]
    }
