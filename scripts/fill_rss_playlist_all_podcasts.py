#!/usr/bin/env python3
"""
Script para llenar el campo rss_playlist de todas las filas de la tabla podcasts.
Convierte el texto de la playlist del RSS a formato JSON estructurado.
"""

import sys
import os
import json
import time
from pathlib import Path

# Agregar el directorio src al path para importaciones
current_dir = Path(__file__).parent.parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from components.database_manager import DatabaseManager
from components.config_manager import ConfigManager
from components.rss_data_processor import RSSDataProcessor
from utils.logger import logger


class RSSPlaylistFiller:
    """
    Clase para llenar el campo rss_playlist de todos los podcasts.
    """
    
    def __init__(self):
        """
        Inicializa el procesador de playlist RSS.
        """
        # Cargar configuración
        config_manager = ConfigManager()
        supabase_config = config_manager.get_supabase_credentials()
        
        # Inicializar componentes
        self.db_manager = DatabaseManager(
            supabase_config['url'], 
            supabase_config['key']
        )
        
        # Crear instancia del procesador RSS (solo para usar sus métodos de procesamiento)
        self.rss_processor = RSSDataProcessor("https://feeds.feedburner.com/popcasting")
        
        # Cache para datos del RSS
        self._rss_cache = None
        self._rss_cache_timestamp = None
        
        logger.info("🚀 RSSPlaylistFiller inicializado")
    
    def process_all_podcasts(self, batch_size: int = 50, dry_run: bool = False, max_podcasts: int = None):
        """
        Procesa todos los podcasts y actualiza el campo rss_playlist.
        
        Args:
            batch_size: Tamaño del lote para procesamiento
            dry_run: Si es True, solo muestra qué se haría sin hacer cambios
            max_podcasts: Número máximo de podcasts a procesar (para pruebas)
        """
        try:
            logger.info(f"🔄 Iniciando procesamiento de podcasts (batch_size: {batch_size}, dry_run: {dry_run}, max: {max_podcasts})")
            
            # Obtener total de podcasts
            all_podcasts = self.db_manager.get_all_podcasts()
            
            # Limitar si se especifica max_podcasts
            if max_podcasts:
                all_podcasts = all_podcasts[:max_podcasts]
                logger.info(f"🔢 Limitando procesamiento a {max_podcasts} podcasts")
            
            total_podcasts = len(all_podcasts)
            
            if total_podcasts == 0:
                logger.warning("⚠️ No hay podcasts en la base de datos")
                return
            
            logger.info(f"📊 Total de podcasts a procesar: {total_podcasts}")
            
            # Estadísticas
            stats = {
                'total': total_podcasts,
                'processed': 0,
                'updated': 0,
                'skipped': 0,
                'errors': 0,
                'already_processed': 0
            }
            
            # Procesar en lotes
            for offset in range(0, total_podcasts, batch_size):
                batch_podcasts = all_podcasts[offset:offset + batch_size]
                batch_num = (offset // batch_size) + 1
                total_batches = (total_podcasts + batch_size - 1) // batch_size
                
                logger.info(f"📦 Procesando lote {batch_num}/{total_batches} ({len(batch_podcasts)} podcasts)")
                
                for podcast in batch_podcasts:
                    try:
                        result = self._process_single_podcast(podcast, dry_run)
                        stats[result] += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Error procesando podcast {podcast.get('id', 'N/A')}: {e}")
                        stats['errors'] += 1
                
                # Pausa entre lotes para no sobrecargar la BD
                if batch_num < total_batches:
                    logger.info("⏸️ Pausa entre lotes...")
                    time.sleep(1)
            
            # Mostrar estadísticas finales
            self._show_final_stats(stats, dry_run)
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento masivo: {e}")
            raise
    
    def process_recent_podcasts(self, limit: int = 50, dry_run: bool = False):
        """
        Procesa solo los podcasts más recientes (que probablemente tengan datos en el RSS).
        
        Args:
            limit: Número de podcasts más recientes a procesar
            dry_run: Si es True, solo muestra qué se haría sin hacer cambios
        """
        try:
            logger.info(f"🔄 Procesando {limit} podcasts más recientes (dry_run: {dry_run})")
            
            # Obtener podcasts ordenados por número de programa (más recientes primero)
            all_podcasts = self.db_manager.get_all_podcasts()
            
            # Ordenar por número de programa descendente
            sorted_podcasts = sorted(all_podcasts, key=lambda x: x.get('program_number', 0), reverse=True)
            
            # Tomar solo los más recientes
            recent_podcasts = sorted_podcasts[:limit]
            
            logger.info(f"📊 Procesando {len(recent_podcasts)} podcasts más recientes")
            
            # Estadísticas
            stats = {
                'total': len(recent_podcasts),
                'processed': 0,
                'updated': 0,
                'skipped': 0,
                'errors': 0,
                'already_processed': 0
            }
            
            # Procesar cada podcast
            for i, podcast in enumerate(recent_podcasts, 1):
                try:
                    logger.info(f"🎵 Procesando {i}/{len(recent_podcasts)}: {podcast.get('title', 'Sin título')}")
                    result = self._process_single_podcast(podcast, dry_run)
                    stats[result] += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando podcast {podcast.get('id', 'N/A')}: {e}")
                    stats['errors'] += 1
            
            # Mostrar estadísticas finales
            self._show_final_stats(stats, dry_run)
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento de podcasts recientes: {e}")
            raise
    
    def _process_single_podcast(self, podcast: dict, dry_run: bool) -> str:
        """
        Procesa un podcast individual.
        
        Args:
            podcast: Datos del podcast
            dry_run: Si es True, solo simula el procesamiento
            
        Returns:
            str: Resultado del procesamiento ('updated', 'skipped', 'already_processed', 'errors')
        """
        podcast_id = podcast.get('id')
        title = podcast.get('title', 'Sin título')
        program_number = podcast.get('program_number', 'N/A')
        
        logger.debug(f"🎵 Procesando: {title} (ID: {podcast_id}, Número: {program_number})")
        
        # Verificar si ya tiene rss_playlist procesado
        current_rss_playlist = podcast.get('rss_playlist')
        if current_rss_playlist and self._is_valid_json_playlist(current_rss_playlist):
            logger.debug(f"⏭️ Podcast {podcast_id} ya tiene rss_playlist válido, saltando...")
            return 'already_processed'
        
        # Buscar datos de playlist en otros campos
        playlist_text = self._find_playlist_text(podcast)
        
        if not playlist_text:
            logger.debug(f"⚠️ Podcast {podcast_id} no tiene datos de playlist, saltando...")
            return 'skipped'
        
        # Procesar la playlist
        try:
            processed_playlist = self.rss_processor._process_rss_playlist(playlist_text)
            
            # Verificar que el procesamiento fue exitoso
            if not processed_playlist or processed_playlist == '[]':
                logger.debug(f"⚠️ Podcast {podcast_id} - playlist procesada está vacía, saltando...")
                return 'skipped'
            
            # Verificar que es JSON válido
            try:
                json.loads(processed_playlist)
            except json.JSONDecodeError:
                logger.warning(f"⚠️ Podcast {podcast_id} - JSON inválido generado, saltando...")
                return 'skipped'
            
            # Actualizar en la base de datos
            if not dry_run:
                success = self.db_manager.update_podcast_rss_playlist(podcast_id, processed_playlist)
                if success:
                    logger.info(f"✅ Podcast {podcast_id} actualizado: {len(json.loads(processed_playlist))} canciones")
                    return 'updated'
                else:
                    logger.error(f"❌ Error actualizando podcast {podcast_id}")
                    return 'errors'
            else:
                # En dry_run, solo mostrar qué se haría
                playlist_data = json.loads(processed_playlist)
                logger.info(f"🔍 DRY RUN - Podcast {podcast_id} se actualizaría con {len(playlist_data)} canciones")
                return 'updated'
                
        except Exception as e:
            logger.error(f"❌ Error procesando playlist del podcast {podcast_id}: {e}")
            return 'errors'
    
    def _find_playlist_text(self, podcast: dict) -> str:
        """
        Busca texto de playlist en diferentes campos del podcast.
        
        Args:
            podcast: Datos del podcast
            
        Returns:
            str: Texto de playlist encontrado o cadena vacía
        """
        # Buscar en diferentes campos que podrían contener la playlist
        possible_fields = [
            'rss_playlist',  # Campo actual (podría tener texto sin procesar)
            'summary',       # Campo que podría existir
            'description',   # Campo que podría existir
            'content'        # Campo que podría existir
        ]
        
        for field in possible_fields:
            value = podcast.get(field)
            if value and isinstance(value, str) and len(value.strip()) > 0:
                # Verificar que no es JSON ya procesado
                if not self._is_valid_json_playlist(value):
                    # Verificar que contiene separadores de playlist
                    if '::' in value or '·' in value:
                        logger.debug(f"📝 Encontrada playlist en campo '{field}' para podcast {podcast.get('id')}")
                        return value
        
        # Si no encontramos datos en la BD, intentar obtener del RSS actual
        program_number = podcast.get('program_number')
        if program_number:
            logger.debug(f"🔍 Buscando datos del RSS para programa {program_number}")
            rss_data = self._get_playlist_from_rss(program_number)
            if rss_data:
                return rss_data
        
        return ""
    
    def _get_playlist_from_rss(self, program_number: int) -> str:
        """
        Intenta obtener datos de playlist del RSS actual para un programa específico.
        
        Args:
            program_number: Número del programa
            
        Returns:
            str: Texto de playlist o cadena vacía
        """
        try:
            # Usar cache del RSS si está disponible
            episodes = self._get_rss_episodes()
            
            # Buscar el episodio por número de programa
            for episode in episodes:
                if episode.get('program_number') == program_number:
                    # Obtener el texto original del RSS (antes del procesamiento)
                    # Necesitamos acceder al summary original, no al rss_playlist ya procesado
                    logger.debug(f"🎵 Encontrado episodio {program_number} en RSS")
                    # Buscar en campos que podrían contener el texto original
                    original_text = episode.get('summary', '') or episode.get('description', '') or episode.get('content', '')
                    if original_text and not self._is_valid_json_playlist(original_text):
                        return original_text
            
            logger.debug(f"⚠️ Episodio {program_number} no encontrado en RSS actual")
            return ""
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos del RSS para programa {program_number}: {e}")
            return ""
    
    def _get_rss_episodes(self) -> list:
        """
        Obtiene los episodios del RSS con cache para evitar descargas repetidas.
        
        Returns:
            list: Lista de episodios del RSS
        """
        import time
        
        # Verificar si el cache es válido (menos de 5 minutos)
        current_time = time.time()
        if (self._rss_cache is not None and 
            self._rss_cache_timestamp is not None and 
            current_time - self._rss_cache_timestamp < 300):  # 5 minutos
            
            logger.debug("📦 Usando cache del RSS")
            return self._rss_cache
        
        # Descargar RSS y actualizar cache
        logger.info("📡 Descargando RSS para obtener datos de playlist...")
        self._rss_cache = self.rss_processor.fetch_and_process_entries()
        self._rss_cache_timestamp = current_time
        
        logger.info(f"✅ RSS descargado: {len(self._rss_cache)} episodios")
        return self._rss_cache
    
    def _is_valid_json_playlist(self, text: str) -> bool:
        """
        Verifica si un texto es una playlist JSON válida ya procesada.
        
        Args:
            text: Texto a verificar
            
        Returns:
            bool: True si es JSON válido de playlist
        """
        if not text or not isinstance(text, str):
            return False
        
        try:
            data = json.loads(text)
            # Verificar que es una lista y tiene la estructura esperada
            if isinstance(data, list) and len(data) > 0:
                # Verificar que el primer elemento tiene la estructura esperada
                first_item = data[0]
                if isinstance(first_item, dict) and 'position' in first_item and 'artist' in first_item and 'title' in first_item:
                    return True
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
        
        return False
    
    def _show_final_stats(self, stats: dict, dry_run: bool):
        """
        Muestra estadísticas finales del procesamiento.
        
        Args:
            stats: Diccionario con estadísticas
            dry_run: Si fue un dry run
        """
        logger.info("📊 === ESTADÍSTICAS FINALES ===")
        logger.info(f"📻 Total de podcasts: {stats['total']}")
        logger.info(f"✅ Procesados exitosamente: {stats['processed']}")
        logger.info(f"🔄 Actualizados: {stats['updated']}")
        logger.info(f"⏭️ Ya procesados: {stats['already_processed']}")
        logger.info(f"⚠️ Saltados: {stats['skipped']}")
        logger.info(f"❌ Errores: {stats['errors']}")
        
        if dry_run:
            logger.info("🔍 MODO DRY RUN - No se realizaron cambios en la base de datos")
        else:
            logger.info("🎉 Procesamiento completado")
    
    def close(self):
        """
        Cierra las conexiones.
        """
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
        logger.info("🔒 Conexiones cerradas")


def main():
    """
    Función principal del script.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Llenar campo rss_playlist de todos los podcasts')
    parser.add_argument('--batch-size', type=int, default=50, 
                       help='Tamaño del lote para procesamiento (default: 50)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Ejecutar en modo simulación sin hacer cambios')
    parser.add_argument('--verbose', action='store_true',
                       help='Mostrar logs detallados')
    parser.add_argument('--max-podcasts', type=int,
                       help='Número máximo de podcasts a procesar (para pruebas)')
    parser.add_argument('--recent-only', type=int, metavar='LIMIT',
                       help='Procesar solo los N podcasts más recientes')
    
    args = parser.parse_args()
    
    # Configurar nivel de logging
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        logger.info("🚀 Iniciando script de llenado de rss_playlist")
        
        # Crear instancia del procesador
        filler = RSSPlaylistFiller()
        
        # Procesar podcasts según las opciones
        if args.recent_only:
            filler.process_recent_podcasts(
                limit=args.recent_only,
                dry_run=args.dry_run
            )
        else:
            filler.process_all_podcasts(
                batch_size=args.batch_size,
                dry_run=args.dry_run,
                max_podcasts=args.max_podcasts
            )
        
        logger.info("✅ Script completado exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error en el script: {e}")
        sys.exit(1)
    finally:
        if 'filler' in locals():
            filler.close()


if __name__ == "__main__":
    main() 