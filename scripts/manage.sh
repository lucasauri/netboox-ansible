#!/bin/bash
# Script: Gerenciar projeto Netbox + Ansible
# Descrição: Inicia, para e gerencia os containers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Função: Iniciar containers
start_services() {
    print_info "Iniciando serviços Netbox + Ansible..."
    cd "$PROJECT_DIR"
    docker-compose up -d
    print_success "Serviços iniciados com sucesso!"
    
    print_info "Aguardando Netbox ficar pronto..."
    sleep 10
    
    if curl -s http://localhost:8000 > /dev/null; then
        print_success "Netbox está acessível em http://localhost:8000"
        print_info "Credenciais padrão - Usuário: admin, Senha: admin"
    fi
}

# Função: Parar containers
stop_services() {
    print_info "Parando serviços..."
    cd "$PROJECT_DIR"
    docker-compose down
    print_success "Serviços parados!"
}

# Função: Gerar token de API
generate_token() {
    print_info "Gerando token de API para Netbox..."
    
    # Aguarda o Netbox estar pronto
    sleep 5
    
    TOKEN=$(docker-compose exec -T netbox python manage.py drf_create_token admin 2>/dev/null | grep -oP '(?<=Generated token, ).*' || echo "token_não_gerado")
    
    if [ "$TOKEN" != "token_não_gerado" ]; then
        print_success "Token gerado: $TOKEN"
        print_info "Atualize a variável NETBOX_TOKEN no docker-compose.yml e no arquivo .env"
    else
        print_warning "Não foi possível gerar token automaticamente. Gere manualmente via UI."
    fi
}

# Função: Executar playbook Ansible
run_playbook() {
    if [ -z "$1" ]; then
        print_warning "Uso: $0 run-playbook <nome-playbook.yml>"
        return 1
    fi
    
    print_info "Executando playbook: $1"
    docker-compose exec -T ansible ansible-playbook "$1" -v
}

# Função: Listar dispositivos no Netbox
list_devices() {
    print_info "Dispositivos registrados no Netbox:"
    docker-compose exec -T ansible python /scripts/list_netbox_devices.py
}

# Função: Teste de inventário dinâmico
test_inventory() {
    print_info "Testando inventário dinâmico..."
    docker-compose exec -T ansible python /ansible/inventory/netbox_inventory.py | python -m json.tool
}

# Main
case "${1:-}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        start_services
        ;;
    token)
        generate_token
        ;;
    run-playbook)
        run_playbook "$2"
        ;;
    list-devices)
        list_devices
        ;;
    test-inventory)
        test_inventory
        ;;
    status)
        print_info "Status dos containers:"
        docker-compose ps
        ;;
    logs)
        docker-compose logs -f "${2:-}"
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|token|run-playbook <playbook>|list-devices|test-inventory|status|logs [service]}"
        exit 1
        ;;
esac
