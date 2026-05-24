#!/usr/bin/env python3
"""
Script: Adicionar dispositivos ao Netbox
Importa dispositivos via arquivo JSON para API do Netbox
"""

import json
import logging
import os
import requests
import sys
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s', stream=sys.stderr)
logger = logging.getLogger(__name__)

class NetboxDeviceAdder:
    def __init__(self):
        self.netbox_url = os.getenv('NETBOX_URL', 'http://netbox:8000')
        self.netbox_token = os.getenv('NETBOX_TOKEN', '')
        
        if not self.netbox_token:
            logger.error("NETBOX_TOKEN não definido")
            sys.exit(1)
    
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
                verify=False,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error("Timeout na conexão com Netbox")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP {response.status_code}: {response.text}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de conexão: {e}")
            return None
    
    def add_from_json(self, json_file):
        """Adiciona dispositivos a partir de arquivo JSON"""
        if not os.path.exists(json_file):
            logger.error(f"Arquivo não encontrado: {json_file}")
            sys.exit(1)
        
        try:
            with open(json_file, 'r') as f:
                devices = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"JSON inválido em {json_file}: {e}")
            sys.exit(1)
        
        if not isinstance(devices, list):
            devices = [devices]
        
        success_count = 0
        for device in devices:
            name = device.get('name', 'unknown')
            logger.info(f"Adicionando: {name}")
            result = self.add_device(device)
            if result:
                logger.info(f"  Sucesso (ID: {result.get('id')})")
                success_count += 1
            else:
                logger.warning(f"  Falha ao adicionar {name}")
        
        logger.info(f"\nResumo: {success_count}/{len(devices)} dispositivos adicionados")
        return success_count == len(devices)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 add_netbox_devices.py <arquivo.json>")
        sys.exit(1)
    
    adder = NetboxDeviceAdder()
    success = adder.add_from_json(sys.argv[1])
    sys.exit(0 if success else 1)
