from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, List
from models.schemas import AIAnalysisResponse, AIAdResponse, ImageImproveResponse
from auth_utils import decode_access_token
from database import get_memory_db
from services.image_analyzer import analyze_images, improve_images
from services.ad_generator import generate_ad
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


@router.post("/properties/{property_id}/analyze", response_model=AIAnalysisResponse)
async def analyze_property_images(
    property_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    db = get_memory_db()
    property = db["properties"].get(property_id)
    
    if not property:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    if property.get("user_id") != current_user_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    images = property.get("images", [])
    if not images:
        raise HTTPException(status_code=400, detail="Imóvel sem imagens para analisar")
    
    # Análise de imagens
    analysis = await analyze_images(images)
    
    # Salvar análise
    property["image_analysis"] = analysis
    property["updated_at"] = str(datetime.now())
    db["properties"][property_id] = property
    
    return AIAnalysisResponse(**analysis)


@router.post("/properties/{property_id}/generate-ad", response_model=AIAdResponse)
async def generate_property_ad(
    property_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    db = get_memory_db()
    property = db["properties"].get(property_id)
    
    if not property:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    if property.get("user_id") != current_user_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Gerar anúncio
    ad = await generate_ad(property)
    
    # Salvar anúncio gerado
    property["ai_title"] = ad["title"]
    property["ai_description"] = ad["description"]
    property["ai_highlights"] = ad["highlights"]
    property["updated_at"] = str(datetime.now())
    db["properties"][property_id] = property
    
    return AIAdResponse(**ad)


@router.post("/properties/{property_id}/improve-images", response_model=List[ImageImproveResponse])
async def improve_property_images(
    property_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    db = get_memory_db()
    property = db["properties"].get(property_id)
    
    if not property:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    if property.get("user_id") != current_user_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    images = property.get("images", [])
    if not images:
        raise HTTPException(status_code=400, detail="Imóvel sem imagens para melhorar")
    
    # Melhorar imagens
    improvements = await improve_images(images)
    
    return improvements


@router.get("/suggestions/{property_id}")
async def get_property_suggestions(
    property_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    db = get_memory_db()
    property = db["properties"].get(property_id)
    
    if not property:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    if property.get("user_id") != current_user_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Gerar sugestões baseadas nos dados do imóvel
    suggestions = []
    
    # Sugestões baseadas no tipo
    property_type = property.get("property_type", "")
    if property_type == "apartamento":
        suggestions.append("Adicione fotos da área comum do prédio")
        suggestions.append(" Destaque a proximidade de serviços e transporte")
    elif property_type == "casa":
        suggestions.append("Fotografe o jardim e área externa")
        suggestions.append("Mostre a segurança do bairro")
    
    # Sugestões baseadas no valor
    value = property.get("value", 0)
    if value > 1000000:
        suggestions.append("Alta gama: invista em fotos profissionais")
        suggestions.append("Destaque acabamentos e materiais de qualidade")
    elif value < 300000:
        suggestions.append("Enfatize o custo-benefício")
        suggestions.append("Mostre a estrutura e manutenção do imóvel")
    
    # Sugestões baseadas na análise de imagem
    analysis = property.get("image_analysis", {})
    if analysis:
        lighting_score = analysis.get("lighting_score", 0)
        if lighting_score < 70:
            suggestions.append("Melhore a iluminação das fotos para aumentar attractividade")
        
        quality_score = analysis.get("quality_score", 0)
        if quality_score < 60:
            suggestions.append("Considere contratar um photographer profissional")
        
        issues = analysis.get("issues", [])
        for issue in issues:
            suggestions.append(f"Correção necessária: {issue}")
    
    return {"suggestions": suggestions}