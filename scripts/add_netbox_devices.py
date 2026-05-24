#!/usr/bin/env python3
"""
Script: Adicionar dispositivos ao Netbox
Permite adicionar novos dispositivos via API de forma programática
"""

import json
import os
import requests
import sys
from urllib.parse import urljoin

class NetboxDeviceAdder:
    def __init__(self):
        self.netbox_url = os.getenv('NETBOX_URL', 'http://netbox:8000')
        self.netbox_token = os.getenv('NETBOX_TOKEN', '')
    
    def add_device(self, device_data):
        """Adiciona um novo dispositivo ao Netbox"""
        url = urljoin(self.netbox_url, '/api/dcim/devices/')
        headers = {
            'Authorization': f'Token {self.netbox_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=device_data,
                verify=False
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao adicionar dispositivo: {e}", file=sys.stderr)
            if response.text:
                print(f"Resposta: {response.text}", file=sys.stderr)
            return None
    
    def add_from_json(self, json_file):
        """Adiciona dispositivos a partir de arquivo JSON"""
        try:
            with open(json_file, 'r') as f:
                devices = json.load(f)
            
            if not isinstance(devices, list):
                devices = [devices]
            
            for device in devices:
                print(f"Adicionando dispositivo: {device.get('name')}")
                result = self.add_device(device)
                if result:
                    print(f"  ✓ Dispositivo adicionado com sucesso (ID: {result.get('id')})")
                else:
                    print(f"  ✗ Falha ao adicionar dispositivo")
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {json_file}", file=sys.stderr)
        except json.JSONDecodeError:
            print(f"Erro ao decodificar JSON: {json_file}", file=sys.stderr)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 add_netbox_devices.py <arquivo.json>")
        sys.exit(1)
    
    adder = NetboxDeviceAdder()
    adder.add_from_json(sys.argv[1])
