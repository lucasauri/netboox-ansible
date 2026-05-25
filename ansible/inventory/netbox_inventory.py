#!/usr/bin/env python3
"""
Netbox Dynamic Inventory Script para Ansible
Sincroniza dispositivos do Netbox com o inventário do Ansible
"""

import json
import logging
import os
import sys
import requests
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s', stream=sys.stderr)
logger = logging.getLogger(__name__)

class NetboxInventory:
    def __init__(self):
        self.netbox_url = os.getenv('NETBOX_URL', 'http://netbox:8000')
        self.netbox_token = os.getenv('NETBOX_TOKEN', '')
        
        if not self.netbox_token:
            logger.error("Variável NETBOX_TOKEN não definida")
            sys.exit(1)
        
        self.inventory = {
            'all': {'hosts': {}, 'vars': {}},
            'networking': {'hosts': {}, 'vars': {}},
            'servers': {'hosts': {}, 'vars': {}},
            'security': {'hosts': {}, 'vars': {}}
        }
    
    def fetch_devices(self):
        """Busca todos os dispositivos do Netbox ou falha crítica"""
        url = urljoin(self.netbox_url, '/api/dcim/devices/')
        headers = {'Authorization': f'Token {self.netbox_token}'}
        
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=10)
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.exceptions.Timeout:
            logger.error(f"Timeout ao conectar em {self.netbox_url}")
            sys.exit(1)
        except requests.exceptions.ConnectionError:
            logger.error(f"Erro de conexão: Não foi possível alcançar {self.netbox_url}")
            sys.exit(1)
        except requests.exceptions.HTTPError:
            logger.error(f"Erro HTTP {response.status_code}: Verifique token e URL")
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro crítico ao conectar com Netbox: {e}")
            sys.exit(1)
    
    def get_device_type(self, device):
        """Classifica o dispositivo em categoria"""
        device_type = device.get('device_type', {}).get('model', '').lower()
        
        if any(x in device_type for x in ['router', 'switch', 'firewall']):
            return 'networking'
        elif any(x in device_type for x in ['server', 'host']):
            return 'servers'
        elif any(x in device_type for x in ['fw', 'security', 'utm']):
            return 'security'
        
        return 'all'
    
    def build_inventory(self):
        """Constrói o inventário a partir dos dados do Netbox"""
        devices = self.fetch_devices()
        logger.info(f"Carregados {len(devices)} dispositivos do Netbox")
        
        for device in devices:
            hostname = device.get('name', 'unknown')
            ip = device.get('primary_ip4') or device.get('primary_ip6')
            
            if not ip:
                logger.warning(f"Dispositivo {hostname} sem IP primário, pulando")
                continue
            
            host_vars = {
                'ansible_host': ip,
                'device_id': device.get('id'),
                'device_type': device.get('device_type', {}).get('model'),
                'site': device.get('site', {}).get('name'),
                'status': device.get('status', {}).get('value'),
            }
            
            host_vars = {k: v for k, v in host_vars.items() if v is not None}
            
            category = self.get_device_type(device)
            self.inventory[category]['hosts'][hostname] = host_vars
            self.inventory['all']['hosts'][hostname] = host_vars
        
        return self.inventory
    
    def print_json(self):
        """Imprime inventário em formato JSON"""
        print(json.dumps(self.inventory, indent=2))

if __name__ == '__main__':
    try:
        inventory = NetboxInventory()
        inventory.build_inventory()
        inventory.print_json()
    except Exception as e:
        logger.error(f"Erro crítico: {e}")
        sys.exit(1)
