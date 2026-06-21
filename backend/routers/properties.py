from fastapi import APIRouter, HTTPException, Depends, Query, Header, Request
from typing import Optional, List
from models.schemas import PropertyCreate, PropertyUpdate, PropertyResponse, PropertyType, PropertyStatus
from auth_utils import generate_property_id, decode_access_token
from database import get_memory_db
from middleware import get_current_user_from_request, apply_rbac_filter
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


@router.get("", response_model=List[PropertyResponse])
async def list_properties(
    request: Request,
    property_type: Optional[PropertyType] = None,
    status: Optional[PropertyStatus] = None,
    city: Optional[str] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    limit: int = Query(50, le=100),
    offset: int = 0
):
    db = get_memory_db()
    user_info = get_current_user_from_request(request)
    properties = list(db["properties"].values())

    # Aplicar filtros RBAC
    rbac_filters = apply_rbac_filter({}, user_info, "properties")

    if rbac_filters.get("imobiliaria_id"):
        properties = [p for p in properties if p.get("imobiliaria_id") == rbac_filters["imobiliaria_id"]]
    elif rbac_filters.get("public_only"):
        properties = properties

    # Aplicar filtros adicionais
    if property_type:
        properties = [p for p in properties if p.get("property_type") == property_type.value]
    if status:
        properties = [p for p in properties if p.get("status") == status.value]
    if city:
        properties = [p for p in properties if city.lower() in p.get("city", "").lower()]
    if min_value is not None:
        properties = [p for p in properties if p.get("value", 0) >= min_value]
    if max_value is not None:
        properties = [p for p in properties if p.get("value", 0) <= max_value]

    # Enriquecer com nome do corretor para admin_imobiliaria
    if user_info and user_info.get('role') == 'admin_imobiliaria':
        users = db["users"]
        for p in properties:
            user_id = p.get('user_id')
            if user_id:
                user = users.get(user_id)
                p['corretor_nome'] = user.get('name', 'Corretor') if user else 'Corretor'

    # Ordenar por data
    properties.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    # Paginar
    properties = properties[offset:offset + limit]

    # Garantir campos obrigatórios do schema (evita ValidationError quando seed/DB
    # não popula description/address/state)
    normalized = []
    for p in properties:
        p = dict(p)
        if "description" not in p or p.get("description") is None:
            p["description"] = ""
        if "address" not in p or p.get("address") is None:
            p["address"] = ""
        if "state" not in p or p.get("state") is None:
            p["state"] = ""
        normalized.append(p)

    return [PropertyResponse(**p) for p in normalized]



@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: str, request: Request):
    db = get_memory_db()
    user_info = get_current_user_from_request(request)
    property = db["properties"].get(property_id)

    if not property:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")

    # Verificar acesso RBAC
    from middleware import check_resource_access
    if not check_resource_access(user_info, property.get("user_id"), property.get("imobiliaria_id")):
        raise HTTPException(status_code=403, detail="Acesso negado")

    return PropertyResponse(**property)


@router.post("", response_model=PropertyResponse)
async def create_property(
    property: PropertyCreate,
    request: Request
):
    db = get_memory_db()
    user_info = get_current_user_from_request(request) or {}
    user_id = user_info.get("user_id")
    imobiliaria_id = user_info.get("imobiliaria_id")

    property_id = generate_property_id()
    now = str(datetime.now())

    new_property = {
        "id": property_id,
        "user_id": user_id,
        "imobiliaria_id": imobiliaria_id,  # ✅ Adicionado campo imobiliaria_id
        "title": property.title,
        "description": property.description,
        "property_type": property.property_type.value,
        "tipo_negocio": property.tipo_negocio.value,
        "value": property.value,
        "address": property.address,
        "city": property.city,
        "state": property.state,
        "bedrooms": property.bedrooms,
        "bathrooms": property.bathrooms,
        "area": property.area,
        "garage_spaces": property.garage_spaces,
        "status": property.status.value,
        "images": [],
        "ai_title": None,
        "ai_description": None,
        "ai_highlights": [],
        "image_analysis": None,
        "views": 0,
        "clicks": 0,
        "leads": 0,
        "created_at": now,
        "updated_at": now
    }

    db["properties"][property_id] = new_property

    return PropertyResponse(**new_property)


@router.put("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: str,
    property: PropertyUpdate,
    request: Request
):
    db = get_memory_db()
    user_info = get_current_user_from_request(request)
    property_obj = db["properties"].get(property_id)

    if not property_obj:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")

    # Verificar acesso RBAC
    from middleware import check_resource_access
    if not check_resource_access(user_info, property_obj.get("user_id"), property_obj.get("imobiliaria_id")):
        raise HTTPException(status_code=403, detail="Acesso negado")

    # Atualizar campos
    if property.title is not None:
        property_obj["title"] = property.title
    if property.description is not None:
        property_obj["description"] = property.description
    if property.property_type is not None:
        property_obj["property_type"] = property.property_type.value
    if property.value is not None:
        property_obj["value"] = property.value
    if property.address is not None:
        property_obj["address"] = property.address
    if property.city is not None:
        property_obj["city"] = property.city
    if property.state is not None:
        property_obj["state"] = property.state
    if property.bedrooms is not None:
        property_obj["bedrooms"] = property.bedrooms
    if property.bathrooms is not None:
        property_obj["bathrooms"] = property.bathrooms
    if property.area is not None:
        property_obj["area"] = property.area
    if property.garage_spaces is not None:
        property_obj["garage_spaces"] = property.garage_spaces
    if property.status is not None:
        property_obj["status"] = property.status.value

    property_obj["updated_at"] = str(datetime.now())
    db["properties"][property_id] = property_obj

    return PropertyResponse(**property_obj)


@router.delete("/{property_id}")
async def delete_property(property_id: str, request: Request):
    db = get_memory_db()
    user_info = get_current_user_from_request(request)
    property = db["properties"].get(property_id)

    if not property:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")

    # Verificar acesso RBAC
    from middleware import check_resource_access
    if not check_resource_access(user_info, property.get("user_id"), property.get("imobiliaria_id")):
        raise HTTPException(status_code=403, detail="Acesso negado")

    del db["properties"][property_id]

    return {"message": "Imóvel excluído com sucesso"}
