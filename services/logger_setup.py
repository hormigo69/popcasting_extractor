import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
LOG_FILE = "parsing_errors.log"
STATS_LOG_FILE = "extraction_stats.log"

def setup_parser_logger():
    """
    Configura y devuelve un logger para registrar errores de parsing.
    Los errores se guardarán en 'logs/parsing_errors.log'.
    """
    # Crear el directorio de logs si no existe
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Configurar el logger
    logger = logging.getLogger('parser_errors')
    logger.setLevel(logging.WARNING)

    # Evitar que se añadan múltiples handlers si la función se llama varias veces
    if logger.hasHandlers():
        return logger

    # Crear un handler que rota los logs cuando alcanzan 1MB, manteniendo 3 archivos de backup.
    handler = RotatingFileHandler(
        os.path.join(LOG_DIR, LOG_FILE), 
        maxBytes=1024*1024, 
        backupCount=3,
        encoding='utf-8'
    )
    
    # Formato del log
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - Podcast: %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Añadir el handler al logger
    logger.addHandler(handler)
    
    return logger

def setup_stats_logger():
    """
    Configura y devuelve un logger para registrar estadísticas del proceso de extracción.
    Las estadísticas se guardarán en 'logs/extraction_stats.log'.
    """
    # Crear el directorio de logs si no existe
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Configurar el logger
    logger = logging.getLogger('extraction_stats')
    logger.setLevel(logging.INFO)

    # Evitar que se añadan múltiples handlers si la función se llama varias veces
    if logger.hasHandlers():
        return logger

    # Crear un handler que rota los logs cuando alcanzan 1MB, manteniendo 3 archivos de backup.
    handler = RotatingFileHandler(
        os.path.join(LOG_DIR, STATS_LOG_FILE), 
        maxBytes=1024*1024, 
        backupCount=3,
        encoding='utf-8'
    )
    
    # Formato del log
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Añadir el handler al logger
    logger.addHandler(handler)
    
    return logger 