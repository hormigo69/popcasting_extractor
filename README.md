# Sincronizador RSS

Sincronizador independiente para extraer y procesar feeds RSS de podcasts, con integración a Supabase y WordPress.

## 🎯 Propósito

Este sincronizador está diseñado para:
- Leer feeds RSS de podcasts
- Extraer información de episodios y canciones
- Sincronizar datos con Supabase
- Integrar con APIs de WordPress
- Procesar y normalizar datos de forma automática
- **Descargar archivos MP3 y extraer duración exacta**
- **Subir archivos al NAS Synology**
- **Gestionar metadatos de audio de forma precisa**

## 📁 Estructura del Proyecto

```
sincronizador_rss/
├── README.md                     # Este archivo
├── config.ini                    # Configuración del sincronizador
├── requirements.txt              # Dependencias Python
├── docs/                         # Documentación técnica
├── logs/                         # Archivos de log
├── tests/                        # Scripts de prueba
└── src/
    ├── components/               # Componentes principales
    │   ├── config_manager.py     # Gestor de configuración
    │   ├── database_manager.py   # Gestor de base de datos
    │   ├── data_processor.py     # Procesador de datos
    │   ├── rss_reader.py         # Lector de RSS
    │   ├── audio_manager.py      # Gestor de audio (descarga + duración)
    │   ├── synology_client.py    # Cliente para NAS Synology
    │   └── wordpress_client.py   # Cliente de WordPress
    ├── utils/                    # Utilidades
    │   └── logger.py             # Sistema de logging
    └── main.py                   # Punto de entrada principal
```

## 🚀 Instalación

1. **Clonar o copiar el proyecto**
2. **Instalar dependencias:**
   ```bash
   cd sincronizador_rss
   pip install -r requirements.txt
   ```

3. **Instalar ffprobe (requerido para extracción de duración de audio):**
   ```bash
   # macOS con Homebrew
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # Windows (usando Chocolatey)
   choco install ffmpeg
   ```

4. **Configurar variables de entorno:**
   - Crear archivo `.env` en el directorio padre con las credenciales de Supabase:
   ```env
   supabase_project_url=https://tu-proyecto.supabase.co
   supabase_api_key=tu-api-key
   ```

5. **Configurar config.ini:**
   - Editar `config.ini` con las URLs de RSS y WordPress

## 🧪 Prueba de Conexión

Para verificar que todo funciona correctamente:

```bash
# Prueba básica de conexión
python test_connection.py

# Prueba de extracción de duración de audio
python tests/test_audio_duration.py

# Prueba completa del AudioManager
python tests/test_audio_manager_complete.py
```

Estos scripts probarán:
- ✅ Carga de configuración
- ✅ Conexión a Supabase
- ✅ Lectura de credenciales
- ✅ Extracción de duración de archivos MP3
- ✅ Funcionalidad completa del AudioManager

## 📖 Documentación

- **`docs/`**: Documentación técnica detallada
  - `AUDIO_MANAGER_IMPROVEMENTS.md`: Mejoras en AudioManager
- **`logs/`**: Archivos de log para debugging
- **`config.ini`**: Configuración del sistema

## 🔧 Configuración

### Variables de Entorno Requeridas (.env)
- `supabase_project_url`: URL del proyecto Supabase
- `supabase_api_key`: API key de Supabase

### Configuración RSS (config.ini)
- `[rss].url`: URL del feed RSS a procesar

### Configuración WordPress (config.ini)
- `[wordpress].url`: URL base del sitio WordPress

## 📝 Uso

```python
from src.components.config_manager import ConfigManager
from src.components.database_manager import DatabaseManager

# Cargar configuración
config = ConfigManager()

# Conectar a Supabase
db = DatabaseManager(
    supabase_url=config.get_supabase_credentials()["url"],
    supabase_key=config.get_supabase_credentials()["key"]
)
```

## 🛠️ Desarrollo

El proyecto está diseñado para ser modular y extensible:

- **Componentes**: Cada funcionalidad está en su propio módulo
- **Configuración**: Centralizada en `config.ini` y variables de entorno
- **Logging**: Sistema de logs integrado para debugging
- **Base de datos**: Integración con Supabase para persistencia

## 📄 Licencia

Este proyecto es parte del sistema de extracción de Popcasting. 