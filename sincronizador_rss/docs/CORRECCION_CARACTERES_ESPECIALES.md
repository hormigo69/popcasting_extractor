# Corrección de Caracteres Especiales en web_playlist

## 🐛 Problema Identificado

Los caracteres especiales como apóstrofes (`'`), comillas (`"`) y otros caracteres Unicode se estaban guardando en la base de datos como secuencias Unicode escapadas en lugar de caracteres legibles.

### Ejemplo del problema:
```json
// ❌ Antes (incorrecto)
"title": "don\u2019t interrupt the sorrow"
"title": "i\u2019ll be your baby tonight"
"title": "you ain\u2019t going nowhere"
```

### Ejemplo corregido:
```json
// ✅ Después (correcto)
"title": "don't interrupt the sorrow"
"title": "i'll be your baby tonight"
"title": "you ain't going nowhere"
```

## 🔍 Causa Raíz

El problema estaba en el método `insert_full_podcast()` del `DatabaseManager` donde se usaba `json.dumps()` sin el parámetro `ensure_ascii=False`. Esto causaba que Python convirtiera automáticamente los caracteres especiales a secuencias Unicode escapadas.

### Código problemático:
```python
# ❌ Antes
filtered_podcast_data['web_playlist'] = json.dumps(songs_list)
```

### Código corregido:
```python
# ✅ Después
filtered_podcast_data['web_playlist'] = json.dumps(songs_list, ensure_ascii=False)
```

## 🛠️ Solución Implementada

### 1. Corrección en DatabaseManager

Se modificó el archivo `sincronizador_rss/src/components/database_manager.py` para agregar `ensure_ascii=False` en todas las llamadas a `json.dumps()`:

- **Línea 201**: Procesamiento de web_playlist como diccionario
- **Línea 207**: Procesamiento de web_playlist como lista directa  
- **Línea 217**: Procesamiento de web_playlist desde JSON string
- **Línea 230**: Procesamiento de web_extra_links

### 2. Función de Limpieza Unicode

Se mejoró la función `_clean_unicode_text()` en `WordPressClient` para manejar correctamente la decodificación de caracteres mal codificados:

```python
def _clean_unicode_text(self, text: str) -> str:
    """
    Limpia caracteres Unicode escapados y entidades HTML, mostrando los caracteres especiales tal como aparecen en la web.
    """
    if not text:
        return text
    try:
        # Si detectamos patrones típicos de mala codificación, intentamos decodificar
        if 'Ã' in text or 'Â' in text:
            try:
                text = text.encode('latin-1').decode('utf-8')
            except Exception:
                pass
        text = html.unescape(text)
        return text.strip()
    except Exception as e:
        logger.warning(f'Error al limpiar texto Unicode: {e}')
        return text
```

## 🧪 Verificación

### Prueba de Extracción
Se ejecutó el sincronizador con episodios de prueba (#484 y #485) y se verificó que:

1. **Extracción correcta**: Los caracteres se extraen correctamente de WordPress
2. **Limpieza correcta**: La función `_clean_unicode_text()` decodifica correctamente
3. **Almacenamiento correcto**: Los caracteres se guardan correctamente en la BD
4. **Visualización correcta**: Los caracteres se muestran tal como aparecen en la web

### Resultados de la verificación:
```
✅ "don't interrupt the sorrow"
✅ "i'll be your baby tonight"
✅ "you ain't going nowhere"
✅ "pickin' up the pieces"
```

## 📋 Archivos Modificados

1. **`sincronizador_rss/src/components/database_manager.py`**
   - Agregado `ensure_ascii=False` en todas las llamadas a `json.dumps()`

2. **`sincronizador_rss/src/components/wordpress_client.py`**
   - Mejorada la función `_clean_unicode_text()`
   - Aplicada limpieza de caracteres en todos los puntos de extracción

## 🎯 Impacto

- **Antes**: Los caracteres especiales se mostraban como `\u2019`, `\u2018`, etc.
- **Después**: Los caracteres especiales se muestran correctamente como `'`, `"`, etc.
- **Beneficio**: Los datos extraídos son ahora fieles al contenido original de WordPress

## 🔄 Flujo Completo Corregido

1. **Extracción de WordPress**: Los caracteres se extraen con codificación correcta
2. **Limpieza Unicode**: Se aplica `_clean_unicode_text()` para decodificar caracteres mal codificados
3. **Serialización JSON**: Se usa `json.dumps(..., ensure_ascii=False)` para preservar caracteres especiales
4. **Almacenamiento en BD**: Los caracteres se guardan como texto legible
5. **Recuperación**: Los caracteres se muestran correctamente al consultar la BD

---

**Fecha de corrección**: 25 de julio de 2025  
**Estado**: ✅ Completado y verificado 