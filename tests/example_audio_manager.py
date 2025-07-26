#!/usr/bin/env python3
"""
Ejemplo de uso del componente AudioManager.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para importaciones
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.components.audio_manager import AudioManager
from services.supabase_database import SupabaseDatabase
from synology.synology_client import SynologyClient
import logging

def setup_logger():
    """Configura un logger simple para los ejemplos."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def example_audio_manager_usage():
    """Ejemplo de uso del AudioManager."""
    print("=== EJEMPLO DE USO DE AUDIO MANAGER ===\n")
    
    # Configurar logging
    logger = setup_logger()
    
    try:
        # 1. Inicializar componentes
        logger.info("📋 Inicializando componentes...")
        
        # Database Manager
        db_manager = SupabaseDatabase()
        logger.info("✅ DatabaseManager inicializado")
        
        # Synology Client
        synology_client = SynologyClient()
        if not synology_client.login():
            raise Exception("No se pudo conectar al NAS Synology")
        logger.info("✅ SynologyClient inicializado")
        
        # 2. Crear AudioManager
        audio_manager = AudioManager(db_manager, synology_client)
        logger.info("✅ AudioManager inicializado")
        
        # 3. Ejemplo: Archivar audio de un podcast específico
        podcast_id = 1  # Cambiar por un ID real de tu base de datos
        
        logger.info(f"🔄 Procesando podcast ID: {podcast_id}")
        
        # Usar context manager para limpieza automática
        with audio_manager:
            success = audio_manager.archive_podcast_audio(podcast_id)
            
            if success:
                logger.info(f"🎉 Podcast {podcast_id} archivado exitosamente")
                
                # Verificar que se actualizó en la base de datos
                podcast = db_manager.get_podcast_by_id(podcast_id)
                if podcast and podcast.get('nas_path'):
                    logger.info(f"📁 Ruta en NAS: {podcast['nas_path']}")
                else:
                    logger.warning("⚠️ No se encontró la ruta del NAS en la base de datos")
            else:
                logger.error(f"❌ Error al archivar podcast {podcast_id}")
        
        # 4. Cerrar conexiones
        synology_client.logout()
        logger.info("✅ Conexiones cerradas")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Error en el ejemplo: {e}")
        return False


def example_batch_processing():
    """Ejemplo de procesamiento por lotes."""
    print("\n=== EJEMPLO DE PROCESAMIENTO POR LOTES ===\n")
    
    logger = setup_logger()
    
    try:
        # Inicializar componentes
        db_manager = SupabaseDatabase()
        synology_client = SynologyClient()
        
        if not synology_client.login():
            raise Exception("No se pudo conectar al NAS Synology")
        
        audio_manager = AudioManager(db_manager, synology_client)
        
        # Obtener podcasts con download_url
        all_podcasts = db_manager.get_all_podcasts()
        podcasts_with_download = [
            p for p in all_podcasts 
            if p.get('download_url') and p.get('program_number')
        ]
        
        logger.info(f"📊 Encontrados {len(podcasts_with_download)} podcasts con URL de descarga")
        
        # Procesar los primeros 5 podcasts como ejemplo
        podcasts_to_process = podcasts_with_download[:5]
        
        with audio_manager:
            for podcast in podcasts_to_process:
                podcast_id = podcast['id']
                title = podcast.get('title', 'Sin título')
                
                logger.info(f"🔄 Procesando: {title} (ID: {podcast_id})")
                
                success = audio_manager.archive_podcast_audio(podcast_id)
                
                if success:
                    logger.info(f"✅ {title} archivado exitosamente")
                else:
                    logger.error(f"❌ Error al archivar {title}")
        
        synology_client.logout()
        logger.info("✅ Procesamiento por lotes completado")
        
    except Exception as e:
        logger.error(f"❌ Error en procesamiento por lotes: {e}")


def example_check_podcasts_in_nas():
    """Ejemplo de verificación de podcasts en el NAS."""
    print("\n=== EJEMPLO: VERIFICACIÓN DE PODCASTS EN NAS ===")
    
    logger = setup_logger()
    
    try:
        # Inicializar componentes
        db_manager = SupabaseDatabase()
        synology_client = SynologyClient()
        
        if not synology_client.login():
            raise Exception("No se pudo conectar al NAS Synology")
        
        audio_manager = AudioManager(db_manager, synology_client)
        
        # Obtener algunos podcasts de ejemplo
        podcasts = db_manager.get_all_podcasts()[:10]
        
        logger.info("🔍 Verificando podcasts en el NAS:")
        
        for podcast in podcasts:
            program_number = podcast.get('program_number')
            title = podcast.get('title', 'Sin título')
            
            if program_number:
                nas_path = audio_manager.get_nas_path_for_podcast(program_number)
                exists = audio_manager.check_podcast_in_nas(program_number)
                
                status = "✅ Existe" if exists else "❌ No existe"
                logger.info(f"   {program_number:3d} - {title[:40]:40} {status}")
                logger.info(f"      Ruta: {nas_path}")
        
        synology_client.logout()
        logger.info("✅ Verificación completada")
        
    except Exception as e:
        logger.error(f"❌ Error en verificación: {e}")


if __name__ == "__main__":
    print("🎵 AudioManager - Gestor de Audio para Podcasts")
    print("=" * 50)
    
    # Ejecutar ejemplo básico
    success = example_audio_manager_usage()
    
    if success:
        # Ejecutar ejemplo de procesamiento por lotes
        example_batch_processing()
        
        # Ejecutar ejemplo de verificación
        example_check_podcasts_in_nas()
    
    print("\n🎉 Ejemplos completados") 