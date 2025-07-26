"""
Ejemplo práctico de uso del SongProcessor.
Muestra cómo integrar el componente en el sistema existente.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para importaciones
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))

from src.components.song_processor import SongProcessor
from sincronizador_rss.src.components.database_manager import DatabaseManager
from sincronizador_rss.src.components.config_manager import ConfigManager
from sincronizador_rss.src.utils.logger import logger


def ejemplo_procesamiento_episodio():
    """
    Ejemplo de cómo procesar las canciones de un episodio usando SongProcessor.
    """
    print("🎵 EJEMPLO: PROCESAMIENTO DE EPISODIO")
    print("=" * 50)
    
    try:
        # 1. Configurar componentes
        config_manager = ConfigManager()
        supabase_credentials = config_manager.get_supabase_credentials()
        
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        song_processor = SongProcessor(db_manager)
        
        # 2. Simular datos de un episodio
        podcast_id = 123
        titulo_episodio = "Popcasting #253 - Música para el verano"
        
        # Datos del RSS (texto plano)
        rss_playlist = """
        the beatles · rain  ::  the doors · wintertime love  ::  joni mitchell · don't interrupt the sorrow
        
        :::::: invita a Popcasting a café https://ko-fi.com/popcasting
        """
        
        # Datos de WordPress (ya procesados)
        web_playlist = [
            {"position": 1, "artist": "the beatles", "title": "rain"},
            {"position": 2, "artist": "the doors", "title": "wintertime love"},
            {"position": 3, "artist": "joni mitchell", "title": "don't interrupt the sorrow"},
            {"position": 4, "artist": "tom petty", "title": "free fallin'"},
            {"position": 5, "artist": "fleetwood mac", "title": "go your own way"}
        ]
        
        print(f"📻 Procesando episodio: {titulo_episodio}")
        print(f"   ID del podcast: {podcast_id}")
        print(f"   Playlist RSS: {len(rss_playlist)} caracteres")
        print(f"   Playlist Web: {len(web_playlist)} canciones")
        
        # 3. Procesar canciones (SongProcessor decide automáticamente qué usar)
        canciones_almacenadas = song_processor.process_and_store_songs(
            podcast_id=podcast_id,
            web_playlist=web_playlist,
            rss_playlist=rss_playlist
        )
        
        print(f"\n✅ Resultado: {canciones_almacenadas} canciones almacenadas")
        
        # 4. Verificar qué playlist se usó
        if web_playlist:
            print("   ℹ️ Se usó la playlist web (prioridad)")
        else:
            print("   ℹ️ Se usó la playlist RSS (fallback)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en el ejemplo: {e}")
        logger.error(f"Error en ejemplo_procesamiento_episodio: {e}")
        return False
    
    finally:
        if 'db_manager' in locals():
            db_manager.close()


def ejemplo_solo_rss():
    """
    Ejemplo cuando solo hay datos del RSS disponibles.
    """
    print("\n📡 EJEMPLO: SOLO DATOS RSS")
    print("=" * 40)
    
    try:
        # Configurar componentes
        config_manager = ConfigManager()
        supabase_credentials = config_manager.get_supabase_credentials()
        
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        song_processor = SongProcessor(db_manager)
        
        # Simular episodio solo con RSS
        podcast_id = 456
        rss_playlist = """
        led zeppelin · stairway to heaven  ::  pink floyd · wish you were here  ::  
        the rolling stones · paint it black  ::  queen · bohemian rhapsody
        
        :::::: invita a Popcasting a café https://ko-fi.com/popcasting
        """
        
        print(f"📻 Procesando episodio solo con RSS (ID: {podcast_id})")
        
        # Procesar (solo RSS disponible)
        canciones_almacenadas = song_processor.process_and_store_songs(
            podcast_id=podcast_id,
            rss_playlist=rss_playlist
        )
        
        print(f"✅ Resultado: {canciones_almacenadas} canciones almacenadas desde RSS")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en el ejemplo RSS: {e}")
        return False
    
    finally:
        if 'db_manager' in locals():
            db_manager.close()


def ejemplo_validacion_canciones():
    """
    Ejemplo de validación de canciones.
    """
    print("\n🔍 EJEMPLO: VALIDACIÓN DE CANCIONES")
    print("=" * 45)
    
    try:
        # Configurar componentes
        config_manager = ConfigManager()
        supabase_credentials = config_manager.get_supabase_credentials()
        
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        song_processor = SongProcessor(db_manager)
        
        # Canciones de prueba con diferentes problemas
        canciones_prueba = [
            {"artist": "the beatles", "title": "hey jude"},  # ✅ Válida
            {"artist": "http://spam.com", "title": "advertisement"},  # ❌ URL
            {"artist": "popcasting", "title": "podcast info"},  # ❌ Palabra clave
            {"artist": "a", "title": "b"},  # ❌ Muy corta
            {"artist": "led zeppelin", "title": "stairway to heaven"},  # ✅ Válida
            {"artist": "www.malicious.com", "title": "fake song"},  # ❌ URL
        ]
        
        print("Validando canciones de prueba:")
        
        canciones_validas = []
        for i, cancion in enumerate(canciones_prueba, 1):
            es_valida = song_processor.validate_song_data(cancion)
            estado = "✅ Válida" if es_valida else "❌ Inválida"
            print(f"   {i}. {estado} - {cancion['artist']} - {cancion['title']}")
            
            if es_valida:
                canciones_validas.append(cancion)
        
        print(f"\n📊 Resumen: {len(canciones_validas)}/{len(canciones_prueba)} canciones válidas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en validación: {e}")
        return False
    
    finally:
        if 'db_manager' in locals():
            db_manager.close()


def ejemplo_parseo_avanzado():
    """
    Ejemplo de parseo avanzado con diferentes formatos.
    """
    print("\n🎼 EJEMPLO: PARSEO AVANZADO")
    print("=" * 35)
    
    try:
        # Configurar componentes
        config_manager = ConfigManager()
        supabase_credentials = config_manager.get_supabase_credentials()
        
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        song_processor = SongProcessor(db_manager)
        
        # Diferentes formatos de texto de canciones
        formatos_prueba = [
            "the beatles · hey jude",
            "pink floyd • wish you were here",
            "led zeppelin - stairway to heaven",
            "queen: bohemian rhapsody",
            'the rolling stones "paint it black"',
            "invalid text without separator",
            "very long artist name that exceeds the limit • very long song title that also exceeds the limit and should be rejected",
        ]
        
        print("Probando diferentes formatos de parseo:")
        
        for i, formato in enumerate(formatos_prueba, 1):
            resultado = song_processor._parse_song_text(formato)
            if resultado:
                print(f"   {i}. ✅ '{formato}' -> {resultado['artist']} - {resultado['title']}")
            else:
                print(f"   {i}. ❌ '{formato}' -> No válido")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en parseo avanzado: {e}")
        return False
    
    finally:
        if 'db_manager' in locals():
            db_manager.close()


if __name__ == "__main__":
    """Ejecutar todos los ejemplos."""
    print("🚀 EJEMPLOS DE USO DEL SONGPROCESSOR")
    print("=" * 60)
    
    # Ejecutar ejemplos
    ejemplos = [
        ejemplo_procesamiento_episodio,
        ejemplo_solo_rss,
        ejemplo_validacion_canciones,
        ejemplo_parseo_avanzado
    ]
    
    exitosos = 0
    total = len(ejemplos)
    
    for ejemplo in ejemplos:
        try:
            if ejemplo():
                exitosos += 1
        except Exception as e:
            print(f"❌ Error ejecutando {ejemplo.__name__}: {e}")
    
    # Resumen
    print(f"\n📊 RESUMEN DE EJEMPLOS")
    print("=" * 30)
    print(f"Ejemplos exitosos: {exitosos}/{total}")
    
    if exitosos == total:
        print("🎉 ¡Todos los ejemplos se ejecutaron correctamente!")
        exit(0)
    else:
        print("⚠️ Algunos ejemplos fallaron. Revisar los errores arriba.")
        exit(1) 