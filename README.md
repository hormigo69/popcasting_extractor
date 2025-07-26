# Sincronizador RSS

Sincronizador independiente para extraer y procesar feeds RSS de podcasts, con integración a Supabase y WordPress.

## 🎯 Propósito

Este sincronizador está diseñado para:
- Leer feeds RSS de podcasts
- Extraer información de episodios y canciones
- Sincronizar datos con Supabase
- Integrar con APIs de WordPress
- Procesar y normalizar datos de forma automática

## 📁 Estructura del Proyecto

```
sincronizador_rss/
├── README.md                     # Este archivo
├── config.ini                    # Configuración del sincronizador
├── requirements.txt              # Dependencias Python
├── docs/                         # Documentación técnica
├── logs/                         # Archivos de log
└── src/
    ├── components/               # Componentes principales
    │   ├── config_manager.py     # Gestor de configuración
    │   ├── database_manager.py   # Gestor de base de datos
    │   ├── data_processor.py     # Procesador de datos
    │   ├── rss_reader.py         # Lector de RSS
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

3. **Configurar variables de entorno:**
   - Crear archivo `.env` en el directorio padre con las credenciales de Supabase:
   ```env
   supabase_project_url=https://tu-proyecto.supabase.co
   supabase_api_key=tu-api-key
   ```

4. **Configurar config.ini:**
   - Editar `config.ini` con las URLs de RSS y WordPress

## 🧪 Prueba de Conexión

Para verificar que todo funciona correctamente:

```bash
python test_connection.py
```

Este script probará:
- ✅ Carga de configuración
- ✅ Conexión a Supabase
- ✅ Lectura de credenciales

## 📖 Documentación

- **`docs/`**: Documentación técnica detallada
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