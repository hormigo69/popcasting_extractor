# Estructura del Proyecto Popcasting Extractor

## 📁 Estructura de Directorios

```
popcasting_extractor/
├── 📄 Archivos de Configuración
│   ├── pyproject.toml          # Configuración del proyecto y dependencias
│   ├── uv.lock                 # Lock file de dependencias
│   ├── .python-version         # Versión de Python
│   ├── .gitignore              # Archivos ignorados por Git
│   ├── .pre-commit-config.yaml # Configuración de pre-commit hooks
│   └── README.md               # Documentación principal
│
├── 🚀 Punto de Entrada
│   └── main.py                 # Script principal de ejecución
│
├── 🔧 Servicios Principales
│   └── services/               # Módulo principal de servicios
│       ├── __init__.py
│       ├── popcasting_extractor.py  # Extractor principal
│       ├── config.py           # Configuración de base de datos
│       ├── database.py         # Clase base de base de datos
│       ├── supabase_database.py # Implementación de Supabase
│       ├── web_extractor.py    # Extractor web
│       ├── web_cli.py          # CLI para extracción web
│       ├── web_report_generator.py # Generador de reportes web
│       ├── cli.py              # CLI principal
│       ├── logger_setup.py     # Configuración de logging
│       └── utils.py            # Utilidades generales
│
├── 🧪 Tests
│   └── tests/                  # Todos los archivos de test
│       ├── __init__.py
│       ├── test_mp3_3_files_final.py
│       ├── test_mp3_download.py
│       ├── test_mp3_script.py
│       ├── test_synology_client.py
│       ├── test_synology_diagnostic.py
│       └── ... (otros archivos de test)
│
├── 📡 Funcionalidades Synology
│   └── synology/               # Módulo de funcionalidades Synology
│       ├── __init__.py
│       ├── synology_client.py  # Cliente para Synology NAS
│       ├── synology_uploader.py # Uploader para Synology
│       ├── setup_synology_env.py # Configuración de entorno
│       ├── synology.env.example # Ejemplo de variables de entorno
│       ├── example_usage.py    # Ejemplo de uso
│       ├── README_SYNOLOGY.md  # Documentación Synology
│       ├── README_SYNOLOGY_CLIENT.md
│       └── README_MP3_UPLOAD.md
│
├── 🔨 Scripts de Utilidad
│   └── scripts/                # Scripts de utilidad y mantenimiento
│       ├── __init__.py
│       ├── generar_informe.py  # Generador de informes
│       ├── backup_supabase_simple.py
│       ├── test_backup.py
│       │
│       ├── extraction/         # Scripts de extracción específicos
│       │   ├── __init__.py
│       │   ├── actualizar_episodio_60.py
│       │   ├── actualizar_episodio_84_final.py
│       │   ├── buscar_episodios_faltantes_auto.py
│       │   ├── extractor_episodios_antiguos.py
│       │   ├── extraer_episodios_61_62_63_final.py
│       │   ├── extraer_episodios_61_62_63_mejorado.py
│       │   ├── extraer_episodios_61_62_63.py
│       │   └── extraer_episodios_65_66_67_68_70.py
│       │
│       ├── reports/            # Scripts de reportes
│       │   ├── __init__.py
│       │   ├── batch_web_extraction.py
│       │   ├── completar_episodios_faltantes.py
│       │   ├── generar_informe_faltantes.py
│       │   ├── procesar_urls_manuales_finales.py
│       │   ├── sincronizar_supabase_web.py
│       │   └── verificar_episodios_faltantes.py
│       │
│       └── utils/              # Utilidades y scripts de mantenimiento
│           ├── __init__.py
│           ├── analyze_date_sequence.py
│           ├── analyze_missing_and_duplicates.py
│           ├── analyze_mp3_inventory.py
│           ├── analyze_songs_distribution.py
│           ├── analyze_url_coherence.py
│           ├── analyze_wordpress_urls.py
│           ├── backup_supabase.py
│           ├── calculate_mp3_hashes_v2.py
│           ├── calculate_mp3_hashes.py
│           ├── check_url_field_confusion.py
│           ├── clean_duplicate_episodes.py
│           ├── clean_summer_comments.py
│           ├── commit_without_linting.py
│           ├── compare_songs_count.py
│           ├── consolidate_manual_episodes.py
│           ├── diagnose_supabase_data.py
│           ├── download_all_mp3.py
│           ├── download_and_upload_mp3_v2.py
│           ├── download_and_upload_mp3.py
│           ├── download_missing_episodes.py
│           ├── execute_supabase_optimization.py
│           ├── extract_episode_62_final.py
│           ├── extract_episode_62_from_html.py
│           ├── extract_playlists_from_wordpress_auto.py
│           ├── extract_playlists_from_wordpress_v2.py
│           ├── extract_playlists_from_wordpress_v3.py
│           ├── extract_playlists_from_wordpress_v4.py
│           ├── extract_playlists_from_wordpress.py
│           ├── fill_missing_from_wordpress.py
│           ├── fill_missing_web_songs_from_web.py
│           ├── find_episode_62_quick.py
│           ├── find_single_song_episodes.py
│           ├── find_two_song_episodes.py
│           ├── fix_all_linting.py
│           ├── fix_episode_92_correct.py
│           ├── fix_episode_96_correct.py
│           ├── fix_linting_errors.py
│           ├── fix_low_songs_episodes.py
│           ├── fix_playlist_parsing.py
│           ├── fix_single_song_episodes.py
│           ├── fix_songs_from_web_playlist.py
│           ├── fix_syntax_errors.py
│           ├── fix_two_song_episodes.py
│           ├── fix_url_coherence_step1.py
│           ├── fix_url_coherence_step2.py
│           ├── generate_supabase_sql.py
│           ├── identify_missing_web_songs_count.py
│           ├── insert_manual_episodes.py
│           ├── investigate_duplicate_dates.py
│           ├── list_duplicated_episodes.py
│           ├── list_episodes_needing_ivoox_urls.py
│           ├── manual_update_web_playlist.py
│           ├── migrate_web_songs_count.py
│           ├── normalize_supabase_dates.py
│           ├── optimize_database_types.py
│           ├── quick_identify_missing.py
│           ├── README_ESSENTIAL_FILES.md
│           ├── restore_episodes_0_to_20_links.py
│           ├── restore_supabase.py
│           ├── setup_smart_precommit.py
│           ├── smart_commit.py
│           ├── test_wordpress_extraction.py
│           ├── update_web_songs_count.py
│           ├── verify_links_integrity.py
│           ├── verify_low_songs_episodes.py
│           ├── verify_podcasts_integrity.py
│           ├── verify_songs_integrity.py
│           ├── web_extractor.py
│           └── web_report.py
│
├── 📊 Datos
│   ├── data/                   # Datos del proyecto
│   │   ├── *.html              # Archivos HTML de episodios
│   │   ├── *.json              # Archivos JSON de datos
│   │   └── *.txt               # Archivos de texto
│   │
│   ├── logs/                   # Archivos de log
│   ├── backups/                # Backups de base de datos
│   ├── outputs/                # Archivos de salida
│   └── migration/              # Scripts de migración de base de datos
│
└── 📚 Documentación
    └── docs/                   # Documentación del proyecto
        ├── README.md
        ├── README_BACKUP.md
        ├── README_EPISODE_LINKS.md
        ├── README_LOGGING.md
        ├── README_MEJORAS.md
        ├── README_PRE_COMMIT.md
        ├── README_WEB_EXTRACTION.md
        ├── README_WEB_SONGS_COUNT.md
        ├── REGENERACION_BDD.md
        ├── VERIFICACION_ENLACES.md
        ├── IMPLEMENTACION_WEB_SONGS_COUNT_COMPLETADA.md
        ├── CORRECCION_EPISODIOS_POCAS_CANCIONES_FINAL.md
        ├── CORRECCION_EPISODIOS_POCAS_CANCIONES.md
        ├── episodes/            # Documentación específica de episodios
        ├── migration/           # Documentación de migraciones
        └── technical/           # Documentación técnica
```

