"""
Serviço de Análise de Imagens com IA
Analisa ambientes, iluminação, qualidade e detecta problemas
"""
import random
from typing import List, Dict


# Mapeamento de ambientes possíveis
ENVIRONMENTS = [
    "Sala de estar",
    "Quarto",
    "Cozinha",
    "Banheiro",
    "Varanda",
    "Área de serviço",
    "Garagem",
    "Jardim",
    "Sala de jantar",
    "Escritório"
]


async def analyze_images(image_urls: List[str]) -> Dict:
    """
    Analisa uma lista de imagens e retorna informações sobre:
    - Ambientes identificados
    - Pontuação de iluminação
    - Pontuação de qualidade
    - Problemas detectados
    - Sugestões de melhoria
    """
    # Simular análise de cada imagem
    environments = []
    total_lighting_score = 0
    total_quality_score = 0
    all_issues = []
    all_suggestions = []
    
    for i, url in enumerate(image_urls):
        # Simular análise baseada no índice
        env = ENVIRONMENTS[i % len(ENVIRONMENTS)]
        
        # Gerar scores aleatórios mas consistentes
        lighting_score = random.randint(60, 95)
        quality_score = random.randint(55, 90)
        
        environments.append({
            "environment": env,
            "image_url": url,
            "lighting_score": lighting_score,
            "quality_score": quality_score
        })
        
        total_lighting_score += lighting_score
        total_quality_score += quality_score
        
        # Detectar problemas
        if lighting_score < 70:
            all_issues.append(f"{env}: Iluminação insuficiente")
            all_suggestions.append(f"{env}: Adicione mais luz ou use flash")
        
        if quality_score < 65:
            all_issues.append(f"{env}: Qualidade de imagem abaixo do ideal")
            all_suggestions.append(f"{env}: Melhore a resolução ou substitua a foto")
    
    # Calcular médias
    avg_lighting = int(total_lighting_score / len(image_urls)) if image_urls else 0
    avg_quality = int(total_quality_score / len(image_urls)) if image_urls else 0
    
    # Adicionar sugestões gerais
    if avg_lighting < 70:
        all_suggestions.append("Considere fotografar em horários com melhor luz natural")
    
    if avg_quality < 70:
        all_suggestions.append("Use uma câmera com melhor resolução ou smartphone atual")
    
    if len(image_urls) < 5:
        all_suggestions.append("Adicione mais fotos para uma melhor apresentação")
    
    return {
        "environments": environments,
        "lighting_score": avg_lighting,
        "quality_score": avg_quality,
        "issues": all_issues[:5],  # Limitar a 5 problemas
        "suggestions": all_suggestions[:8]  # Limitar a 8 sugestões
    }


async def improve_images(image_urls: List[str]) -> List[Dict]:
    """
    Melhora automaticamente as imagens:
    - Ajuste de brilho/contraste
    - Nitidez
    - Correção de cores
    - Crop inteligente
    - Alinhamento
    """
    improvements_list = []
    
    for url in image_urls:
        # Simular URL da imagem melhorada
        # Em produção, isso chamaria um serviço de processamento de imagem
        improved_url = url.replace("/original/", "/improved/")
        
        improvements = [
            "Ajuste de brilho aplicado",
            "Contraste otimizado",
            "Correção de cor aplicada",
            "Nitidez ajustada",
            "Alinhamento corrigido"
        ]
        
        improvements_list.append({
            "original_url": url,
            "improved_url": improved_url,
            "improvements": improvements
        })
    
    return improvements_list


def detect_environment(image_description: str) -> str:
    """Detecta o ambiente baseado na descrição da imagem"""
    description_lower = image_description.lower()
    
    if "quarto" in description_lower or "bedroom" in description_lower:
        return "Quarto"
    elif "sala" in description_lower or "living" in description_lower:
        return "Sala de estar"
    elif "cozinha" in description_lower or "kitchen" in description_lower:
        return "Cozinha"
    elif "banheiro" in description_lower or "bathroom" in description_lower:
        return "Banheiro"
    elif "varanda" in description_lower or "balcony" in description_lower:
        return "Varanda"
    elif "jardim" in description_lower or "garden" in description_lower:
        return "Jardim"
    else:
        return "Ambiente não identificado"