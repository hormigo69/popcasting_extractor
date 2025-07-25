# Guía de Instalación y Configuración

## 📋 Requisitos Previos

- Python 3.8 o superior
- Acceso a un proyecto Supabase
- Credenciales de Supabase (URL del proyecto y API key)

## 🔧 Instalación Paso a Paso

### 1. Preparar el Entorno

```bash
# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

### 2. Instalar Dependencias

```bash
cd sincronizador_rss
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno

Crear archivo `.env` en el directorio padre con:

```env
# Credenciales de Supabase
supabase_project_url=https://tu-proyecto.supabase.co
supabase_api_key=tu-api-key-aqui

# Opcional: Configuración adicional
DATABASE_TYPE=supabase
```

### 4. Configurar config.ini

Editar `sincronizador_rss/config.ini`:

```ini
[database]
# Las credenciales se cargan desde variables de entorno
use_env_vars = true

[rss]
url = https://feeds.feedburner.com/Popcasting

[wordpress]
url = https://popcastingpop.com
```

## 🧪 Verificar Instalación

### Prueba de Conexión

```bash
python test_connection.py
```

**Resultado esperado:**
```
✅ --- PRUEBA FINALIZADA CON ÉXITO --- ✅
```

### Verificar Logs

Los logs se guardan en `sincronizador_rss/logs/sincronizador_rss.log`

## 🔍 Solución de Problemas

### Error: "No se encontró el archivo de configuración"
- Verificar que `config.ini` existe en `sincronizador_rss/`
- Verificar permisos de lectura

### Error: "Faltan variables de entorno"
- Verificar que `.env` existe en el directorio padre
- Verificar nombres de variables: `supabase_project_url`, `supabase_api_key`

### Error: "Error al conectar a Supabase"
- Verificar credenciales de Supabase
- Verificar conectividad de red
- Verificar que el proyecto Supabase esté activo

## 📁 Estructura de Archivos Esperada

```
proyecto_principal/
├── .env                          # Variables de entorno
└── sincronizador_rss/
    ├── README.md
    ├── config.ini                # Configuración
    ├── requirements.txt          # Dependencias
    ├── docs/                     # Documentación
    ├── logs/                     # Logs
    └── src/                      # Código fuente
```

## 🚀 Próximos Pasos

Después de la instalación exitosa:

1. Revisar la documentación en `docs/`
2. Implementar componentes adicionales
3. Configurar tareas programadas si es necesario
4. Personalizar configuración según necesidades 