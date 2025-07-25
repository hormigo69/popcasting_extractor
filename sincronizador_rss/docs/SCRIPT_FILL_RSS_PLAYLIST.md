# Script de Llenado de RSS Playlist

## Descripción

El script `scripts/fill_rss_playlist_all_podcasts.py` procesa todas las filas de la tabla `podcasts` y llena el campo `rss_playlist` con datos estructurados en formato JSON, convirtiendo el texto plano del RSS a una estructura organizada.

## Funcionalidad

### Procesamiento de Playlist

El script convierte el texto de playlist del RSS de formato:
```
the beatles · rain  ::  the doors · wintertime love  ::  joni mitchell · don't interrupt the sorrow
```

A formato JSON estructurado:
```json
[
  {
    "position": 1,
    "artist": "the beatles",
    "title": "rain"
  },
  {
    "position": 2,
    "artist": "the doors",
    "title": "wintertime love"
  },
  {
    "position": 3,
    "artist": "joni mitchell",
    "title": "don't interrupt the sorrow"
  }
]
```

### Características

- **Limpieza automática**: Elimina texto extra como Ko-fi y referencias a archivos
- **Cache inteligente**: Descarga el RSS una sola vez y lo reutiliza
- **Procesamiento por lotes**: Maneja grandes volúmenes de datos eficientemente
- **Validación**: Verifica que los datos sean válidos antes de guardar
- **Modo dry-run**: Permite simular el procesamiento sin hacer cambios

## Uso

### Comandos Básicos

```bash
# Procesar todos los podcasts (modo dry-run)
python scripts/fill_rss_playlist_all_podcasts.py --dry-run

# Procesar solo los 50 podcasts más recientes
python scripts/fill_rss_playlist_all_podcasts.py --recent-only 50

# Procesar máximo 100 podcasts (para pruebas)
python scripts/fill_rss_playlist_all_podcasts.py --max-podcasts 100

# Procesar con logs detallados
python scripts/fill_rss_playlist_all_podcasts.py --recent-only 10 --verbose
```

### Opciones Disponibles

- `--batch-size N`: Tamaño del lote para procesamiento (default: 50)
- `--dry-run`: Ejecutar en modo simulación sin hacer cambios
- `--verbose`: Mostrar logs detallados
- `--max-podcasts N`: Número máximo de podcasts a procesar
- `--recent-only N`: Procesar solo los N podcasts más recientes

## Estrategias de Procesamiento

### 1. Procesamiento de Podcasts Recientes

Recomendado para la mayoría de casos:

```bash
python scripts/fill_rss_playlist_all_podcasts.py --recent-only 100
```

**Ventajas:**
- Los podcasts más recientes tienen datos disponibles en el RSS actual
- Procesamiento rápido y eficiente
- Menor riesgo de errores

### 2. Procesamiento Completo

Para procesar toda la base de datos:

```bash
python scripts/fill_rss_playlist_all_podcasts.py --batch-size 25
```

**Consideraciones:**
- Los podcasts más antiguos pueden no tener datos en el RSS actual
- Muchos podcasts serán saltados por falta de datos
- Tiempo de procesamiento más largo

### 3. Procesamiento de Prueba

Para verificar el funcionamiento:

```bash
python scripts/fill_rss_playlist_all_podcasts.py --recent-only 5 --dry-run --verbose
```

## Flujo de Procesamiento

1. **Inicialización**: Carga configuración y conecta a la base de datos
2. **Obtención de datos**: Descarga podcasts de la BD y RSS actual
3. **Procesamiento por lote**: Procesa podcasts en grupos para eficiencia
4. **Búsqueda de playlist**: Busca datos de playlist en:
   - Campo `rss_playlist` (texto sin procesar)
   - Campos `summary`, `description`, `content`
   - RSS actual (para podcasts recientes)
5. **Conversión a JSON**: Aplica el procesamiento de playlist
6. **Validación**: Verifica que el JSON sea válido
7. **Actualización**: Guarda en la base de datos
8. **Estadísticas**: Muestra resumen del procesamiento

## Resultados Esperados

### Estadísticas de Salida

```
📊 === ESTADÍSTICAS FINALES ===
📻 Total de podcasts: 100
✅ Procesados exitosamente: 0
🔄 Actualizados: 85
⏭️ Ya procesados: 10
⚠️ Saltados: 5
❌ Errores: 0
```

### Interpretación

- **Actualizados**: Podcasts que se procesaron y actualizaron exitosamente
- **Ya procesados**: Podcasts que ya tenían `rss_playlist` en formato JSON válido
- **Saltados**: Podcasts sin datos de playlist disponibles
- **Errores**: Podcasts que fallaron durante el procesamiento

## Consideraciones Importantes

### Limitaciones del RSS

- El RSS actual solo contiene los ~400 episodios más recientes
- Los episodios más antiguos (antes del 400) no tienen datos disponibles
- Para episodios antiguos, se necesitarían archivos RSS históricos

### Rendimiento

- **Cache del RSS**: Se descarga una sola vez y se reutiliza
- **Procesamiento por lotes**: Evita sobrecargar la base de datos
- **Pausas entre lotes**: Permite que la BD procese las actualizaciones

### Seguridad

- **Modo dry-run**: Siempre probar primero sin hacer cambios
- **Validación de datos**: Verifica JSON antes de guardar
- **Manejo de errores**: Continúa procesando aunque algunos podcasts fallen

## Ejemplos de Uso

### Caso 1: Actualización Inicial

```bash
# Procesar los 200 podcasts más recientes
python scripts/fill_rss_playlist_all_podcasts.py --recent-only 200
```

### Caso 2: Verificación de Datos

```bash
# Verificar qué se haría sin hacer cambios
python scripts/fill_rss_playlist_all_podcasts.py --recent-only 50 --dry-run --verbose
```

### Caso 3: Procesamiento Completo

```bash
# Procesar toda la base de datos (puede tomar tiempo)
python scripts/fill_rss_playlist_all_podcasts.py --batch-size 25
```

## Troubleshooting

### Problemas Comunes

1. **Muchos podcasts saltados**: Normal para episodios antiguos sin datos RSS
2. **Errores de conexión**: Verificar configuración de Supabase
3. **JSON inválido**: El script valida automáticamente y salta datos problemáticos

### Logs Útiles

- `--verbose`: Muestra detalles de cada podcast procesado
- Logs de debug: Información sobre búsqueda de datos de playlist
- Estadísticas finales: Resumen completo del procesamiento

## Integración con el Sistema

El script es independiente del sincronizador RSS principal y puede ejecutarse:

- **Antes de la sincronización**: Para preparar datos históricos
- **Después de la sincronización**: Para procesar episodios nuevos
- **Como mantenimiento**: Para actualizar episodios existentes

Los datos procesados son compatibles con el resto del sistema y pueden ser consultados por otras herramientas. 