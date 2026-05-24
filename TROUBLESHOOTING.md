# Troubleshooting Guide - Netbox + Ansible

## Problemas Comuns

### 🔴 Netbox não inicia

#### Sintoma
```
docker-compose logs netbox mostra erros
```

#### Soluções

1. **Verificar PostgreSQL**
```bash
./scripts/manage.sh logs postgres
docker-compose exec postgres psql -U netbox -c "SELECT 1"
```

2. **Limpar containers e volumes**
```bash
docker-compose down -v
docker-compose up -d
```

3. **Recriar banco de dados**
```bash
docker-compose exec postgres psql -U netbox -c "DROP DATABASE IF EXISTS netbox;"
docker-compose exec postgres psql -U netbox -c "CREATE DATABASE netbox;"
```

---

### 🔴 Erro de conexão com Netbox

#### Sintoma
```
Connection refused on localhost:8000
```

#### Verificações

```bash
# Status dos containers
./scripts/manage.sh status

# Logs do Netbox
./scripts/manage.sh logs netbox

# Testar conectividade
curl -v http://localhost:8000
```

#### Soluções

1. **Aguardar inicialização completa** (pode levar 30-60s)
```bash
# Monitorar logs
./scripts/manage.sh logs netbox -f
```

2. **Verificar portas em uso**
```bash
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows
```

3. **Liberar porta se necessário**
```bash
# Mudar porta em docker-compose.yml
# "8001:8000" ao invés de "8000:8000"
```

---

### 🔴 Ansible não consegue acessar Netbox

#### Sintoma
```
Ansible playbook retorna erro de conexão com Netbox
```

#### Verificações

```bash
# Testar conectividade do container Ansible
docker-compose exec ansible curl http://netbox:8000

# Verificar token
echo $NETBOX_TOKEN
```

#### Soluções

1. **Gerar novo token**
```bash
./scripts/manage.sh token
```

2. **Verificar variáveis de ambiente**
```bash
docker-compose exec ansible env | grep NETBOX
```

3. **Validar token manualmente**
```bash
docker-compose exec ansible curl \
  -H "Authorization: Token YOUR_TOKEN" \
  http://netbox:8000/api/dcim/devices/
```

---

### 🔴 Inventário dinâmico vazio

#### Sintoma
```
Inventário sem dispositivos mesmo com dados no Netbox
```

#### Verificações

```bash
# Testar script de inventário
./scripts/manage.sh test-inventory

# Verificar se há dispositivos cadastrados
./scripts/manage.sh list-devices

# Debug manual
docker-compose exec ansible python \
  /ansible/inventory/netbox_inventory.py
```

#### Soluções

1. **Adicionar dispositivos ao Netbox**
   - Acessar http://localhost:8000
   - DCIM → Devices → Add Device

2. **Validar categorização**
   - Script classifica por tipo de dispositivo
   - Confirmar que device_type está correto

3. **Testar manualmente**
```bash
docker-compose exec ansible python3 << 'EOF'
import os, requests
url = "http://netbox:8000/api/dcim/devices/"
headers = {"Authorization": f"Token {os.getenv('NETBOX_TOKEN')}"}
r = requests.get(url, headers=headers, verify=False)
print(f"Status: {r.status_code}")
print(f"Total: {len(r.json().get('results', []))}")
EOF
```

---

### 🔴 Playbook executa com erros

#### Sintoma
```
Playbook falha ao executar
```

#### Debug

```bash
# Executar com verbosidade
./scripts/manage.sh run-playbook \
  ansible/playbooks/sync_netbox.yml -vvv

# Testar sintaxe
docker-compose exec ansible ansible-playbook \
  --syntax-check \
  ansible/playbooks/seu_playbook.yml

# Verificar inventário
docker-compose exec ansible ansible-inventory --list
```

#### Soluções

1. **Instalar dependências Ansible**
```bash
docker-compose exec ansible pip install -r /ansible/requirements.txt
```