## 🔄 Cambios Realizados

### ✅ Archivos Movidos y Reorganizados

1. **Tests**: Todos los archivos `test_*.py` movidos a `tests/`
2. **Synology**: Archivos relacionados con Synology movidos a `synology/`
3. **Scripts**: `generar_informe.py` movido a `scripts/`
4. **Documentación**: Archivos README específicos movidos a `synology/`

### ✅ Archivos Eliminados

1. **Duplicados**: Versiones anteriores de archivos de test (`test_mp3_3_files.py`, `test_mp3_3_files_v2.py`, `test_mp3_3_files_correct.py`)
2. **Obsoletos**: `test_path.txt`, `verify_folder_creation.py`

### ✅ Rutas de Importación Actualizadas

1. **Tests**: Actualizadas para importar desde `services` y `synology`
2. **Scripts**: Actualizadas para importar desde `services` y `synology`
3. **Módulos**: Creados `__init__.py` para `tests/` y `synology/`

## 🚀 Uso

### Ejecutar el extractor principal:
```bash
python main.py
```

### Ejecutar tests:
```bash
python tests/test_mp3_3_files_final.py
```

### Usar funcionalidades Synology:
```python
from synology.synology_client import SynologyClient
client = SynologyClient()
```

### Ejecutar scripts de utilidad:
```bash
python scripts/generar_informe.py
```

## 📝 Notas Importantes

- Todos los archivos mantienen sus funcionalidades originales
- Las rutas de importación han sido actualizadas automáticamente
- La estructura es más limpia y organizada
- Se eliminaron archivos duplicados y obsoletos
- Se mantuvieron todas las dependencias y configuraciones 