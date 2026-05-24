# Netbox + Ansible Integration Project

Plataforma de integração entre **Netbox** (IPAM/DCIM) e **Ansible** (automação de infraestrutura) para automação completa do ciclo de vida de dispositivos em redes corporativas.

## Contexto

Este projeto resolve o desafio de manter uma fonte única de verdade para infraestrutura heterogênea. Em ambientes onde você gerencia múltiplos tipos de dispositivos (roteadores, switches, servidores, firewalls) distribuídos em vários sites, o Netbox centraliza os dados e o Ansible executa as mudanças baseado nesses dados. Elimina sincronização manual e reduz inconsistências de configuração.

## 📋 Componentes

### Netbox
- **Função**: Fonte central de dados de infraestrutura
- **Dados gerenciados**: 
  - IPs e VLANs (IPAM)
  - Dispositivos e componentes (DCIM)
  - Sites e espaços
  - Documentação e custom fields

### Ansible
- **Função**: Automação e orquestração baseada em dados do Netbox
- **Playbooks inclusos**:
  - `sync_netbox.yml` - Sincronizar dados de dispositivos com Netbox
  - `configure_networking.yml` - Configurar dispositivos de rede
  - `configure_servers.yml` - Configurar servidores
  - `check_security.yml` - Verificar segurança de firewalls

## 🚀 Início Rápido

### Pré-requisitos
- Docker e Docker Compose
- Acesso a shell/terminal
- Git (opcional)

### 1. Iniciar os Serviços

```bash
# Executar o projeto
./scripts/manage.sh start

# Ou usando docker-compose diretamente
docker-compose up -d
```

### 2. Acessar Netbox

- **URL**: http://localhost:8000
- **Usuário**: admin
- **Senha**: admin

### 3. Gerar Token de API

```bash
./scripts/manage.sh token
```

Ou gere manualmente via UI do Netbox:
1. Acesse http://localhost:8000/admin/
2. Navegue para **Tokens** (em Users)
3. Crie um novo token para o usuário `admin`
4. Copie o token gerado

### 4. Atualizar Configuração

```bash
# Copie o .env.example e atualize com seu token
cp .env.example .env

# Atualize docker-compose.yml com o token real
# Busque por NETBOX_TOKEN e substitua o valor
```

## 📁 Estrutura do Projeto

```
netbox-ansible/
├── docker-compose.yml          # Configuração dos containers
├── .env.example                # Variáveis de ambiente
├── ansible/
│   ├── ansible.cfg            # Configuração do Ansible
│   ├── inventory/
│   │   ├── hosts              # Inventário estático (exemplo)
│   │   └── netbox_inventory.py# Script de inventário dinâmico
│   └── playbooks/
│       ├── sync_netbox.yml    # Sincronizar com Netbox
│       ├── configure_networking.yml  # Configurar rede
│       ├── configure_servers.yml     # Configurar servidores
│       └── check_security.yml        # Verificar segurança
├── scripts/
│   ├── manage.sh              # Script de gerenciamento
│   ├── list_netbox_devices.py # Listar dispositivos
│   ├── add_netbox_devices.py  # Adicionar dispositivos
│   └── sample_devices.json    # Exemplo de dispositivos
└── netbox_config/
    └── configuration.py       # Configuração avançada do Netbox
```

## 📝 Usando Scripts

### Gerenciar Serviços

```bash
# Iniciar
./scripts/manage.sh start

# Parar
./scripts/manage.sh stop

# Reiniciar
./scripts/manage.sh restart

# Ver status
./scripts/manage.sh status

# Ver logs
./scripts/manage.sh logs netbox    # Logs do Netbox
./scripts/manage.sh logs ansible   # Logs do Ansible
```

### Listar Dispositivos

```bash
./scripts/manage.sh list-devices
```

### Testar Inventário Dinâmico

```bash
./scripts/manage.sh test-inventory
```

### Executar Playbooks

