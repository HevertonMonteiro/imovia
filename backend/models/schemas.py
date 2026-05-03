from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ===== ENUMS =====

class UserRole(str, Enum):
    """Roles de usuário no sistema"""
    ADMIN_MASTER = "admin_master"        # Administrador master (plataforma)
    ADMIN_IMOBILIARIA = "admin_imobiliaria"  # Administrador da imobiliária
    CORRETOR = "corretor"              # Corretor de imóveis
    CLIENTE = "cliente"              # Cliente final


class ImobiliáriaStatus(str, Enum):
    """Status da imobiliária (para sistema SaaS)"""
    ATIVO = "ativo"
    INATIVO = "inativo"
    TRIAL = "trial"


class Plano(str, Enum):
    """Planos disponíveis"""
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class PropertyType(str, Enum):
    APARTMENT = "apartamento"
    HOUSE = "casa"
    COMMERCIAL = "comercial"
    LAND = "terreno"
    OFFICE = "escritório"
    GARAGE = "garagem"



class TipoNegocio(str, Enum):
    """Tipo de negócio do imóvel"""
    VENDA = "venda"
    ALUGUEL = "aluguel"

class PropertyStatus(str, Enum):
    AVAILABLE = "disponível"
    RESERVED = "reservado"
    SOLD = "vendido"
    RENTED = "alugado"
    NEGOTIATION = "em_negociação"



class GoalType(str, Enum):
    """Objetivo do cliente (comprar ou alugar)"""
    BUY = "comprar"
    RENT = "alugar"


class UserBase(BaseModel):
    email: str
    name: str


class UserCreate(UserBase):
    password: str
    tipo: UserRole = UserRole.CLIENTE  # Tipo padrão


class UserResponse(UserBase):
    id: str
    tipo: UserRole = UserRole.CLIENTE
    imobiliaria_id: Optional[str] = None
    phone: Optional[str] = None
    ativo: bool = True
    password_set: bool = False  # True quando o usuário definiu sua senha via convite
    created_at: datetime

    class Config:
        from_attributes = True


# ===== MODELO IMOBILIÁRIA (SaaS) =====

class ImobiliáriaBase(BaseModel):
    nome: str
    email: str


class ImobiliáriaCreate(ImobiliáriaBase):
    pass


class ImobiliáriaUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    status: Optional[ImobiliáriaStatus] = None
    plano: Optional[Plano] = None
    data_pagamento: Optional[datetime] = None


class ImobiliáriaResponse(ImobiliáriaBase):
    id: str
    status: ImobiliáriaStatus = ImobiliáriaStatus.TRIAL
    plano: Plano = Plano.FREE
    data_pagamento: Optional[datetime] = None
    trial_termino: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True



class PropertyBase(BaseModel):
    title: str
    description: str
    property_type: PropertyType
    tipo_negocio: TipoNegocio = TipoNegocio.VENDA
    value: float
    address: str
    city: str
    state: str
    bedrooms: Optional[int] = 0
    bathrooms: Optional[int] = 0
    area: Optional[float] = 0
    garage_spaces: Optional[int] = 0
    status: PropertyStatus = PropertyStatus.AVAILABLE




class PropertyCreate(PropertyBase):
    pass

class FavoriteCreate(BaseModel):
    """Criar favorito"""
    property_id: str

class FavoriteResponse(BaseModel):
    """Resposta de favorito"""
    id: str
    user_id: str
    property_id: str
    property_title: str
    created_at: datetime

    class Config:
        from_attributes = True



class PropertyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    property_type: Optional[PropertyType] = None
    value: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area: Optional[float] = None
    garage_spaces: Optional[int] = None
    status: Optional[PropertyStatus] = None


