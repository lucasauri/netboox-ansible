#!/usr/bin/env python3
"""
Netbox Dynamic Inventory Script para Ansible
Sincroniza dispositivos do Netbox com o inventário do Ansible
"""

import json
import os
import requests
from urllib.parse import urljoin

class NetboxInventory:
    def __init__(self):
        self.netbox_url = os.getenv('NETBOX_URL', 'http://netbox:8000')
        self.netbox_token = os.getenv('NETBOX_TOKEN', '')
        self.inventory = {
            'all': {
                'hosts': {},
                'vars': {}
            },
            'networking': {
                'hosts': {},
                'vars': {}
            },
            'servers': {
                'hosts': {},
                'vars': {}
            },
            'security': {
                'hosts': {},
                'vars': {}
            }
        }
    
    def fetch_devices(self):
        """Busca todos os dispositivos do Netbox"""
        url = urljoin(self.netbox_url, '/api/dcim/devices/')
        headers = {'Authorization': f'Token {self.netbox_token}'}
        
        try:
            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.exceptions.RequestException as e:
            print(f"Erro ao conectar com Netbox: {e}")
            return []
    
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
        
        for device in devices:
            hostname = device.get('name', 'unknown')
            
            # Coleta informações do dispositivo
            host_vars = {
                'ansible_host': device.get('primary_ip4') or device.get('primary_ip6'),
                'device_id': device.get('id'),
                'device_type': device.get('device_type', {}).get('model'),
                'site': device.get('site', {}).get('name'),
                'status': device.get('status', {}).get('value'),
            }
            
            # Remove valores None
            host_vars = {k: v for k, v in host_vars.items() if v is not None}
            
            # Adiciona ao grupo apropriado
            category = self.get_device_type(device)
            self.inventory[category]['hosts'][hostname] = host_vars
            self.inventory['all']['hosts'][hostname] = host_vars
        
        return self.inventory
    
    def print_json(self):
        """Imprime inventário em formato JSON"""
        print(json.dumps(self.inventory, indent=2))

if __name__ == '__main__':
    inventory = NetboxInventory()
    inventory.build_inventory()
    inventory.print_json()
