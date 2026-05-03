"""
Middleware de Controle de Acesso RBAC (Role-Based Access Control)

Implementa controle de acesso baseado em papéis com Row Level Security:
- ADMIN_MASTER: Acesso total ao sistema
- ADMIN_IMOBILIARIA: Acesso restrito à própria imobiliária
- CORRETOR: Acesso restrito à imobiliária vinculada
- CLIENTE: Acesso limitado
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
from database import get_memory_db
from auth_utils import decode_access_token


class AccessControlMiddleware(BaseHTTPMiddleware):
    """Middleware para controle de acesso baseado em papéis (RBAC)"""

    # Rotas que não requerem autenticação
    PUBLIC_ROUTES = [
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/auth/login",
        "/auth/register",
        "/auth/verify-email",
        "/auth/resend-code",
        "/public",
        "/catalogo",
        "/imovel",
        "/preferencias",
        "/minhas-preferencias",
        "/perfil",
        "/criar-senha"
    ]

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Permitir rotas públicas
        path = request.url.path

        for public_route in self.PUBLIC_ROUTES:
            if path.startswith(public_route):
                return await call_next(request)

        # Verificar autenticação
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return self._unauthorized_response("Token de autenticação requerido")

        token = auth_header.replace("Bearer ", "")
        payload = decode_access_token(token)

        if not payload:
            return self._unauthorized_response("Token inválido")

        user_id = payload.get("sub")
        if not user_id:
            return self._unauthorized_response("Token malformado")

        # Verificar se usuário existe
        db = get_memory_db()
        user = db["users"].get(user_id)
        if not user:
            return self._unauthorized_response("Usuário não encontrado")

        # Verificar se usuário está ativo
        if not user.get("ativo", True):
            return self._unauthorized_response("Usuário inativo")

        # Adicionar informações do usuário à requisição
        request.state.user = {
            "user_id": user_id,
            "role": user.get("tipo", "cliente"),
            "imobiliaria_id": user.get("imobiliaria_id"),
            "email": user.get("email")
        }

        # Aplicar regras RBAC específicas por rota
        try:
            self._apply_rbac_rules(request)
        except HTTPException as e:
            return self._error_response(e.status_code, e.detail)

        return await call_next(request)

    def _apply_rbac_rules(self, request: Request):
        """Aplica regras RBAC específicas por rota"""
        path = request.url.path
        user_info = request.state.user
        role = user_info.get("role")

        # ADMIN_MASTER: acesso total
        if role == "admin_master":
            return

        # Rotas específicas por papel
        if path.startswith("/imobiliarias"):
            if role not in ["admin_master"]:
                raise HTTPException(status_code=403, detail="Acesso restrito ao administrador master")

        elif path.startswith("/corretores"):
            if role not in ["admin_master", "admin_imobiliaria"]:
                raise HTTPException(status_code=403, detail="Acesso restrito a administradores")

        elif path.startswith("/dashboard"):
            if role not in ["admin_master", "admin_imobiliaria", "corretor"]:
                raise HTTPException(status_code=403, detail="Acesso restrito a equipe imobiliária")

        elif path.startswith("/clients"):
            if role not in ["admin_master", "admin_imobiliaria", "corretor"]:
                raise HTTPException(status_code=403, detail="Acesso restrito a equipe imobiliária")

        elif path.startswith("/leads"):
            if role not in ["admin_master", "admin_imobiliaria", "corretor"]:
                raise HTTPException(status_code=403, detail="Acesso restrito a equipe imobiliária")

        elif path.startswith("/properties"):
            if role not in ["admin_master", "admin_imobiliaria", "corretor"]:
                raise HTTPException(status_code=403, detail="Acesso restrito a equipe imobiliária")

    def _unauthorized_response(self, message: str):
        """Retorna resposta de não autorizado"""
        return self._error_response(401, message)

    def _error_response(self, status_code: int, message: str):
        """Retorna resposta de erro"""
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=status_code,
            content={"detail": message}
        )


def get_current_user_from_request(request: Request):
    """Extrai informações do usuário da requisição"""
    return getattr(request.state, "user", None)


def apply_rbac_filter(query_params: dict, user_info: Optional[dict], table_name: str):
    """
    Aplica filtros RBAC automaticamente baseado no papel do usuário

    Args:
        query_params: Parâmetros da query
        user_info: Informações do usuário autenticado
        table_name: Nome da tabela para aplicar filtros

    Returns:
        dict: Filtros a serem aplicados
    """
    filters = {}

    if not user_info:
        # Usuário não autenticado - acesso limitado
        if table_name in ["properties", "clients", "leads"]:
            filters["public_only"] = True
        return filters

    role = user_info.get("role")
    imobiliaria_id = user_info.get("imobiliaria_id")

    # ADMIN_MASTER: acesso total, ignora filtros
    if role == "admin_master":
        return filters

    # ADMIN_IMOBILIARIA: acesso apenas à própria imobiliária
    elif role == "admin_imobiliaria":
        if imobiliaria_id:
            filters["imobiliaria_id"] = imobiliaria_id

    # CORRETOR: acesso apenas à imobiliária vinculada
    elif role == "corretor":
        if imobiliaria_id:
            filters["imobiliaria_id"] = imobiliaria_id

    # CLIENTE: acesso limitado (apenas dados públicos)
    elif role == "cliente":
        filters["public_only"] = True

    return filters


def check_resource_access(user_info: Optional[dict], resource_owner_id: Optional[str], resource_imobiliaria_id: Optional[str]) -> bool:
    """
    Verifica se o usuário tem acesso a um recurso específico

    Args:
        user_info: Informações do usuário
        resource_owner_id: ID do proprietário do recurso
        resource_imobiliaria_id: ID da imobiliária do recurso

    Returns:
        bool: True se tem acesso, False caso contrário
    """
    if not user_info:
        return False

    role = user_info.get("role")
    user_id = user_info.get("user_id")
    imobiliaria_id = user_info.get("imobiliaria_id")

    # ADMIN_MASTER: acesso total
    if role == "admin_master":
        return True

    # ADMIN_IMOBILIARIA: acesso à própria imobiliária
    elif role == "admin_imobiliaria":
        return imobiliaria_id == resource_imobiliaria_id

    # CORRETOR: acesso à imobiliária vinculada
    elif role == "corretor":
        return imobiliaria_id == resource_imobiliaria_id

    # CLIENTE: acesso limitado
    elif role == "cliente":
        # Clientes podem ver apenas recursos públicos ou próprios
        return resource_owner_id == user_id

    return False


def check_permission(user_id: str, permission: str) -> bool:
    """
    Função auxiliar para verificar permissões específicas.
    Útil para verificar no código das rotas.
    """
    db = get_memory_db()
    user = db["users"].get(user_id)
    
    if not user:
        return False
    
    user_tipo = user.get("tipo", "cliente")
    imob_id = user.get("_imobiliaria_id")
    
    # Cliente tem permissões limitadas
    if user_tipo == "cliente":
        return permission in ["view_catalog"]
    
    # Verificar status da imobiliária
    if imob_id:
        imob = db["imobiliarias"].get(imob_id)
        if imob:
            imob_status = imob.get("status")
            
            # Se inativo, retornar False para permissões de escrita
            if imob_status == "inativo":
                write_permissions = [
                    "create_property",
                    "edit_property",
                    "delete_property",
                    "publish_property",
                    "view_leads",
                    "view_metrics",
                    "manage_negotiations"
                ]
                if permission in write_permissions:
                    return False
    
    # Permissões baseado no tipo
    permissions_map = {
        "admin": [
            "view_catalog", "create_property", "edit_property", "delete_property",
            "publish_property", "view_leads", "view_metrics", "manage_negotiations",
            "manage_corretors", "manage_imobiliaria"
        ],
        "corretor": [
            "view_catalog", "create_property", "edit_property", "publish_property",
            "view_leads", "view_metrics", "manage_negotiations"
        ],
        "cliente": ["view_catalog"]
    }
    
    return permission in permissions_map.get(user_tipo, [])


def get_user_permissions(user_id: str) -> dict:
    """
    Retorna todas as permissões do usuário.
    """
    db = get_memory_db()
    user = db["users"].get(user_id)
    
    if not user:
        return {}
    
    user_tipo = user.get("tipo", "cliente")
    imob_id = user.get("imobiliaria_id")
    
    # Permissões base
    permissions = {
        "can_view_catalog": True,
        "can_create_properties": False,
        "can_edit_properties": False,
        "can_delete_properties": False,
        "can_publish_properties": False,
        "can_view_leads": False,
        "can_view_dashboard": False,
        "can_manage_negotiations": False,
        "can_manage_corretors": False,
        "can_manage_imobiliaria": False,
        "plan_status": "free"
    }
    
    # Se não tem imobiliária,return base para cliente
    if user_tipo == "cliente":
        return permissions
    
    # Verificar status da imobiliária
    if imob_id:
        imob = db["imobiliarias"].get(imob_id)
        if imob:
            imob_status = imob.get("status", "trial")
            permissions["plan_status"] = imob_status
            
            if imob_status == "ativo":
                if user_tipo == "admin":
                    permissions = {
                        "can_view_catalog": True,
                        "can_create_properties": True,
                        "can_edit_properties": True,
                        "can_delete_properties": True,
                        "can_publish_properties": True,
                        "can_view_leads": True,
                        "can_view_dashboard": True,
                        "can_manage_negotiations": True,
                        "can_manage_corretors": True,
                        "can_manage_imobiliaria": True,
                        "plan_status": imob.get("plano", "free")
                    }
                elif user_tipo == "corretor":
                    permissions = {
                        "can_view_catalog": True,
                        "can_create_properties": True,
                        "can_edit_properties": True,
                        "can_delete_properties": False,
                        "can_publish_properties": True,
                        "can_view_leads": True,
                        "can_view_dashboard": True,
                        "can_manage_negotiations": True,
                        "can_manage_corretors": False,
                        "can_manage_imobiliaria": False,
                        "plan_status": imob.get("plano", "free")
                    }
    
    return permissions
