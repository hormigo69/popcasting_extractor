#!/usr/bin/env python3
"""
Script principal para ejecutar el extractor de Popcasting
"""

from services.popcasting_extractor import PopcastingExtractor

def main():
    """Función principal"""
    print("🎵 Iniciando extractor de Popcasting con parser simplificado...")
    
    # Crear instancia del extractor
    extractor = PopcastingExtractor()
    
    # Ejecutar el proceso completo
    extractor.run()
    
    print("✅ Proceso completado!")

if __name__ == "__main__":
    main() 