2. **Validar variáveis**
```bash
docker-compose exec ansible ansible all -m debug -a "var=hostvars"
```

3. **Testar conectividade SSH**
```bash
docker-compose exec ansible ping -c1 seu_device_ip
```

---

### 🔴 Erro de permissão em scripts

#### Sintoma
```
Permission denied ao executar scripts
```

#### Solução

```bash
# Tornar executável
chmod +x scripts/*.sh
chmod +x quickstart.sh

# Tornar executável recursivamente
chmod +x scripts/
```

---

### 🔴 Banco de dados corrompido

#### Sintoma
```
Erros ao acessar banco ou perda de dados
```

#### Recuperação

1. **Restaurar do backup**
```bash
# Se houver backup SQL
docker-compose exec -T postgres psql -U netbox netbox < backup.sql
```

2. **Reinicializar banco limpo**
```bash
docker-compose down -v
rm -rf postgres_data/
docker-compose up -d
sleep 30
./scripts/manage.sh token
```

---

### 🟡 Performance lenta

#### Diagnóstico

```bash
# Ver uso de recursos
docker stats

# Verificar logs de erro
./scripts/manage.sh logs netbox | grep -i error
./scripts/manage.sh logs postgres | grep -i slow

# Teste de API
time curl http://localhost:8000/api/dcim/devices/
```

#### Soluções

1. **Aumentar recursos do Docker**
   - Ir em Docker Desktop → Preferences → Resources
   - Aumentar RAM e CPUs

2. **Otimizar Ansible**
```ini
# ansible.cfg
[defaults]
forks = 10
```

3. **Limpar cache**
```bash
docker-compose exec ansible rm -rf /ansible/.ansible/
```

---

## Debugging Avançado

### Acessar shell do Netbox

```bash
docker-compose exec netbox /bin/bash
python manage.py shell
```

### Acessar PostgreSQL diretamente

```bash
docker-compose exec postgres psql -U netbox netbox
\dt  # listar tabelas
SELECT * FROM dcim_device LIMIT 5;
```

### Monitorar recursos em tempo real

```bash
# Terminal 1
docker stats

# Terminal 2
./scripts/manage.sh logs netbox -f
```

### Validar docker-compose

```bash
docker-compose config
docker-compose config --resolve-image-digests
```

---

## Logs Úteis

### Ver todos os logs

```bash
# Últimas 100 linhas de todos os serviços
./scripts/manage.sh logs

# Apenas do Netbox
./scripts/manage.sh logs netbox

# Apenas do Ansible
./scripts/manage.sh logs ansible

# Tempo real
./scripts/manage.sh logs -f

# Últimas 50 linhas
./scripts/manage.sh logs --tail 50
```

### Filtrar logs

```bash
# Buscar erros
./scripts/manage.sh logs netbox | grep ERROR

# Buscar warnings
./scripts/manage.sh logs netbox | grep WARNING

# Período específico (últimas 10 minutos)
./scripts/manage.sh logs --since 10m
```

---

## Checklist de Recuperação

Siga este checklist se tudo parar de funcionar:

- [ ] `./scripts/manage.sh status` - todos rodando?
- [ ] `./scripts/manage.sh logs netbox` - erros?
- [ ] `curl http://localhost:8000` - Netbox responde?
- [ ] `./scripts/manage.sh token` - token válido?
- [ ] `./scripts/manage.sh test-inventory` - inventário ok?
- [ ] `./scripts/manage.sh list-devices` - dispositivos visíveis?
- [ ] Verificar .env tem valores corretos
- [ ] Se tudo falhar: `docker-compose down -v && docker-compose up -d`

---

## Contato e Recursos

Se o problema persistir:

1. Verificar logs completos: `docker-compose logs > logs.txt`
2. Consultar documentação oficial:
   - Netbox: https://netbox.readthedocs.io/
   - Ansible: https://docs.ansible.com/
3. Coletar informações do sistema:
   ```bash
   docker version
   docker-compose version
   uname -a
   ```

---

**Última atualização**: Maio 2026
