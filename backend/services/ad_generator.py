"""
Serviço de Geração de Anúncios com IA
Gera títulos otimizados, descrições persuasivas e highlights
"""
import random
from typing import Dict, List


# Templates de títulos por tipo de imóvel (ANTI-ALUCINAÇÃO: só dados reais)
TITLE_TEMPLATES = {
    "apartamento": [
        "🏠 {bedrooms} Quarto(s) em {city}",
        "✨ Apartamento {area}m² - {city}",
        "💎 {property_type.upper()} à Venda - {city}",
        "🌟 Oportunidade em {city}: {bedrooms}Q",
        "🏙️ {property_type} {area}m² {state}"
    ],
    "casa": [
        "🏡 Casa {bedrooms}Q em {city}",
        "✨ {area}m² em {city}, {state}",
        "🌺 Casa Familiar - {city}",
        "🏠 {property_type} à Venda {city}",
        "💫 Casa {bedrooms} Suíte(s) {city}"
    ],
    "comercial": [
        "🏪 Espaço Comercial {area}m²",
        "💼 {property_type} {city}",
        "🏢 Ponto {area}m² - {city}",
        "📍 Loja/Consultório {city}",
        "✨ Comercial Premium {state}"
    ],
    "terreno": [
        "📐 Terreno {area}m² {city}",
        "🌿 {property_type} à Venda {city}",
        "🏗️ Lote em {city}, {state}",
        "💚 Terreno Construir {city}",
        "📍 Oportunidade {city}"
    ]
}


# Templates de descrições (SÓ DADOS REAIS - sem alucinar features)
DESCRIPTION_TEMPLATES = {
    "apartamento": [
        "Apartamento localizado em {city}, {state}. Possui {bedrooms} quarto(s), {bathrooms} banheiro(s) e {area}m² de área útil. Valor: R$ {value:,.0f}. {address}",
        "Imóvel tipo {property_type} com {bedrooms}Q/{bathrooms}B em {city}. Área: {area}m². Em {address}. Imóvel disponível para visita."
    ],
    "casa": [
        "Casa em {city}, {state} com {bedrooms} quartos e {area}m². {bathrooms} banheiro(s). Localizado em {address}. Valor R$ {value:,.0f}",
        "{property_type} à venda em {city}. {bedrooms}Q, {area}m², {garage_spaces} vaga(s). Agende sua visita!"
    ],
    "comercial": [
        "{property_type} comercial {area}m² em {city}. Localização: {address}. Ideal para diversos negócios. Valor: R$ {value:,.0f}",
        "Espaço {area}m² disponível em {city}, {state}. Entre em contato para mais informações."
    ]
}


# Highlights por tipo de imóvel
HIGHLIGHTS_TEMPLATES = {
    "apartamento": [
        "✅ Localização privilegiada",
        "✅ Academia e área de lazer",
        "✅ Segurança 24h",
        "✅ Vaga de garagem",
        "✅ Acabamento de alto padrão",
        "✅ Próximo ao metrô",
        "✅ Vista panorâmica"
    ],
    "casa": [
        "✅ Quintal com churrasqueira",
        "✅ Piscina privativa",
        "✅ Jardim arborizado",
        "✅ Segurança reforçada",
        "✅ Casa de apoio",
        "✅ Área de serviço completa",
        "✅ Close de escolas"
    ],
    "comercial": [
        "✅ Alta visibilidade",
        "✅ Estacionamento próprio",
        "✅ Piso industrial",
        "✅ Instalações elétricas novas",
        "✅ Ar-condicionado central",
        "✅ Acesso para deficientes"
    ]
}


async def generate_ad(property_data: Dict) -> Dict:
    """
    Gera um anúncio automaticamente baseado nos dados do imóvel
    """
    property_type = property_data.get("property_type", "apartamento")
    city = property_data.get("city", "")
    state = property_data.get("state", "")
    bedrooms = property_data.get("bedrooms", 0)
    bathrooms = property_data.get("bathrooms", 0)
    area = property_data.get("area", 0)
    value = property_data.get("value", 0)
    
    # Título só dados reais (anti-alucinação)
    title_templates = TITLE_TEMPLATES.get(property_type, TITLE_TEMPLATES["apartamento"])
    title = random.choice(title_templates).format(
        bedrooms=bedrooms, area=area, property_type=property_type, city=city or 'cidade', state=state or 'estado'
    )
    
    # Gerar descrição
    desc_templates = DESCRIPTION_TEMPLATES.get(property_type, DESCRIPTION_TEMPLATES["apartamento"])
    address = property_data.get('address', 'localização privilegiada')
    property_type = property_data.get('property_type', 'imóvel')
    description = random.choice(desc_templates).format(
        bedrooms=bedrooms or 0,
        bathrooms=bathrooms or 0,
        area=area or 0,
        city=city or 'sua cidade',
        state=state or 'seu estado',
        address=address,
        value=value or 0,
        property_type=property_type
    )
    
    # Adicionar informações de valor
    value_formatted = f"R$ {value:,.0f}".replace(",", ".")
    description += f"\n\n💰 Valor: {value_formatted}"
    
    # Highlights SÓ dados confirmados (anti-alucinação)
    highlights = []
    
    # Adicionar highlights baseados nos dados
    if bedrooms > 0:
        highlights.append(f"✅ {bedrooms} quarto(s)")
    if bathrooms > 0:
        highlights.append(f"✅ {bathrooms} banheiro(s)")
    if area > 0:
        highlights.append(f"✅ {area}m² de área")
    if property_data.get("garage_spaces", 0) > 0:
        highlights.append(f"✅ {property_data.get('garage_spaces')} vaga(s) de garagem")
    
    # Gerar tags
    tags = [
        property_type,
        city.lower(),
        "imóvel",
        "venda",
        "oportunidade"
    ]
    
    if value < 300000:
        tags.append("barato")
        tags.append("custo-benefício")
    elif value > 1000000:
        tags.append("alto-padrão")
        tags.append("premium")
    
    return {
        "title": title,
        "description": description,
        "highlights": highlights,
        "review_required": True,
        "generated_from_real_data": True
    }


def generate_seo_keywords(property_data: Dict) -> List[str]:
    """Gera palavras-chave para SEO"""
    keywords = []
    
    property_type = property_data.get("property_type", "")
    city = property_data.get("city", "")
    state = property_data.get("state", "")
    
    keywords.append(f"{property_type} {city}")
    keywords.append(f"{property_type} {state}")
    keywords.append(f"comprar {property_type} {city}")
    keywords.append(f"{property_type} à venda {city}")
    
    return keywords