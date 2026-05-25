# Guia de Boas Práticas - Netbox + Ansible

## 📌 Estrutura de Dados no Netbox

### Organização Recomendada

**Sites**: Locais físicos onde a infraestrutura reside
- Data Center Principal
- Data Center Secundário
- Filiais

**Racks**: Estruturas dentro de sites
- Identificar por número/localização
- Documentar U (unidade) inicial e final

**Dispositivos**: Equipamentos individuais
- Usar nomenclatura consistente (ex: tipo-local-número)
- Manter comentários atualizados
- Registrar IP primário corretamente

**Interfaces**: Conexões de rede
- Documentar VLANs
- Manter descrições claras
- Registrar MACs de gerenciamento

### Exemplo de Nomenclatura

```
router-br-01       # Router, Brasil, número 01
switch-dc1-02      # Switch, Data Center 1, número 02
server-app-prod-01 # Server, Aplicação, Produção, número 01
firewall-edge-01   # Firewall, borda, número 01
```

## 🔄 Workflow Netbox → Ansible

### 1. Adicionar Dispositivos no Netbox

```bash
# Via UI em http://localhost:8000
# Ou via API/Script

docker-compose exec ansible python /scripts/add_netbox_devices.py devices.json
```

### 2. Verificar Inventário

```bash
# Listar todos os dispositivos
./scripts/manage.sh list-devices

# Testar inventário dinâmico
./scripts/manage.sh test-inventory
```

### 3. Executar Playbooks

```bash
# Com grupos automáticos do Netbox
./scripts/manage.sh run-playbook ansible/playbooks/sync_netbox.yml
```

## 📊 Custom Fields no Netbox

Recomendamos adicionar custom fields para melhorar a integração:

### Campos Sugeridos

| Campo | Tipo | Uso |
|-------|------|-----|
| `ansible_user` | Text | Usuário para acesso SSH |
| `ansible_port` | Integer | Porta SSH (padrão: 22) |
| `snmp_community` | Text | Comunidade SNMP (oculto) |
| `environment` | Select | prod/staging/dev |
| `monitoring` | Boolean | Incluir em monitoramento |
| `backup_enabled` | Boolean | Backup habilitado |

### Exemplo de JSON

```json
{
  "custom_fields": {
    "ansible_user": "network-admin",
    "ansible_port": 22,
    "environment": "prod",
    "monitoring": true
  }
}
```

## 🔐 Segurança

### Credenciais e Tokens

1. **Nunca commitar .env no git**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Usar gerenciador de segredos em produção**
   - HashiCorp Vault
   - AWS Secrets Manager
   - Azure Key Vault

3. **Rotacionar tokens regularmente**
   ```bash
   # Gerar novo token a cada 90 dias
   ./scripts/manage.sh token
   ```

### Acesso SSH do Ansible

```bash
# Criar diretório para chaves
mkdir -p ansible/ssh_keys
chmod 700 ansible/ssh_keys

# Adicionar chaves privadas
cp ~/.ssh/id_rsa ansible/ssh_keys/
chmod 600 ansible/ssh_keys/id_rsa
```

### Ansible Vault para Senhas

```bash
# Criar arquivo com senhas criptografadas
ansible-vault create ansible/vars/credentials.yml

# Conteúdo exemplo:
# ---
# db_password: "senha_super_secreta"
# api_token: "token_oculto"

# Usar em playbooks:
# vars_files:
#   - ansible/vars/credentials.yml
```

## 📈 Escalabilidade

### Para Ambientes Grandes

1. **Dividir Playbooks por Função**
   ```
   playbooks/
   ├── networking/
   │   ├── base_config.yml
   │   ├── routing.yml
   │   └── security.yml
   ├── servers/
   │   ├── provisioning.yml
   │   ├── patching.yml
   │   └── monitoring.yml
   └── shared/
       └── common.yml
   ```

2. **Usar Roles do Ansible**
   ```
   roles/
   ├── base_linux/
   ├── webserver/
   ├── database/
   └── monitoring_agent/
   ```

3. **Organizar Inventário Dinamicamente**
   ```python
   # Agrupar por:
   # - Site
   # - Função
   # - Ambiente
   # - Criticidade
   ```

## 🚀 Performance

### Otimizações Recomendadas

1. **Usar Forks do Ansible**
   ```ini
   # ansible.cfg
   [defaults]
   forks = 10  # Aumentar conforme CPU disponível
   ```

2. **Paralelizar Tarefas**
   ```yaml
   - name: Tarefa paralela
     hosts: all
     serial: 0  # Executar em paralelo
   ```

3. **Cache de Inventário**
   ```python
   # Implementar cache simples em netbox_inventory.py
   import json
   cache_file = '/tmp/netbox_inventory.cache'
   ```

## 📈 Manutenção Prática

**Quando algo quebra:**
- SSH para investigar logs: `docker-compose logs -f netbox`
- Validar conectividade: `curl -v http://localhost:8000/api/dcim/devices/`
- Rodar inventário manualmente: `./scripts/manage.sh test-inventory`

**Antes de mudanças críticas:**
- Backup do PostgreSQL: `docker-compose exec postgres pg_dump -U netbox netbox > backup_$(date +%Y%m%d-%H%M%S).sql`
- Testar playbook em modo dry-run: `ansible-playbook --check`

**Após alguns meses em produção:**
- Revisar tokens expirados e regenerar
- Limpeza de containers não usados
- Atualizar imagens base quando necessário

### Backup e Recovery

```bash
# Backup do banco PostgreSQL
docker-compose exec postgres pg_dump -U netbox netbox > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker-compose exec -T postgres psql -U netbox netbox < backup_20240101.sql

# Backup de volumes
docker run --rm -v netbox_media:/data -v $(pwd):/backup \
  alpine tar czf /backup/media_backup.tar.gz -C /data .
```

## 🔍 Monitoramento

### Métricas Importantes

1. **Netbox**
   - Tempo de resposta da API
   - Uso de banco de dados
   - Taxa de erro

2. **Ansible**
   - Tempo de execução de playbooks
   - Taxa de falha
   - Sincronização com Netbox

### Implementar Logs Centralizados

```yaml
# Adicionar a playbooks para logging
- name: Log executado
  debug:
    msg: "Playbook {{ playbook }} completado em {{ ansible_date_time }}"
```

## 📚 Recursos

- [Netbox Best Practices](https://netbox.readthedocs.io/)
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/tips_tricks/index.html)
- [Netbox Ansible Modules](https://github.com/netbox-community/ansible_modules)


