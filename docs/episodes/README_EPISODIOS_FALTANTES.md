# 📋 Completar Episodios Faltantes - Información Web

## 📊 Estado Actual

- **Total episodios**: 396
- **Con información web**: 363 (91.7%)
- **Sin información web**: 33 (8.3%)

## 🎯 Objetivo

Completar la información web de los 33 episodios restantes para alcanzar el 100% de cobertura.

## 📁 Archivos Creados

1. **`episodios_faltantes.txt`** - Lista original de episodios faltantes
2. **`episodios_faltantes_actualizado.txt`** - Lista actualizada generada automáticamente
3. **`completar_episodios_faltantes.py`** - Script para procesar URLs manuales
4. **`verificar_episodios_faltantes.py`** - Script para verificar estado actual

## 🔄 Proceso de Completado

### Paso 1: Verificar Estado Actual
```bash
python verificar_episodios_faltantes.py
```

### Paso 2: Buscar URLs Manualmente

1. **Abre el archivo**: `episodios_faltantes_actualizado.txt`
2. **Ve al sitio web**: https://popcastingpop.com
3. **Para cada episodio**:
   - Busca por número (ej: "popcasting 470")
   - Busca por fecha
   - Busca por título
   - Copia la URL completa de la página del episodio
   - Pégala en la columna `URL_MANUAL`

### Paso 3: Procesar URLs Encontradas
```bash
python completar_episodios_faltantes.py
```

### Paso 4: Verificar Resultado
```bash
python verificar_episodios_faltantes.py
```

## 📋 Episodios por Año

### 2025 (1 episodio)
- ID: 15 | #470 | 2025-01-14 | Popcasting470

### 2024 (2 episodios)
- ID: 16 | #469 | 2024-12-31 | Popcasting469
- ID: 396 | #TEST001 | 2024-01-15 | Test Episode for Change Detection

### 2017 (3 episodios)
- ID: 199 | #286 | 2017-05-14 | Popcasting 286
- ID: 200 | #285 | 2017-05-01 | Popcasting 285
- ID: 207 | #278 | 2017-01-14 | Popcasting 278

### 2016 (3 episodios)
- ID: 214 | #271 | 2016-10-04 | Popcasting271 (ok)
- ID: 222 | #263 | 2016-06-01 | Popcasting263
- ID: 230 | #255 | 2016-02-01 | Popcasting255

### 2015 (1 episodio)
- ID: 232 | #253 | 2015-12-31 | Popcasting253

### 2014 (1 episodio)
- ID: 261 | #062 | 2014-10-29 | Popcasting062

### 2012 (1 episodio)
- ID: 307 | #180 | 2012-12-14 | Popcasting180 :: Especial Navidad 2012

### 2011 (5 episodios)
- ID: 331 | #156 | 2011-12-01 | Popcasting156
- ID: 333 | #154 | 2011-10-31 | Popcasting154
- ID: 339 | #147 | 2011-07-15 | Popcasting147
- ID: 343 | #143 | 2011-05-19 | Popcasting143
- ID: 351 | #135 | 2011-01-15 | Popcasting135

### 2010 (4 episodios)
- ID: 352 | #134 | 2010-12-31 | Popcasting134
- ID: 362 | #124 | 2010-07-26 | Popcasting124
- ID: 374 | #112 | 2010-01-31 | Popcasting112
- ID: 375 | #111 | 2010-01-15 | Popcasting111

### 2009 (2 episodios)
- ID: 381 | #98 | 2009-07-01 | Popcasting98
- ID: 382 | #96 | 2009-06-01 | Popcasting 96

### 2008 (7 episodios)
- ID: 385 | #84 | 2008-12-01 | Popcasting84
- ID: 386 | #70 | 2008-04-30 | Popcasting70
- ID: 387 | #68 | 2008-04-01 | Popcasting68
- ID: 388 | #67 | 2008-03-15 | Popcasting67
- ID: 389 | #66 | 2008-03-01 | Popcasting66
- ID: 390 | #65 | 2008-02-15 | Popcasting65
- ID: 392 | #63 | 2008-01-14 | Popcasting63

### 2007 (3 episodios)
- ID: 393 | #62 | 2007-12-31 | Popcasting62
- ID: 394 | #61 | 2007-12-15 | Popcasting61
- ID: 395 | #60 | 2007-12-01 | Popcasting60

## 🔍 Estrategias de Búsqueda

### 1. Búsqueda por Número
- Busca "popcasting 470" en Google
- Busca "popcasting470" en el sitio web
- Busca "#470" en el sitio web

### 2. Búsqueda por Fecha
- Busca episodios de la fecha específica
- Usa el formato YYYY/MM/DD en la URL

### 3. Búsqueda por Título
- Busca el título completo del episodio
- Busca palabras clave del título

### 4. Patrones de URL Comunes
```
https://popcastingpop.com/YYYY/MM/DD/popcasting-XXX/
https://popcastingpop.com/popcasting-XXX/
https://popcastingpop.com/programas-anteriores-XXX-YY/
```

## ⚠️ Consideraciones Especiales

### Episodios de Prueba
- **TEST001**: Es un episodio de prueba, puede no existir en la web

### Episodios Muy Antiguos (2007-2009)
- Algunos episodios de los primeros años pueden no estar disponibles
- Busca en archivos o secciones especiales del sitio

### Episodios Especiales
- **Popcasting180 :: Especial Navidad 2012**: Puede tener formato especial
- **Popcasting062**: Número de 3 dígitos, formato inusual

### Discrepancias de Numeración
- Algunos episodios pueden tener numeración diferente en la web
- Busca variaciones del número (ej: 470, 470-2, etc.)

## 📝 Formato del Archivo

Cada línea debe tener este formato:
```
ID: X | Número: Y | Fecha: Z | Título: W | URL_MANUAL: https://popcastingpop.com/...
```

Ejemplo:
```
ID: 15 | Número: 470 | Fecha: 2025-01-14 | Título: Popcasting470 | URL_MANUAL: https://popcastingpop.com/2025/01/14/popcasting-470/
```

## ✅ Verificación Final

Después de completar el proceso:

1. **Verificar estado**: `python verificar_episodios_faltantes.py`
2. **Comprobar porcentaje**: Debe ser 100% o muy cercano
3. **Revisar información**: Usar `python -m services.web_cli info [ID]` para verificar

## 🎯 Meta

**Objetivo**: Alcanzar el 100% de episodios con información web (396/396)

**Estado actual**: 91.7% (363/396)

**Episodios restantes**: 33 