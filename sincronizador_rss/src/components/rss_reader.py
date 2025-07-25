import feedparser
from ..utils.logger import logger


class RSSReader:
    """
    Clase para leer y parsear feeds RSS.
    """
    
    def __init__(self, feed_url: str):
        """
        Inicializa el lector RSS con la URL del feed.
        
        Args:
            feed_url (str): URL del feed RSS a leer
        """
        self.feed_url = feed_url
        logger.info(f"RSSReader inicializado con URL: {feed_url}")
    
    def fetch_entries(self) -> list:
        """
        Descarga y parsea el feed RSS.
        
        Returns:
            list: Lista de entradas del feed RSS
            
        Raises:
            Exception: Si hay un error al acceder o parsear el feed
        """
        try:
            logger.info(f"Descargando feed RSS desde: {self.feed_url}")
            
            # Parsear el feed RSS
            feed = feedparser.parse(self.feed_url)
            
            # Verificar si el feed se descargó correctamente
            if feed.bozo:
                logger.warning(f"El feed RSS tiene problemas de formato: {feed.bozo_exception}")
            
            # Obtener las entradas
            entries = feed.entries
            
            # Registrar información sobre el feed
            logger.info(f"Feed descargado exitosamente. Título: {feed.feed.get('title', 'Sin título')}")
            logger.info(f"Número de entradas encontradas: {len(entries)}")
            
            if entries:
                logger.info(f"Primera entrada: {entries[0].get('title', 'Sin título')}")
                logger.info(f"Última entrada: {entries[-1].get('title', 'Sin título')}")
            
            return entries
            
        except Exception as e:
            error_msg = f"Error al descargar o parsear el feed RSS desde {self.feed_url}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e


if __name__ == "__main__":
    """
    Punto de entrada para pruebas directas del RSSReader.
    """
    import sys
    
    # URL de ejemplo para pruebas (feed RSS de Popcasting)
    test_url = "https://feeds.feedburner.com/popcasting"
    
    # Si se proporciona una URL como argumento, usarla
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    print(f"Probando RSSReader con URL: {test_url}")
    print("-" * 50)
    
    try:
        # Crear instancia del lector RSS
        reader = RSSReader(test_url)
        
        # Obtener las entradas
        entries = reader.fetch_entries()
        
        print(f"\n✅ Prueba exitosa!")
        print(f"📊 Total de entradas: {len(entries)}")
        
        # Mostrar las primeras 3 entradas como ejemplo
        if entries:
            print(f"\n📝 Primeras {min(3, len(entries))} entradas:")
            for i, entry in enumerate(entries[:3], 1):
                title = entry.get('title', 'Sin título')
                published = entry.get('published', 'Sin fecha')
                link = entry.get('link', 'Sin enlace')
                print(f"  {i}. {title}")
                print(f"     📅 {published}")
                print(f"     🔗 {link}")
                print()
        
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        sys.exit(1) 


# Probar con la URL por defecto (Popcasting)
# source .venv/bin/activate
# python src/components/rss_reader.py

# Probar con una URL específica
# python src/components/rss_reader.py https://url_de_tu_feed.com/rss

# Para ver los logs:
# tail -f sincronizador_rss/logs/sincronizador_rss.log