class PropertyResponse(PropertyBase):
    id: str
    user_id: str
    images: List[str] = []
    ai_title: Optional[str] = None
    ai_description: Optional[str] = None
    ai_highlights: List[str] = []
    image_analysis: Optional[dict] = None
    views: int = 0
    clicks: int = 0
    leads: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClientBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: str
    interest: Optional[str] = None
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientResponse(ClientBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class LeadStatus(str, Enum):
    PENDENTE = "pendente"
    CONTACTADO = "contactado"

class LeadBase(BaseModel):
    property_id: str
    client_id: Optional[str] = None
    corretor_id: Optional[str] = None
    imobiliaria_id: str
    client_name: str
    client_email: Optional[str] = None
    client_phone: str
    message: Optional[str] = None
    source: Optional[str] = "website"
    status_contato: LeadStatus = LeadStatus.PENDENTE


class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    status_contato: Optional[LeadStatus] = None
    data_contato: Optional[str] = None
    corretor_id: Optional[str] = None

class LeadTransferRequest(BaseModel):
    corretor_id: str

class LeadResponse(LeadBase):
    id: str
    user_id: str
    data_criacao: str
    data_contato: Optional[str] = None
    cliente_id: Optional[str] = None

    class Config:
        from_attributes = True


class LeadResponse(LeadBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class DashboardStats(BaseModel):
    total_properties: int
    active_properties: int
    sold_properties: int
    total_clients: int
    total_leads: int
    properties_by_type: dict
    properties_by_city: dict
    recent_leads: List[LeadResponse] = []


class AIAnalysisResponse(BaseModel):
    environments: List[dict]
    lighting_score: int
    quality_score: int
    issues: List[str]
    suggestions: List[str]


class AIAdResponse(BaseModel):
    title: str
    description: str
    highlights: List[str]
    tags: List[str]


class ImageImproveResponse(BaseModel):
    original_url: str
    improved_url: str
    improvements: List[str]


# ===== NOVOS MODELOS - ÁREA DO CLIENTE =====

class ClientPreferences(BaseModel):
    """Preferências do cliente para recomendação"""
    property_type: Optional[PropertyType] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    city: Optional[str] = None
    state: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    min_area: Optional[float] = None
    max_area: Optional[float] = None
    goal: GoalType = GoalType.BUY  # comprar ou alugar


class ClientPreferencesUpdate(BaseModel):
    """Atualização de preferências do cliente"""
    property_type: Optional[PropertyType] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    city: Optional[str] = None
    state: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    min_area: Optional[float] = None
    max_area: Optional[float] = None
    goal: Optional[GoalType] = None


class ClientWithPreferences(BaseModel):
    """Cliente com preferências salvas"""
    id: str
    user_id: str
    name: str
    email: Optional[str] = None
    phone: str
    interest: Optional[str] = None
    notes: Optional[str] = None
    preferences: Optional[ClientPreferences] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PropertyView(BaseModel):
    """Registro de visualização de imóvel"""
    id: str
    session_id: str  # Identificador anônimo da sessão
    property_id: str
    viewed_at: datetime


class Interaction(BaseModel):
    """Interação do cliente com imóveis"""
    id: str
    session_id: str
    property_id: str
    type: str  # "view", "click", "favorite", "interest"
    created_at: datetime


class LeadWithIntelligence(BaseModel):
    """Lead com dados inteligentes"""
    id: str
    user_id: str
    property_id: str
    client_name: str
    client_email: Optional[str] = None
    client_phone: str
    message: Optional[str] = None
    source: str
    
    # Dados de inteligência
    preferences: Optional[ClientPreferences] = None
    properties_viewed: List[str] = []  # IDs dos imóveis visualizados
    views_count: int = 0
    interest_score: int = 0  # 0-10
    
    created_at: datetime

    class Config:
        from_attributes = True


class PropertyPublicResponse(BaseModel):
    """Resposta pública de imóvel (sem dados internos)"""
    id: str
    title: str
    description: Optional[str] = ""
    property_type: PropertyType
    value: float
    address: Optional[str] = ""
    city: str
    state: Optional[str] = ""
    bedrooms: Optional[int] = 0
    bathrooms: Optional[int] = 0
    area: Optional[float] = 0
    garage_spaces: Optional[int] = 0
    status: PropertyStatus
    images: List[str] = []
    ai_title: Optional[str] = None
    ai_description: Optional[str] = None
    ai_highlights: List[str] = []
    views: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class PublicLeadCreate(BaseModel):
    """Criação de lead público (sem autenticação)"""
    property_id: str
    client_name: str
    client_email: str
    client_phone: str
    message: Optional[str] = None
    # Preferências do cliente
    preferences: Optional[ClientPreferences] = None


class CorretorStats(BaseModel):
    """Estatísticas detalhadas do corretor"""
    corretor_id: str
    corretor_name: Optional[str] = None
    corretor_email: Optional[str] = None
    total_properties: int
    active_properties: int
    sold_properties: int
    in_negotiation: int = 0
    total_views: int = 0
    total_clicks: int = 0
    total_leads: int
    leads_novo: int = 0
    leads_em_contacto: int = 0
    leads_qualificado: int = 0
    leads_convertido: int = 0
    conversion_rate: float
    top_properties: List[dict] = []


class DashboardAdvancedStats(BaseModel):
    """Estatísticas avançadas do dashboard"""
    total_properties: int
    active_properties: int
    sold_properties: int
    in_negotiation_properties: int
    total_clients: int
    total_leads: int
    conversion_rate: float
    properties_by_type: dict
    properties_by_city: dict
    top_properties: List[dict]  # Mais visualizados
    recent_leads: List[LeadResponse] = []
    leads_by_source: dict
