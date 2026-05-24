#!/bin/bash
# Script de inicialização rápida do projeto

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Netbox + Ansible - Quick Start      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker não instalado!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker encontrado${NC}"

# Verificar docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose não instalado!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker Compose encontrado${NC}"

# Criar .env se não existir
if [ ! -f .env ]; then
    echo -e "${YELLOW}→ Criando arquivo .env${NC}"
    cp .env.example .env
fi

# Dar permissão ao script de gerenciamento
chmod +x scripts/manage.sh

echo -e "${YELLOW}→ Iniciando serviços...${NC}"
docker-compose down 2>/dev/null || true
docker-compose up -d

echo -e "${YELLOW}→ Aguardando serviços ficarem prontos...${NC}"
sleep 15

# Verificar se Netbox está acessível
if curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Netbox está online!${NC}"
else
    echo -e "${YELLOW}⟳ Netbox ainda está iniciando...${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        Projeto Iniciado!               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}Próximos passos:${NC}"
echo ""
echo "1. Acessar Netbox:"
echo -e "   ${YELLOW}URL: http://localhost:8000${NC}"
echo -e "   ${YELLOW}Usuário: admin${NC}"
echo -e "   ${YELLOW}Senha: admin${NC}"
echo ""
echo "2. Gerar Token de API:"
echo -e "   ${YELLOW}./scripts/manage.sh token${NC}"
echo ""
echo "3. Atualizar .env com o token gerado"
echo ""
echo "4. Consultar comandos disponíveis:"
echo -e "   ${YELLOW}./scripts/manage.sh${NC}"
echo ""
echo "5. Ver documentação completa:"
echo -e "   ${YELLOW}cat README.md${NC}"
echo ""
