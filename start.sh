#!/bin/bash

# Imovia - Script de Inicialização

echo "🚀 Iniciando Imovia..."

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar Python
echo -e "${BLUE}Verificando Python...${NC}"
if command -v python3 &> /dev/null; then
    python3 --version
else
    echo -e "${YELLOW}Python não encontrado. Instalando...${NC}"
    brew install python3
fi

# Verificar Node.js
echo -e "${BLUE}Verificando Node.js...${NC}"
if command -v node &> /dev/null; then
    node --version
else
    echo -e "${YELLOW}Node.js não encontrado. Instalando...${NC}"
    brew install node
fi

# Backend
echo -e "${BLUE}Configurando Backend...${NC}"
cd backend
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

echo "Ativando ambiente virtual..."
source venv/bin/activate

echo "Instalando dependências..."
pip install -r requirements.txt

echo -e "${GREEN}Backend configurado!${NC}"

# Frontend
echo -e "${BLUE}Configurando Frontend...${NC}"
cd ../frontend

echo "Instalando dependências..."
npm install

echo -e "${GREEN}Frontend configurado!${NC}"

echo ""
echo "========================================="
echo -e "${GREEN}Imovia pronto!${NC}"
echo "========================================="
echo ""
echo "Para iniciar o Backend:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn main:app --reload"
echo ""
echo "Para iniciar o Frontend:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Acesse: http://localhost:5173"
echo "========================================="