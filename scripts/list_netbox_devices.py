#!/usr/bin/env python3
"""
Script: Listar dispositivos do Netbox
Sincroniza com o Netbox via API e exibe todos os dispositivos registrados
"""

import json
import os
import requests
import sys
from urllib.parse import urljoin
from tabulate import tabulate

class NetboxDeviceLister:
    def __init__(self):
        self.netbox_url = os.getenv('NETBOX_URL', 'http://netbox:8000')
        self.netbox_token = os.getenv('NETBOX_TOKEN', '')
    
    def fetch_devices(self):
        """Busca todos os dispositivos do Netbox"""
        url = urljoin(self.netbox_url, '/api/dcim/devices/')
        headers = {'Authorization': f'Token {self.netbox_token}'}
        
        try:
            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.exceptions.RequestException as e:
            print(f"Erro ao conectar com Netbox: {e}", file=sys.stderr)
            return []
    
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
