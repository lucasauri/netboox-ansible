#!/usr/bin/env python3
"""
Script: Listar dispositivos do Netbox
Consulta a API do Netbox e exibe todos os dispositivos registrados
"""

import logging
import os
import requests
import sys
from urllib.parse import urljoin

try:
    from tabulate import tabulate
except ImportError:
    print("Erro: tabulate não instalado. Execute: pip install tabulate", file=sys.stderr)
    sys.exit(1)

logging.basicConfig(level=logging.ERROR, format='%(message)s', stream=sys.stderr)
logger = logging.getLogger(__name__)

class NetboxDeviceLister:
    def __init__(self):
        self.netbox_url = os.getenv('NETBOX_URL', 'http://netbox:8000')
        self.netbox_token = os.getenv('NETBOX_TOKEN', '')
        
        if not self.netbox_token:
            logger.error("NETBOX_TOKEN não definido")
            sys.exit(1)
    
    def fetch_devices(self):
        """Busca todos os dispositivos do Netbox ou falha"""
        url = urljoin(self.netbox_url, '/api/dcim/devices/')
        headers = {'Authorization': f'Token {self.netbox_token}'}
        
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=10)
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.exceptions.Timeout:
            logger.error(f"Timeout: Netbox em {self.netbox_url} não respondeu em 10s")
            sys.exit(1)
        except requests.exceptions.ConnectionError:
            logger.error(f"Erro de conexão: Não foi possível conectar em {self.netbox_url}")
            sys.exit(1)
        except requests.exceptions.HTTPError:
            logger.error(f"Erro HTTP {response.status_code}: Verifique token e URL")
            sys.exit(1)
    
    def list_devices(self):
        """Lista todos os dispositivos em formato tabular"""
        devices = self.fetch_devices()
        
        if not devices:
            print("Nenhum dispositivo encontrado no Netbox.")
            return
        
        table_data = []
        for device in devices:
            table_data.append([
                device.get('name', 'N/A'),
                device.get('device_type', {}).get('model', 'N/A'),
                device.get('site', {}).get('name', 'N/A'),
                device.get('status', {}).get('value', 'N/A'),
                device.get('primary_ip4', 'N/A'),
            ])
        
        headers = ['Nome', 'Modelo', 'Site', 'Status', 'IP Principal']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        print(f"\nTotal de dispositivos: {len(devices)}")

if __name__ == '__main__':
    lister = NetboxDeviceLister()
    lister.list_devices()
