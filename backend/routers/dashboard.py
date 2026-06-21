from fastapi import APIRouter, Depends, Header, HTTPException
from typing import Optional
from models.schemas import DashboardStats, LeadResponse, DashboardAdvancedStats, CorretorStats
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


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user_id: str = Depends(get_current_user_id)):
    db = get_memory_db()
    
    # Estatísticas de imóveis
    properties = [p for p in db["properties"].values() if p.get("user_id") == current_user_id]
    total_properties = len(properties)
    active_properties = len([p for p in properties if p.get("status") == "disponível"])
    sold_properties = len([p for p in properties if p.get("status") == "vendido"])
    
    # Imóveis em negociação
    in_negotiation_properties = len([p for p in properties if p.get("status") == "em_negociação"])
    
    # Estatísticas de clientes
    clients = [c for c in db["clients"].values() if c.get("user_id") == current_user_id]
    total_clients = len(clients)
    
    # Estatísticas de leads
    leads = [l for l in db["leads"].values() if l.get("user_id") == current_user_id]
    total_leads = len(leads)
    
    # Imóveis por tipo
    properties_by_type = {}
    for p in properties:
        ptype = p.get("property_type", "outros")
        properties_by_type[ptype] = properties_by_type.get(ptype, 0) + 1
    
    # Imóveis por cidade
    properties_by_city = {}
    for p in properties:
        city = p.get("city", "outros")
        properties_by_city[city] = properties_by_city.get(city, 0) + 1
    
    # Leads recentes
    recent_leads = sorted(leads, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
    
    return DashboardStats(
        total_properties=total_properties,
        active_properties=active_properties,
        sold_properties=sold_properties,
        total_clients=total_clients,
        total_leads=total_leads,
        properties_by_type=properties_by_type,
        properties_by_city=properties_by_city,
        recent_leads=[LeadResponse(**l) for l in recent_leads]
    )


@router.get("/stats/advanced", response_model=DashboardAdvancedStats)
async def get_advanced_stats(current_user_id: str = Depends(get_current_user_id)):
    """
    Estatísticas avançadas do dashboard com métricas de conversão.
    """
    db = get_memory_db()
    
    # Estatísticas de imóveis
    properties = [p for p in db["properties"].values() if p.get("user_id") == current_user_id]
    total_properties = len(properties)
    active_properties = len([p for p in properties if p.get("status") == "disponível"])
    sold_properties = len([p for p in properties if p.get("status") == "vendido"])
    
    in_negotiation_properties = len([p for p in properties if p.get("status") == "em_negociação"])
    
    # Estatísticas de clientes
    clients = [c for c in db["clients"].values() if c.get("user_id") == current_user_id]
    total_clients = len(clients)
    
    # Estatísticas de leads
    leads = [l for l in db["leads"].values() if l.get("user_id") == current_user_id]
    total_leads = len(leads)
    
    # Taxa de conversão (leads que resultaram em venda/aluguel)
    conversion_rate = 0.0
    if total_leads > 0:
        conversion_rate = (sold_properties / total_leads) * 100
    
    # Imóveis por tipo
    properties_by_type = {}
    for p in properties:
        ptype = p.get("property_type", "outros")
        properties_by_type[ptype] = properties_by_type.get(ptype, 0) + 1
    
    # Imóveis por cidade
    properties_by_city = {}
    for p in properties:
        city = p.get("city", "outros")
        properties_by_city[city] = properties_by_city.get(city, 0) + 1
    
    # Imóveis mais visualizados (top)
    top_properties = sorted(
        properties, 
        key=lambda x: x.get("views", 0), 
        reverse=True
    )[:5]
    top_properties = [
        {
            "id": p.get("id"),
            "title": p.get("title"),
            "views": p.get("views", 0),
            "clicks": p.get("clicks", 0),
            "leads": p.get("leads", 0)
        }
        for p in top_properties
    ]
    
    # Leads recentes
    recent_leads = sorted(leads, key=lambda x: x.get("created_at", ""), reverse=True)[:10]
    
    # Leads por fonte
    leads_by_source = {}
    for l in leads:
        source = l.get("source", "outros")
        leads_by_source[source] = leads_by_source.get(source, 0) + 1
    
    return DashboardAdvancedStats(
        total_properties=total_properties,
        active_properties=active_properties,
        sold_properties=sold_properties,
        in_negotiation_properties=in_negotiation_properties,
        total_clients=total_clients,
        total_leads=total_leads,
        conversion_rate=round(conversion_rate, 2),
        properties_by_type=properties_by_type,
        properties_by_city=properties_by_city,
        top_properties=top_properties,
        recent_leads=[LeadResponse(**l) for l in recent_leads],
        leads_by_source=leads_by_source
    )


@router.get("/corretores", response_model=list)
async def list_corretores(current_user_id: str = Depends(get_current_user_id)):
    """
    Lista corretores relacionados ao usuário atual.
    """
    db = get_memory_db()
    
    # Buscar usuários que são corretores
    users = db["users"]
    corretores = [
        {
            "id": user_id,
            "name": user.get("name"),
            "email": user.get("email"),
            "ativo": user.get("ativo", True),
            "created_at": user.get("created_at")
        }
        for user_id, user in users.items()
        if user.get("tipo") == "corretor"
    ]
    
    return corretores


@router.get("/corretores/{corretor_id}/stats", response_model=CorretorStats)
async def get_corretor_stats(
    corretor_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Estatísticas detalhadas de um corretor específico.
    """
    db = get_memory_db()
    
    # Verificar se corretor existe
    corretor = db["users"].get(corretor_id)
    if not corretor or corretor.get("tipo") != "corretor":
        raise HTTPException(status_code=404, detail="Corretor não encontrado")
    
    # Estatísticas de imóveis do corretor
    properties = [p for p in db["properties"].values() if p.get("user_id") == corretor_id]
    total_properties = len(properties)
    active_properties = len([p for p in properties if p.get("status") == "disponível"])
    sold_properties = len([p for p in properties if p.get("status") == "vendido"])
    in_negotiation = len([p for p in properties if p.get("status") == "em_negociação"])
    
    
    # Total de visualizações e cliques nos imóveis do corretor
    total_views = sum(p.get("views", 0) for p in properties)
    total_clicks = sum(p.get("clicks", 0) for p in properties)
    
    # Estatísticas de leads do corretor
    leads = [l for l in db["leads"].values() if l.get("user_id") == corretor_id]
    total_leads = len(leads)
    
    # Leads por status
    leads_Novo = len([l for l in leads if l.get("status") == "novo"])
    leads_Contacto = len([l for l in leads if l.get("status") == "em_contacto"])
    leads_Qualificado = len([l for l in leads if l.get("status") == "qualificado"])
    leads_Convertido = len([l for l in leads if l.get("status") == "convertido"])
    
    # Taxa de conversão
    conversion_rate = 0.0
    if total_leads > 0:
        conversion_rate = (sold_properties / total_leads) * 100
    
# Imóveis mais visualizados do corretor
    top_properties = sorted(
        properties, 
        key=lambda x: x.get("views", 0), 
        reverse=True
    )[:5]
    
    return CorretorStats(
        corretor_id=corretor_id,
        corretor_name=corretor.get("name"),
        corretor_email=corretor.get("email"),
        total_properties=total_properties,
        active_properties=active_properties,
        sold_properties=sold_properties,
        in_negotiation=in_negotiation,
        total_views=total_views,
        total_clicks=total_clicks,
        total_leads=total_leads,
        leads_novo=leads_Novo,
        leads_em_contacto=leads_Contacto,
        leads_qualificado=leads_Qualificado,
        leads_convertido=leads_Convertido,
        conversion_rate=round(conversion_rate, 2),
        top_properties=[
            {
                "id": p.get("id"),
                "title": p.get("title"),
                "views": p.get("views", 0),
                "clicks": p.get("clicks", 0),
                "status": p.get("status")
            }
            for p in top_properties
        ]
    )


@router.get("/corretores/ranking")
async def get_corretores_ranking(
    current_user_id: str = Depends(get_current_user_id),
    metric: str = "leads",
    limit: int = 10
):
    """
    Ranking de corretores por performance.
    
    Métricas disponíveis:
    - leads: total de leads recebidos
    - conversion: taxa de conversão
    - views: total de visualizações
    - properties: total de imóveis
    """
    db = get_memory_db()
    users = db["users"]
    properties_db = db["properties"]
    leads_db = db["leads"]
    
    # Buscar todos os corretores
    corretores = [
        {
            "id": user_id,
            "name": user.get("name"),
            "email": user.get("email"),
            "ativo": user.get("ativo", True)
        }
        for user_id, user in users.items()
        if user.get("tipo") == "corretor" and user.get("ativo", True)
    ]
    
    # Calcular métricas para cada corretor
    ranking = []
    for corretor in corretores:
        corretor_id = corretor["id"]
        
        # Estatísticas
        properties = [p for p in properties_db.values() if p.get("user_id") == corretor_id]
        leads = [l for l in leads_db.values() if l.get("user_id") == corretor_id]
        
        total_properties = len(properties)
        total_leads = len(leads)
        total_views = sum(p.get("views", 0) for p in properties)
        sold = len([p for p in properties if p.get("status") == "vendido"])
        
        # Taxa de conversão
        conversion_rate = 0.0
        if total_leads > 0:
            conversion_rate = round((sold / total_leads) * 100, 2)
        
        ranking.append({
            "id": corretor_id,
            "name": corretor["name"],
            "email": corretor["email"],
            "total_properties": total_properties,
            "total_leads": total_leads,
            "total_views": total_views,
            "sold_properties": sold,
            "conversion_rate": conversion_rate
        })
    
    # Ordenar por métrica selecionada
    if metric == "leads":
        ranking.sort(key=lambda x: x["total_leads"], reverse=True)
    elif metric == "conversion":
        ranking.sort(key=lambda x: x["conversion_rate"], reverse=True)
    elif metric == "views":
        ranking.sort(key=lambda x: x["total_views"], reverse=True)
    elif metric == "properties":
        ranking.sort(key=lambda x: x["total_properties"], reverse=True)
    
    return ranking[:limit]