```bash
# Sincronizar com Netbox
./scripts/manage.sh run-playbook ansible/playbooks/sync_netbox.yml

# Configurar rede
./scripts/manage.sh run-playbook ansible/playbooks/configure_networking.yml

# Configurar servidores
./scripts/manage.sh run-playbook ansible/playbooks/configure_servers.yml

# Verificar segurança
./scripts/manage.sh run-playbook ansible/playbooks/check_security.yml
```

## 🔧 Configuração Avançada

### Adicionar Dispositivos ao Netbox

1. **Prepare um arquivo JSON** (exemplo: `devices.json`):

```json
[
  {
    "name": "router-prod-01",
    "device_type": 2,
    "site": 1,
    "status": "active",
    "comments": "Roteador de produção"
  }
]
```

2. **Execute o script**:

```bash
docker-compose exec ansible python /scripts/add_netbox_devices.py devices.json
```

### Customizar Playbooks

Edite os playbooks em `ansible/playbooks/` para adicionar suas próprias tarefas:

```yaml
- name: Minha tarefa customizada
  hosts: all
  tasks:
    - name: Exemplo
      debug:
        msg: "Olá {{ inventory_hostname }}"
```

### Usar Inventário Dinâmico

O Netbox é automaticamente consultado como fonte de inventário. Os dispositivos são:
- Organizados em grupos por tipo (networking, servers, security)
- Carregados automaticamente do Netbox
- Atualizados a cada execução do Ansible

## 🌐 Integração com Netbox

### API Endpoints Utilizados

- `GET /api/dcim/devices/` - Listar dispositivos
- `PATCH /api/dcim/devices/{id}/` - Atualizar dispositivo
- `POST /api/dcim/devices/` - Criar dispositivo

### Autenticação

A integração usa Token-based authentication. Certifique-se de:
1. Gerar um token no Netbox
2. Definir a variável `NETBOX_TOKEN`
3. Definir a variável `NETBOX_URL` se for não-padrão

## 🔐 Segurança

**⚠️ Avisos Importantes:**

1. **Mudança de senhas padrão**:
```bash
# Dentro do container Netbox
python manage.py changepassword admin
```

2. **Gere um novo SECRET_KEY** em produção (em `netbox_config/configuration.py`)

3. **Desabilite verificação SSL apenas em desenvolvimento** (veja `NETBOX_VERIFY_SSL`)

4. **Mantenha tokens privados** - não commite `.env` no git

## 📚 Exemplos de Uso

### Sincronizar dados entre Netbox e Ansible

```bash
# 1. Primeiro, adicione dispositivos ao Netbox (via UI ou API)
# 2. Execute o playbook de sincronização
./scripts/manage.sh run-playbook ansible/playbooks/sync_netbox.yml
```

### Aplicar configurações com base em dados do Netbox

```bash
# Os playbooks usam automaticamente o inventário do Netbox
# Dispositivos são agrupados por tipo de site, função, etc.
./scripts/manage.sh run-playbook ansible/playbooks/configure_servers.yml
```

## 🐛 Troubleshooting

### Netbox não inicia

```bash
# Verificar logs
./scripts/manage.sh logs netbox

# Verificar conexão com banco
./scripts/manage.sh logs postgres
```

### Erro ao conectar com Netbox do Ansible

1. Verifique se `NETBOX_TOKEN` está correto
2. Verifique se `NETBOX_URL` é acessível dentro da rede Docker
3. Confira credenciais do banco de dados

### Inventário vazio

1. Verifique se há dispositivos cadastrados no Netbox
2. Confira se o token tem permissões de leitura
3. Teste o script manualmente:
```bash
docker-compose exec ansible python /ansible/inventory/netbox_inventory.py
```

## 📖 Recursos Adicionais

- [Documentação Netbox](https://netbox.readthedocs.io/)
- [Documentação Ansible](https://docs.ansible.com/)
- [Ansible Netbox Plugin](https://github.com/netbox-community/ansible_modules)
- [API Netbox](https://netbox.readthedocs.io/en/stable/api/overview/)

## 📄 Licença

Este projeto é fornecido como exemplo educacional.

## ✉️ Suporte

Para dúvidas, confira:
1. Logs dos containers
2. Documentação oficial do Netbox e Ansible
3. Issues no GitHub (se aplicável)


