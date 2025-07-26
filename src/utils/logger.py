# Configuración de logging para el sincronizador RSS
import logging
import sys
from pathlib import Path


def setup_logger(name: str = "sincronizador_rss", level: str = "INFO"):
    """Configura y devuelve un logger personalizado."""
    
    # Crear el logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
    
    # Crear formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo (opcional)
    try:
        # Crear directorio de logs dentro de sincronizador_rss
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_dir / "sincronizador_rss.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"No se pudo configurar el log de archivo: {e}")
    
    return logger


# Crear logger global
logger = setup_logger() 