#!/usr/bin/env python3
"""
Script principal del sincronizador de WordPress.com.
Orquesta todos los componentes para leer la API de WordPress.com
y guardar los episodios en Supabase.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path para importaciones
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from components.config_manager import ConfigManager
from components.database_manager import DatabaseManager
# from components.rss_data_processor import RSSDataProcessor  # Ya no necesario
# from components.wordpress_data_processor import WordPressDataProcessor  # Ya no necesario
# from components.wordpress_client import WordPressClient  # Ya no necesario
# from components.data_processor import DataProcessor  # Ya no necesario
from components.song_processor import SongProcessor
from components.mp3_manager import MP3Manager
from components.synology_client import SynologyClient
from api.wpcom_api import get_posts, extract_best_mp3_url, extract_ivoox_page_url, get_file_size, extract_cover_image_url, extract_web_extra_links, extract_web_playlist, extract_comments, parse_duration, get_duration_from_mp3
from utils.logger import logger


def _extract_program_number(title: str) -> int | None:
    """
    Extrae el número de programa del título del episodio.
    
    Args:
        title: Título del episodio
        
    Returns:
        int: Número del programa si se encuentra, None si no se encuentra
    """
    import re
    
    # Patrón para buscar números de episodio en el título
    patterns = [
        r'Popcasting\s*#?(\d+)',  # Popcasting #123
        r'Episodio\s*#?(\d+)',    # Episodio #123
        r'#(\d+)',                # #123
        r'(\d+)',                 # Solo número
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except (ValueError, IndexError):
                continue
    
    return None


def main(dry_run: bool = False):
    """
    Función principal que orquesta todo el proceso de sincronización desde WordPress.com.
    
    Args:
        dry_run: Si es True, solo muestra los datos sin procesarlos ni guardarlos
    """
    if dry_run:
        logger.info("🧪 Iniciando sincronizador de WordPress.com en MODO DRY-RUN")
    else:
        logger.info("🚀 Iniciando sincronizador de WordPress.com")
    
    try:
        # Inicialización de componentes
        logger.info("📋 Inicializando componentes...")
        
        # 1. Cargar configuración
        config_manager = ConfigManager()
        supabase_credentials = config_manager.get_supabase_credentials()
        rss_url = config_manager.get_rss_url()
        wordpress_config = config_manager.get_wordpress_config()
        
        logger.info("✅ Configuración cargada correctamente")
        
        # 2. Inicializar gestor de base de datos
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        # 3. Inicializar cliente de WordPress (ya no necesario, usamos wpcom_api)
        # wordpress_client = WordPressClient(wordpress_config['api_url'])
        
        # 4. Inicializar procesadores de datos (ya no necesario, usamos wpcom_api)
        # rss_processor = RSSDataProcessor(rss_url)
        # wordpress_processor = WordPressDataProcessor()
        
        # 5. Inicializar procesador principal (orquestador) - ya no necesario
        # data_processor = DataProcessor(rss_processor, wordpress_processor)
        
        # 6. Inicializar cliente de Synology y gestor de audio
        logger.info("Inicializando cliente de Synology...")
        synology_credentials = config_manager.get_synology_credentials()
        synology_client = SynologyClient(
            host=synology_credentials["ip"],
            port=synology_credentials["port"],
            username=synology_credentials["user"],
            password=synology_credentials["password"]
        )

        # Hacer login al Synology
        if not synology_client.login():
            raise Exception("No se pudo conectar al NAS Synology")

        logger.info("Inicializando gestor de audio...")
        audio_manager = MP3Manager(db_manager, synology_client)
        
        logger.info("✅ Todos los componentes inicializados correctamente")
        
        # Lógica principal de sincronización
        logger.info("🔄 Iniciando proceso de sincronización...")
        
        # 1. Obtener el episodio más reciente de la base de datos
        logger.info("📊 Verificando episodio más reciente en la base de datos...")
        latest_podcast = db_manager.get_latest_podcast()
        
        if latest_podcast:
            latest_program_number = latest_podcast.get('program_number', 0)
            latest_title = latest_podcast.get('title', 'Sin título')
            logger.info(f"📅 Episodio más reciente en BD: {latest_title} (Número: {latest_program_number})")
        else:
            logger.info("📅 No hay episodios en la base de datos, se procesarán todos")
            latest_program_number = 0
        
        # 2. Obtener episodios desde la API de WordPress.com (optimizado)
        logger.info("📻 Obteniendo episodios desde la API de WordPress.com...")
        
        PAGE_SIZE = 20  # Número de posts por página
        all_episodes = []
        page = 1
        found_old_episodes = False
        max_pages_to_check = 10  # Límite de seguridad para evitar bucles infinitos
        
        while True and page <= max_pages_to_check:
            logger.info(f"📄 Obteniendo página {page} de posts...")
            posts = get_posts(page, PAGE_SIZE)
            
            if not posts:
                logger.info(f"📄 No hay más posts en la página {page}")
                break
                
            logger.info(f"📄 Encontrados {len(posts)} posts en la página {page}")
            
            # Verificar si encontramos episodios viejos (ya en BD)
            page_has_new_episodes = False
            for post in posts:
                episode_title = post.get('title', 'Sin título')
                episode_program_number = _extract_program_number(episode_title)
                
                if episode_program_number and episode_program_number > latest_program_number:
                    page_has_new_episodes = True
                    break
            
            if not page_has_new_episodes and latest_program_number > 0:
                logger.info(f"📄 Página {page} solo contiene episodios viejos, parando búsqueda...")
                found_old_episodes = True
                break
            
            if dry_run:
                # En modo dry-run, mostrar detalles de cada post
                for i, post in enumerate(posts, 1):
                    episode_title = post.get('title', 'Sin título')
                    episode_program_number = _extract_program_number(episode_title)
                    is_new = episode_program_number and episode_program_number > latest_program_number
                    
                    logger.info(f"📝 Post {i} de la página {page}:")
                    logger.info(f"   ID: {post.get('id')}")
                    logger.info(f"   Título: {episode_title}")
                    logger.info(f"   Número: {episode_program_number}")
                    logger.info(f"   Es nuevo: {'✅' if is_new else '❌'}")
                    logger.info(f"   Fecha: {post.get('published_at')}")
                    logger.info(f"   URL: {post.get('url')}")
                    logger.info("   " + "="*50)
            
            all_episodes.extend(posts)
            page += 1
        
        if page > max_pages_to_check:
            logger.warning(f"⚠️ Se alcanzó el límite de {max_pages_to_check} páginas, puede haber más episodios nuevos")
        
        logger.info(f"📻 Total de episodios obtenidos desde WordPress.com: {len(all_episodes)}")
        logger.info(f"📄 Páginas revisadas: {page - 1}")
        
        if found_old_episodes:
            logger.info(f"✅ Optimización: Se detuvo la búsqueda al encontrar episodios viejos")
        
        # 3. Filtrar solo episodios nuevos (con número mayor al último en BD)
        new_episodes = []
        if latest_program_number > 0:
            logger.info(f"📊 Comparando por número de episodio: último en BD = {latest_program_number}")
            
            for episode in all_episodes:
                # Extraer número de episodio del título
                episode_title = episode.get('title', 'Sin título')
                episode_program_number = _extract_program_number(episode_title)
                
                if dry_run:
                    logger.info(f"🔍 Analizando episodio: '{episode_title}' -> Número extraído: {episode_program_number}")
                
                if episode_program_number and episode_program_number > latest_program_number:
                    new_episodes.append(episode)
                    logger.debug(f"🆕 Episodio nuevo encontrado: {episode_title} (Número: {episode_program_number})")
                elif episode_program_number and episode_program_number <= latest_program_number:
                    # Los episodios están ordenados por número, podemos parar aquí
                    logger.debug(f"⏭️ Episodio ya existe: {episode_title} (Número: {episode_program_number})")
                    break
            
            logger.info(f"🆕 Encontrados {len(new_episodes)} episodios nuevos para procesar")
        else:
            # Si no hay episodios en BD, procesar todos
            new_episodes = all_episodes
            logger.info(f"🆕 Procesando todos los {len(new_episodes)} episodios (BD vacía)")
        
        # 4. Si no hay episodios nuevos, terminar
        if not new_episodes:
            logger.info("✅ No hay episodios nuevos. Sincronización completada.")
            return
        
        # 5. Procesar solo los episodios nuevos
        logger.info(f"🚀 Procesando {len(new_episodes)} episodios nuevos...")
        
        if dry_run:
            logger.info("🧪 MODO DRY-RUN: Solo mostrando datos, sin procesar ni guardar")
            for i, wp_episode in enumerate(new_episodes, 1):
                episode_title = wp_episode.get('title', 'Sin título')
                episode_date = wp_episode.get('published_at', 'Sin fecha')
                
                logger.info(f"📝 Episodio {i}/{len(new_episodes)}: {episode_title} ({episode_date})")
                
                # Buscar URLs de MP3 en el contenido del post (modo dry-run)
                import re
                content = wp_episode.get('content', '')
                mp3_urls = []
                
                # Buscar URLs de MP3 en el contenido HTML
                mp3_patterns = [
                    r'href=["\']([^"\']*\.mp3[^"\']*)["\']',  # href="...mp3..."
                    r'src=["\']([^"\']*\.mp3[^"\']*)["\']',   # src="...mp3..."
                    r'https?://[^\s<>"\']*\.mp3[^\s<>"\']*',  # URLs directas de MP3
                ]
                
                for pattern in mp3_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    mp3_urls.extend(matches)
                
                # Eliminar duplicados y limpiar URLs
                mp3_urls = list(set(mp3_urls))
                mp3_urls = [url.strip() for url in mp3_urls if url.strip()]
                
                download_url = mp3_urls[0] if mp3_urls else None
                
                # Procesar attachments para convertirlos a formato compatible (modo dry-run)
                attachments = wp_episode.get('attachments', {})
                processed_attachments = []
                
                # Si attachments es un diccionario, convertirlo a lista
                if isinstance(attachments, dict):
                    for attachment_id, attachment_data in attachments.items():
                        if isinstance(attachment_data, dict):
                            processed_attachments.append(attachment_data)
                        else:
                            processed_attachments.append(attachment_data)
                elif isinstance(attachments, list):
                    processed_attachments = attachments
                
                # Mostrar estructura de datos que se crearía
                episode_program_number = _extract_program_number(episode_title)
                episode_data = {
                    'title': episode_title,
                    'date': episode_date,
                    'url': wp_episode.get('url', ''),
                    'content': wp_episode.get('content', ''),
                    'program_number': episode_program_number,
                    'wordpress_playlist_data': processed_attachments,
                    'rss_playlist': '',  # Ya no usamos RSS
                    'wordpress_id': wp_episode.get('id'),
                    'download_url': download_url
                }
                
                logger.info(f"   📊 Datos estructurados:")
                logger.info(f"      - Título: {episode_data['title']}")
                logger.info(f"      - Fecha: {episode_data['date']}")
                logger.info(f"      - URL: {episode_data['url']}")
                logger.info(f"      - Número de programa: {episode_data['program_number']}")
                logger.info(f"      - WordPress ID: {episode_data['wordpress_id']}")
                logger.info(f"      - URL de descarga MP3: {episode_data['download_url'] or 'No encontrada'}")
                logger.info(f"      - Contenido (primeros 150 chars): {episode_data['content'][:150]}...")
                logger.info(f"      - Adjuntos: {len(episode_data['wordpress_playlist_data'])} elementos")
                logger.info("   " + "="*60)
            
            logger.info("🧪 MODO DRY-RUN completado. No se procesaron ni guardaron datos.")
            return
        
        # Contadores para el reporte
        total_new_episodes = len(new_episodes)
        processed_episodes = 0
        error_episodes = 0
        
        # Procesar cada episodio nuevo
        for i, wp_episode in enumerate(new_episodes, 1):
            episode_title = wp_episode.get('title', 'Sin título')
            episode_date = wp_episode.get('published_at', 'Sin fecha')
            
            logger.info(f"📝 Procesando episodio nuevo {i}/{total_new_episodes}: {episode_title} ({episode_date})")
            
            try:
                # Los datos ya vienen de WordPress.com, solo necesitamos adaptarlos al formato esperado
                logger.info(f"🔗 Adaptando datos de WordPress.com para: {episode_title}")
                
                # Extraer número de episodio del título
                episode_program_number = _extract_program_number(episode_title)
                
                # Buscar URLs de MP3 en el contenido del post usando la función mejorada
                content = wp_episode.get('content', '')
                download_url = extract_best_mp3_url(content)  # URL directa del MP3
                ivoox_page_url = extract_ivoox_page_url(content)  # URL de la página de iVoox
                
                if not download_url:
                    logger.warning(f"⚠️ No se encontró URL de MP3 para: {episode_title}")
                    error_episodes += 1
                    continue
                
                if not ivoox_page_url:
                    logger.warning(f"⚠️ No se encontró URL de página de iVoox para: {episode_title}")
                    # Usar la URL de descarga como fallback
                    ivoox_page_url = download_url
                
                logger.info(f"🎵 Encontrada URL de MP3: {download_url}")
                logger.info(f"🔗 Encontrada URL de página iVoox: {ivoox_page_url}")
                
                # Obtener el tamaño del archivo MP3
                file_size = get_file_size(download_url)
                if file_size > 0:
                    # Convertir a MB para mostrar en el log
                    file_size_mb = file_size / (1024 * 1024)
                    logger.info(f"📏 Tamaño del archivo: {file_size_mb:.2f} MB ({file_size:,} bytes)")
                else:
                    logger.warning(f"⚠️ No se pudo obtener el tamaño del archivo")
                    file_size = 0
                
                # Extraer la imagen de portada
                cover_image_url = extract_cover_image_url(content)
                if cover_image_url:
                    logger.info(f"🖼️ Encontrada imagen de portada: {cover_image_url}")
                else:
                    logger.warning(f"⚠️ No se encontró imagen de portada")
                    cover_image_url = None
                
                # Extraer enlaces adicionales
                web_extra_links = extract_web_extra_links(content)
                if web_extra_links:
                    logger.info(f"🔗 Encontrados {len(web_extra_links)} enlaces adicionales")
                    for link in web_extra_links:
                        logger.info(f"   📎 {link['text']} -> {link['url']}")
                else:
                    logger.info(f"🔗 No se encontraron enlaces adicionales")
                
                # Extraer playlist
                web_playlist = extract_web_playlist(content)
                if web_playlist:
                    logger.info(f"🎵 Encontradas {len(web_playlist)} canciones en la playlist")
                    for song in web_playlist[:3]:  # Mostrar solo las primeras 3
                        logger.info(f"   🎶 {song['position']}. {song['artist']} · {song['title']}")
                    if len(web_playlist) > 3:
                        logger.info(f"   ... y {len(web_playlist) - 3} canciones más")
                else:
                    logger.warning(f"⚠️ No se encontró playlist")
                
                # Extraer comentarios del título
                comments = extract_comments(episode_title)
                if comments:
                    logger.info(f"💬 Comentarios extraídos: {comments}")
                else:
                    logger.info(f"💬 No se encontraron comentarios en el título")
                
                # Extraer duración
                duration = None
                
                # Primero intentar obtener duración del MP3
                if download_url:
                    logger.info(f"⏱️ Extrayendo duración del archivo MP3...")
                    duration = get_duration_from_mp3(download_url)
                    if duration:
                        duration_minutes = duration // 60
                        duration_seconds = duration % 60
                        logger.info(f"⏱️ Duración extraída del MP3: {duration_minutes}:{duration_seconds:02d} ({duration} segundos)")
                    else:
                        logger.warning(f"⚠️ No se pudo extraer duración del MP3")
                
                # Si no se pudo extraer del MP3, intentar desde el contenido (si hay)
                if not duration:
                    # Buscar duración en el contenido HTML (si existe)
                    duration_pattern = r'(\d{1,2}):(\d{2})(?::(\d{2}))?'
                    duration_matches = re.findall(duration_pattern, content)
                    if duration_matches:
                        # Tomar la primera coincidencia que parezca una duración válida
                        for match in duration_matches:
                            if len(match) == 3 and match[2]:  # HH:MM:SS
                                hours, minutes, seconds = int(match[0]), int(match[1]), int(match[2])
                                duration = hours * 3600 + minutes * 60 + seconds
                                break
                            elif len(match) == 3 and not match[2]:  # MM:SS
                                minutes, seconds = int(match[0]), int(match[1])
                                duration = minutes * 60 + seconds
                                break
                        
                        if duration:
                            duration_minutes = duration // 60
                            duration_seconds = duration % 60
                            logger.info(f"⏱️ Duración extraída del contenido: {duration_minutes}:{duration_seconds:02d} ({duration} segundos)")
                
                if not duration:
                    logger.warning(f"⚠️ No se pudo extraer duración del episodio")
                
                # Procesar attachments para convertirlos a formato compatible
                attachments = wp_episode.get('attachments', {})
                processed_attachments = []
                
                # Si attachments es un diccionario, convertirlo a lista
                if isinstance(attachments, dict):
                    for attachment_id, attachment_data in attachments.items():
                        if isinstance(attachment_data, dict):
                            processed_attachments.append(attachment_data)
                        else:
                            processed_attachments.append(attachment_data)
                elif isinstance(attachments, list):
                    processed_attachments = attachments
                
                # Crear estructura de datos compatible con la BD
                episode_data = {
                    'title': episode_title,
                    'date': episode_date,
                    'url': ivoox_page_url,  # URL de la página de iVoox
                    'wordpress_link': wp_episode.get('url', ''),  # URL de WordPress
                    'content': wp_episode.get('content', ''),
                    'program_number': episode_program_number,
                    'rss_playlist': '',  # Ya no usamos RSS
                    'wordpress_id': wp_episode.get('id'),
                    'download_url': download_url,  # URL directa del MP3 para descarga
                    'file_size': file_size,  # Tamaño del archivo en bytes
                    'featured_image_url': cover_image_url,  # URL de la imagen de portada
                    'web_extra_links': web_extra_links,  # Enlaces adicionales
                    'web_playlist': web_playlist,  # Playlist de canciones extraída del contenido
                    'comments': comments,  # Comentarios extraídos del título
                    'duration': duration  # Duración en segundos
                }
                
                if not episode_data:
                    logger.warning(f"⚠️ No se pudieron obtener datos para: {episode_title}")
                    error_episodes += 1
                    continue
                
                # Insertar en la base de datos
                logger.info(f"💾 Guardando episodio en la BD: {episode_title}")
                new_podcast_id = db_manager.insert_full_podcast(episode_data)
                
                # Procesar y almacenar canciones con SongProcessor
                stored_songs_count = 0
                try:
                    logger.info(f"🎵 Procesando canciones para: {episode_title}")
                    song_processor = SongProcessor(db_manager)
                    
                    # Extraer canciones de web_playlist
                    web_playlist = episode_data.get('web_playlist')
                    
                    stored_songs_count = song_processor.process_and_store_songs(
                        podcast_id=new_podcast_id,
                        web_playlist=web_playlist,
                        rss_playlist=episode_data.get('rss_playlist')
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Error al procesar canciones para {episode_title}: {e}")
                    logger.warning(f"⚠️ Continuando con el proceso de audio...")
                
                # Iniciar el proceso de archivado de audio
                logger.info(f"🎵 Iniciando el proceso de archivado de audio para el podcast ID: {new_podcast_id}")
                try:
                    audio_success = audio_manager.archive_podcast_audio(podcast_id=new_podcast_id)
                    if audio_success:
                        logger.info(f"✅ Audio archivado exitosamente para: {episode_title}")
                    else:
                        logger.warning(f"⚠️ Error al archivar audio para: {episode_title}")
                except Exception as e:
                    logger.error(f"❌ Error crítico al archivar audio para {episode_title}: {e}")
                
                logger.info(f"✅ Episodio guardado exitosamente: {episode_title} ({stored_songs_count} canciones)")
                processed_episodes += 1
                
            except Exception as e:
                logger.error(f"❌ Error al procesar episodio '{episode_title}': {e}")
                error_episodes += 1
                continue
        
        # Reporte final
        logger.info("📊 === REPORTE FINAL DE SINCRONIZACIÓN ===")
        logger.info(f"📻 Total de episodios en WordPress.com: {len(all_episodes)}")
        logger.info(f"🆕 Episodios nuevos encontrados: {total_new_episodes}")
        logger.info(f"✅ Episodios procesados exitosamente: {processed_episodes}")
        logger.info(f"❌ Episodios con errores: {error_episodes}")
        logger.info("🎉 Sincronización completada")
        
    except Exception as e:
        logger.error(f"❌ Error crítico en la sincronización: {e}")
        raise
    
    finally:
        # Cerrar conexión a la base de datos
        logger.info("🔒 Cerrando conexión a la base de datos...")
        db_manager.close()
        logger.info("✅ Sincronizador finalizado correctamente")


if __name__ == "__main__":
    """
    Punto de entrada principal del sincronizador de WordPress.com.
    """
    import sys
    
    # Verificar si se pasa el argumento --dry-run
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        print("🧪 Ejecutando en MODO DRY-RUN")
        print("   Para ejecutar normalmente, quita el argumento --dry-run")
        print("="*60)
    
    main(dry_run=dry_run)


# source .venv/bin/activate
# python src/main.py

