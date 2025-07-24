#!/usr/bin/env python3
"""
Script para configurar las variables de entorno del NAS Synology.
"""

import os
from pathlib import Path


def setup_synology_env():
    """Configura las variables de entorno del NAS."""
    print("🔧 CONFIGURACIÓN DE VARIABLES DE ENTORNO SYNOLOGY")
    print("=" * 60)
    
    # Verificar si ya existe .env
    env_file = Path(".env")
    if env_file.exists():
        print("📁 Archivo .env ya existe")
        with open(env_file, 'r') as f:
            content = f.read()
            if "SYNOLOGY_IP" in content:
                print("✅ Variables de Synology ya configuradas")
                return True
    
    print("📝 Configurando variables de entorno para Synology NAS...")
    print("\nPor favor, proporciona la siguiente información:")
    
    # Solicitar datos
    host = input("🔗 IP del NAS (ej: 192.168.1.100): ").strip()
    port = input("🔌 Puerto (5000 para HTTP, 5001 para HTTPS): ").strip() or "5000"
    user = input("👤 Usuario: ").strip()
    password = input("🔒 Contraseña: ").strip()
    
    if not all([host, user, password]):
        print("❌ Faltan datos obligatorios")
        return False
    
    # Crear contenido del archivo .env
    env_content = f"""# Configuración de Synology NAS
SYNOLOGY_IP={host}
SYNOLOGY_PORT={port}
SYNOLOGY_USER={user}
SYNOLOGY_PASS={password}
"""
    
    # Escribir archivo .env
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Archivo .env creado exitosamente")
        print(f"📁 Ubicación: {env_file.absolute()}")
        return True
    except Exception as e:
        print(f"❌ Error al crear archivo .env: {e}")
        return False


def show_current_config():
    """Muestra la configuración actual."""
    print("\n📋 CONFIGURACIÓN ACTUAL:")
    print("=" * 30)
    
    host = os.getenv("SYNOLOGY_IP")
    port = os.getenv("SYNOLOGY_PORT")
    user = os.getenv("SYNOLOGY_USER")
    pass_env = os.getenv("SYNOLOGY_PASS")
    
    print(f"Host: {host or 'NO CONFIGURADO'}")
    print(f"Puerto: {port or 'NO CONFIGURADO'}")
    print(f"Usuario: {user or 'NO CONFIGURADO'}")
    print(f"Contraseña: {'*' * len(pass_env) if pass_env else 'NO CONFIGURADO'}")


if __name__ == "__main__":
    show_current_config()
    
    if not all([os.getenv("SYNOLOGY_IP"), os.getenv("SYNOLOGY_USER"), os.getenv("SYNOLOGY_PASS")]):
        print("\n⚠️  Variables de Synology no configuradas")
        setup = input("¿Quieres configurarlas ahora? (s/n): ").lower()
        if setup == 's':
            setup_synology_env()
            print("\n🔄 Recargando configuración...")
            show_current_config()
    else:
        print("\n✅ Configuración completa") 