# Gestor de base de datos para el sincronizador RSS
from supabase import create_client, Client
import logging
import sys
import os
from pathlib import Path

# Agregar el directorio src al path para importaciones
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))


class DatabaseManager:
    """Gestor de base de datos Supabase para el sincronizador RSS."""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        """Inicializa la conexión a Supabase."""
        self.logger = logging.getLogger(__name__)
        
        try:
            # Crear cliente de Supabase
            self.client: Client = create_client(supabase_url, supabase_key)
            self.logger.info("✅ Conexión a Supabase establecida correctamente")
            
        except Exception as e:
            self.logger.error(f"❌ Error al conectar a Supabase: {e}")
            raise
    
    def test_connection(self):
        """Prueba la conexión ejecutando una consulta simple."""
        try:
            # Intentar hacer una consulta simple para verificar la conexión
            result = self.client.table("podcasts").select("id").limit(1).execute()
            self.logger.info("✅ Prueba de conexión a Supabase exitosa")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error en prueba de conexión: {e}")
            raise
    
    def get_table_structure_from_sample(self, table_name: str, limit: int = 1):
        """Obtiene la estructura de una tabla analizando una muestra de datos."""
        try:
            # Obtener una muestra de datos
            result = self.client.table(table_name).select("*").limit(limit).execute()
            
            if not result.data:
                self.logger.warning(f"⚠️ Tabla '{table_name}' está vacía")
                return []
            
            # Analizar la estructura del primer registro
            sample_record = result.data[0]
            structure = []
            
            for column_name, value in sample_record.items():
                # Determinar el tipo de dato
                if value is None:
                    data_type = "unknown"
                elif isinstance(value, bool):
                    data_type = "boolean"
                elif isinstance(value, int):
                    data_type = "integer"
                elif isinstance(value, float):
                    data_type = "numeric"
                elif isinstance(value, str):
                    data_type = "text"
                elif isinstance(value, list):
                    data_type = "json"
                elif isinstance(value, dict):
                    data_type = "jsonb"
                else:
                    data_type = str(type(value).__name__)
                
                structure.append({
                    'column_name': column_name,
                    'data_type': data_type,
                    'sample_value': str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                })
            
            self.logger.info(f"✅ Estructura de tabla '{table_name}' obtenida de muestra")
            return structure
            
        except Exception as e:
            self.logger.error(f"❌ Error al obtener estructura de tabla '{table_name}': {e}")
            return []
    
    def get_table_info(self):
        """Obtiene información completa de las tablas conocidas."""
        tables_info = {}
        known_tables = ["podcasts", "songs"]
        
        for table in known_tables:
            structure = self.get_table_structure_from_sample(table)
            tables_info[table] = structure
            self.logger.info(f"📋 Tabla '{table}': {len(structure)} columnas")
        
        return tables_info
    
    def get_latest_podcast(self) -> dict | None:
        """
        Obtiene el episodio más reciente de la base de datos.
        
        Returns:
            dict: Datos del episodio más reciente o None si no hay episodios
        """
        try:
            # Obtener el episodio con el número más alto (más reciente)
            result = self.client.table('podcasts').select('*').order('program_number', desc=True).limit(1).execute()
            
            if result.data:
                latest_podcast = result.data[0]
                program_number = latest_podcast.get('program_number', 'Sin número')
                title = latest_podcast.get('title', 'Sin título')
                self.logger.info(f"Episodio más reciente en BD: {title} (Número: {program_number})")
                return latest_podcast
            else:
                self.logger.info("No hay episodios en la base de datos")
                return None
                
        except Exception as e:
            self.logger.error(f"Error al obtener el episodio más reciente: {e}")
            return None
    
    def podcast_exists(self, guid: str) -> bool:
        """
        Verifica si un podcast ya existe en la base de datos por su GUID.
        
        Args:
            guid: GUID único del podcast
            
        Returns:
            bool: True si el podcast existe, False en caso contrario
        """
        try:
            result = self.client.table('podcasts').select('id', count='exact').eq('guid', guid).execute()
            count = result.count if hasattr(result, 'count') else len(result.data)
            exists = count > 0
            self.logger.debug(f"Verificando podcast con GUID '{guid}': {'existe' if exists else 'no existe'}")
            return exists
        except Exception as e:
            self.logger.error(f"Error al verificar existencia del podcast con GUID '{guid}': {e}")
            return False
    
    def insert_full_podcast(self, podcast_data: dict) -> int:
        """
        Inserta un podcast completo con sus canciones en la base de datos.
        Operación transaccional que inserta en las tablas 'podcasts' y 'songs'.
        
        Args:
            podcast_data: Diccionario con los datos del podcast y sus canciones
            
        Returns:
            int: ID del podcast insertado
        """
        try:
            # Extraer la lista de canciones pero mantener una copia para la tabla podcasts
            songs = podcast_data.get('web_playlist', [])
            self.logger.info(f"Insertando podcast: {podcast_data.get('title', 'Sin título')}")
            
            # Filtrar solo los campos válidos para la tabla podcasts
            valid_podcast_fields = {
                'title', 'date', 'url', 'download_url', 'file_size', 'program_number', 
                'wordpress_url', 'cover_image_url', 'web_extra_links', 'web_playlist',
                'web_songs_count', 'comments', 'duration', 'rss_playlist'
            }
            
            # Crear diccionario con solo campos válidos y mapeo correcto
            filtered_podcast_data = {}
            
            # Mapeo de campos del procesador a campos de la tabla
            field_mapping = {
                'title': 'title',
                'date': 'date',
                'url': 'url',
                'download_url': 'download_url',
                'file_size': 'file_size',
                'program_number': 'program_number',
                'wordpress_link': 'wordpress_url',
                'featured_image_url': 'cover_image_url',
                'web_extra_links': 'web_extra_links',
                'web_playlist': 'web_playlist',  # Playlist de canciones extraída del contenido
                'comments': 'comments',
                'duration': 'duration',
                'rss_playlist': 'rss_playlist'
            }
            
            for key, value in podcast_data.items():
                if key in field_mapping:
                    db_field = field_mapping[key]
                    filtered_podcast_data[db_field] = value
                else:
                    self.logger.debug(f"Campo '{key}' omitido (no existe en tabla podcasts)")
            
            # Procesar web_playlist y calcular web_songs_count
            if 'web_playlist' in filtered_podcast_data:
                web_playlist_data = filtered_podcast_data['web_playlist']
                
                # Si es un diccionario con estructura anidada, extraer solo las canciones
                if isinstance(web_playlist_data, dict) and 'songs' in web_playlist_data:
                    songs_list = web_playlist_data['songs']
                    # Calcular el número de canciones
                    filtered_podcast_data['web_songs_count'] = len(songs_list) if isinstance(songs_list, list) else 0
                    # Guardar solo la lista de canciones como JSON
                    import json
                    filtered_podcast_data['web_playlist'] = json.dumps(songs_list, ensure_ascii=False)
                    self.logger.info(f"Procesado web_playlist: {filtered_podcast_data['web_songs_count']} canciones")
                
                # Si es una lista directa
                elif isinstance(web_playlist_data, list):
                    filtered_podcast_data['web_songs_count'] = len(web_playlist_data)
                    import json
                    filtered_podcast_data['web_playlist'] = json.dumps(web_playlist_data, ensure_ascii=False)
                    self.logger.info(f"Procesado web_playlist: {filtered_podcast_data['web_songs_count']} canciones")
                
                # Si es un string JSON, intentar parsearlo
                elif isinstance(web_playlist_data, str):
                    try:
                        import json
                        parsed_data = json.loads(web_playlist_data)
                        if isinstance(parsed_data, dict) and 'songs' in parsed_data:
                            songs_list = parsed_data['songs']
                            filtered_podcast_data['web_songs_count'] = len(songs_list) if isinstance(songs_list, list) else 0
                            filtered_podcast_data['web_playlist'] = json.dumps(songs_list, ensure_ascii=False)
                        elif isinstance(parsed_data, list):
                            filtered_podcast_data['web_songs_count'] = len(parsed_data)
                        self.logger.info(f"Procesado web_playlist desde JSON: {filtered_podcast_data.get('web_songs_count', 0)} canciones")
                    except json.JSONDecodeError:
                        self.logger.warning("No se pudo parsear web_playlist como JSON")
                        filtered_podcast_data['web_songs_count'] = 0
                else:
                    self.logger.warning(f"Formato de web_playlist no reconocido: {type(web_playlist_data)}")
                    filtered_podcast_data['web_songs_count'] = 0
            
            # Convertir web_extra_links a JSON string si es una lista
            if 'web_extra_links' in filtered_podcast_data and isinstance(filtered_podcast_data['web_extra_links'], list):
                import json
                filtered_podcast_data['web_extra_links'] = json.dumps(filtered_podcast_data['web_extra_links'], ensure_ascii=False)
            
            # Insertar el podcast en la tabla podcasts
            podcast_result = self.client.table('podcasts').insert(filtered_podcast_data).execute()
            
            if not podcast_result.data:
                raise Exception("No se pudo insertar el podcast en la base de datos")
            
            # Obtener el ID del podcast insertado
            podcast_id = podcast_result.data[0]['id']
            self.logger.info(f"Podcast insertado con ID: {podcast_id}")
            
            # Si hay canciones, insertarlas en la tabla songs
            if songs:
                # Añadir el podcast_id a cada canción
                songs_with_podcast_id = []
                for song in songs:
                    song_copy = song.copy()
                    song_copy['podcast_id'] = podcast_id
                    songs_with_podcast_id.append(song_copy)
                
                # TEMPORALMENTE DESHABILITADO: Insertar todas las canciones de una vez
                # songs_result = self.client.table('songs').insert(songs_with_podcast_id).execute()
                # self.logger.info(f"Insertadas {len(songs_with_podcast_id)} canciones para el podcast {podcast_id}")
                self.logger.info(f"⚠️ Inserción en tabla 'songs' temporalmente deshabilitada. {len(songs_with_podcast_id)} canciones pendientes.")
            else:
                self.logger.info("No hay canciones para insertar")
            
            # Devolver el ID del podcast insertado
            return podcast_id
            
        except Exception as e:
            self.logger.error(f"Error al insertar podcast completo: {e}")
            raise
    
    def close(self):
        """Cierra la conexión a Supabase."""
        # La librería de Supabase maneja automáticamente las conexiones
        self.logger.info("🔒 Conexión a Supabase cerrada")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def get_all_podcasts(self) -> list:
        """
        Obtiene todos los podcasts de la base de datos.
        
        Returns:
            list: Lista de todos los podcasts
        """
        try:
            result = self.client.table('podcasts').select('*').execute()
            podcasts = result.data
            self.logger.info(f"Obtenidos {len(podcasts)} podcasts de la base de datos")
            return podcasts
        except Exception as e:
            self.logger.error(f"Error al obtener todos los podcasts: {e}")
            return []
    
    def get_podcasts_without_rss_playlist(self) -> list:
        """
        Obtiene todos los podcasts que no tienen rss_playlist o lo tienen vacío.
        
        Returns:
            list: Lista de podcasts sin rss_playlist
        """
        try:
            # Obtener podcasts donde rss_playlist es null, vacío o no existe
            result = self.client.table('podcasts').select('*').or_('rss_playlist.is.null,rss_playlist.eq.,rss_playlist.eq.null').execute()
            podcasts = result.data
            self.logger.info(f"Encontrados {len(podcasts)} podcasts sin rss_playlist")
            return podcasts
        except Exception as e:
            self.logger.error(f"Error al obtener podcasts sin rss_playlist: {e}")
            return []
    
    def update_podcast_rss_playlist(self, podcast_id: int, rss_playlist: str) -> bool:
        """
        Actualiza el campo rss_playlist de un podcast específico.
        
        Args:
            podcast_id: ID del podcast a actualizar
            rss_playlist: JSON string con la playlist procesada
            
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        try:
            result = self.client.table('podcasts').update({'rss_playlist': rss_playlist}).eq('id', podcast_id).execute()
            
            if result.data:
                self.logger.info(f"✅ Podcast {podcast_id} actualizado con rss_playlist")
                return True
            else:
                self.logger.warning(f"⚠️ No se pudo actualizar podcast {podcast_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error al actualizar podcast {podcast_id}: {e}")
            return False
    
    def update_podcast_mp3_duration(self, podcast_id: int, duration_in_seconds: float) -> bool:
        """
        Actualiza el campo mp3_duration de un podcast específico.
        
        Args:
            podcast_id: ID del podcast a actualizar
            duration_in_seconds: Duración del archivo MP3 en segundos
            
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        try:
            # Convertir a entero para compatibilidad con la BD
            duration_int = int(round(duration_in_seconds))
            
            result = self.client.table('podcasts').update({'mp3_duration': duration_int}).eq('id', podcast_id).execute()
            
            if result.data:
                self.logger.info(f"✅ Podcast {podcast_id} actualizado con mp3_duration: {duration_int}s")
                return True
            else:
                self.logger.warning(f"⚠️ No se pudo actualizar mp3_duration del podcast {podcast_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error al actualizar mp3_duration del podcast {podcast_id}: {e}")
            return False
    
    def get_podcast_by_program_number(self, program_number: int) -> dict | None:
        """
        Obtiene un podcast específico por su número de programa.
        
        Args:
            program_number: Número del programa a buscar
            
        Returns:
            dict: Datos del podcast o None si no se encuentra
        """
        try:
            result = self.client.table('podcasts').select('*').eq('program_number', program_number).limit(1).execute()
            
            if result.data:
                podcast = result.data[0]
                self.logger.debug(f"Podcast encontrado: #{program_number} - {podcast.get('title', 'Sin título')}")
                return podcast
            else:
                self.logger.debug(f"Podcast no encontrado: #{program_number}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error al buscar podcast #{program_number}: {e}")
            return None
    
    def get_podcast_by_id(self, podcast_id: int) -> dict | None:
        """
        Obtiene un podcast específico por su ID.
        
        Args:
            podcast_id: ID del podcast a buscar
            
        Returns:
            dict: Datos del podcast o None si no se encuentra
        """
        try:
            result = self.client.table('podcasts').select('*').eq('id', podcast_id).limit(1).execute()
            
            if result.data:
                podcast = result.data[0]
                self.logger.debug(f"Podcast encontrado: ID {podcast_id} - {podcast.get('title', 'Sin título')}")
                return podcast
            else:
                self.logger.debug(f"Podcast no encontrado: ID {podcast_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error al buscar podcast ID {podcast_id}: {e}")
            return None
    
    def get_podcasts_by_batch(self, batch_size: int = 50, offset: int = 0) -> list:
        """
        Obtiene podcasts en lotes para procesamiento eficiente.
        
        Args:
            batch_size: Tamaño del lote
            offset: Desplazamiento para paginación
            
        Returns:
            list: Lista de podcasts del lote
        """
        try:
            result = self.client.table('podcasts').select('*').range(offset, offset + batch_size - 1).execute()
            podcasts = result.data
            self.logger.info(f"Obtenidos {len(podcasts)} podcasts (lote {offset//batch_size + 1})")
            return podcasts
        except Exception as e:
            self.logger.error(f"Error al obtener lote de podcasts: {e}")
            return []
    
    def insert_songs_batch(self, songs_data: list) -> int:
        """
        Inserta múltiples canciones en la tabla songs en una sola operación.
        
        Args:
            songs_data: Lista de diccionarios con datos de canciones.
                       Cada diccionario debe contener: podcast_id, title, artist, position
        
        Returns:
            int: Número de canciones insertadas exitosamente
        """
        try:
            if not songs_data:
                self.logger.warning("No hay canciones para insertar")
                return 0
            
            # Validar que todas las canciones tengan los campos requeridos
            required_fields = ['podcast_id', 'title', 'artist', 'position']
            valid_songs = []
            
            for song in songs_data:
                if all(field in song for field in required_fields):
                    valid_songs.append(song)
                else:
                    self.logger.warning(f"Canción omitida por campos faltantes: {song}")
            
            if not valid_songs:
                self.logger.error("No hay canciones válidas para insertar")
                return 0
            
            # Insertar todas las canciones de una vez
            result = self.client.table('songs').insert(valid_songs).execute()
            
            inserted_count = len(result.data) if result.data else 0
            self.logger.info(f"Insertadas {inserted_count} canciones en la tabla songs")
            
            return inserted_count
            
        except Exception as e:
            self.logger.error(f"Error al insertar canciones en lote: {e}")
            return 0

    def export_table_with_pagination(self, table_name: str, page_size: int = 1000) -> list:
        """
        Exporta una tabla completa usando paginación para manejar tablas grandes.
        
        Args:
            table_name: Nombre de la tabla a exportar
            page_size: Tamaño de cada página (default: 1000)
            
        Returns:
            Lista con todos los datos de la tabla
        """
        try:
            self.logger.info(f"Exportando tabla {table_name} con paginación...")
            
            all_data = []
            offset = 0
            
            while True:
                response = (
                    self.client.table(table_name)
                    .select("*")
                    .range(offset, offset + page_size - 1)
                    .execute()
                )
                page_data = response.data
                
                if not page_data:
                    break
                    
                all_data.extend(page_data)
                offset += page_size
                
                self.logger.info(f"  📄 Página {offset//page_size}: {len(page_data)} registros")
            
            self.logger.info(f"✅ Tabla {table_name} exportada: {len(all_data)} registros totales")
            return all_data
            
        except Exception as e:
            self.logger.error(f"❌ Error al exportar tabla {table_name}: {e}")
            raise

    def get_table_count(self, table_name: str) -> int:
        """
        Obtiene el número total de registros en una tabla.
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            Número total de registros
        """
        try:
            response = self.client.table(table_name).select("id").execute()
            return len(response.data)
        except Exception as e:
            self.logger.error(f"❌ Error al contar registros en {table_name}: {e}")
            return 0

    def create_backup(self, output_dir: str = "backups", tables: list = None) -> dict:
        """
        Crea un backup completo de las tablas especificadas.
        
        Args:
            output_dir: Directorio donde guardar el backup
            tables: Lista de tablas a hacer backup (default: ["podcasts", "songs"])
            
        Returns:
            Diccionario con información del backup
        """
        import json
        import csv
        from datetime import datetime
        from pathlib import Path
        
        if tables is None:
            tables = ["podcasts", "songs"]
        
        # Crear directorio de backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(output_dir) / f"backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"🚀 Iniciando backup en {backup_dir}")
        
        backup_info = {
            "timestamp": timestamp,
            "backup_dir": str(backup_dir),
            "tables": {},
            "success": True,
            "errors": []
        }
        
        try:
            # Exportar cada tabla
            for table in tables:
                try:
                    self.logger.info(f"📊 Exportando tabla: {table}")
                    
                    # Obtener datos con paginación
                    data = self.export_table_with_pagination(table)
                    
                    # Guardar como JSON
                    json_file = backup_dir / f"{table}.json"
                    with open(json_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                    
                    # Guardar como CSV si hay datos
                    csv_file = None
                    if data:
                        csv_file = backup_dir / f"{table}.csv"
                        with open(csv_file, "w", newline="", encoding="utf-8") as f:
                            writer = csv.DictWriter(f, fieldnames=data[0].keys())
                            writer.writeheader()
                            writer.writerows(data)
                    
                    backup_info["tables"][table] = {
                        "json_file": str(json_file),
                        "csv_file": str(csv_file) if csv_file else None,
                        "record_count": len(data)
                    }
                    
                    self.logger.info(f"✅ {table}: {len(data)} registros exportados")
                    
                except Exception as e:
                    error_msg = f"Error en tabla {table}: {e}"
                    self.logger.error(error_msg)
                    backup_info["errors"].append(error_msg)
                    backup_info["success"] = False
            
            # Crear archivo de resumen
            summary_file = backup_dir / "resumen.txt"
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(f"Backup Supabase - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Directorio: {backup_dir}\n\n")
                
                for table in tables:
                    count = backup_info["tables"].get(table, {}).get("record_count", 0)
                    f.write(f"{table}: {count} registros\n")
            
            backup_info["summary_file"] = str(summary_file)
            
            if backup_info["success"]:
                self.logger.info(f"✅ Backup completado exitosamente en {backup_dir}")
            else:
                self.logger.warning("⚠️ Backup completado con errores")
            
            return backup_info
            
        except Exception as e:
            error_msg = f"Error fatal durante el backup: {e}"
            self.logger.error(error_msg)
            backup_info["success"] = False
            backup_info["errors"].append(error_msg)
            return backup_info


def test_database_connection():
    """
    Función de prueba para verificar la conexión a la base de datos.
    Se ejecuta cuando se llama directamente este archivo.
    """
    import sys
    import os
    
    # Agregar el directorio padre al path para importar otros módulos
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    sys.path.insert(0, project_root)
    
    try:
        from sincronizador_rss.src.components.config_manager import ConfigManager
        from sincronizador_rss.src.utils.logger import logger
        
        logger.info("--- INICIANDO PRUEBA DE CONEXIÓN A SUPABASE ---")
        
        # 1. Cargar la configuración
        logger.info("Paso 1: Cargando configuración...")
        cfg_manager = ConfigManager()
        supabase_credentials = cfg_manager.get_supabase_credentials()
        logger.info("Credenciales de Supabase cargadas con éxito.")
        
        # 2. Intentar conectar a Supabase
        logger.info("Paso 2: Creando instancia de DatabaseManager para conectar...")
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        # 3. Probar la conexión
        logger.info("Paso 3: Probando la conexión...")
        db_manager.test_connection()
        
        # 4. Obtener información de tablas
        logger.info("Paso 4: Obteniendo información de tablas...")
        tables_info = db_manager.get_table_info()
        
        # 5. Mostrar información
        logger.info("📊 INFORMACIÓN DE TABLAS:")
        for table_name, columns in tables_info.items():
            logger.info(f"\n📋 Tabla: {table_name}")
            for column in columns:
                logger.info(f"  - {column['column_name']}: {column['data_type']} (ejemplo: {column['sample_value']})")
        
        # 6. Cerrar la conexión
        logger.info("Paso 5: Cerrando la conexión...")
        db_manager.close()
        
        logger.info("✅ --- PRUEBA FINALIZADA CON ÉXITO --- ✅")
        return True
        
    except FileNotFoundError as e:
        logger.error(f"❌ ERROR CRÍTICO: No se encontró el archivo de configuración. {e}")
        return False
    except ValueError as e:
        logger.error(f"❌ ERROR CRÍTICO: Faltan variables en el archivo .env. {e}")
        return False
    except Exception as e:
        logger.error(f"❌ ERROR DURANTE LA PRUEBA: {e}")
        return False


if __name__ == "__main__":
    """
    Punto de entrada para ejecutar pruebas directamente desde este archivo.
    Uso: python database_manager.py
    """
    success = test_database_connection()
    exit(0 if success else 1)
