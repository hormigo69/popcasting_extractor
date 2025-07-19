# 📋 Episodios Faltantes Finales - Popcasting Extractor

## 📊 Estado Actual
- **Total episodios en BD**: 486
- **Con información web**: 475 (97.7%)
- **Sin información web**: 11 episodios
- **Cobertura**: 97.7% ✅

## 🎯 Objetivo
Completar la información web de los **11 episodios faltantes** para alcanzar el 100% de cobertura.

## 📝 Episodios Faltantes

### Episodios Antiguos (2007-2008)
Todos los episodios faltantes son del rango antiguo (0-91):

1. **Episodio #60** - 2007-12-01
2. **Episodio #61** - 2007-12-15  
3. **Episodio #062** - 2014-10-29 (especial)
4. **Episodio #62** - 2007-12-31
5. **Episodio #63** - 2008-01-14
6. **Episodio #65** - 2008-02-15
7. **Episodio #66** - 2008-03-01
8. **Episodio #67** - 2008-03-15
9. **Episodio #68** - 2008-04-01
10. **Episodio #70** - 2008-04-30
11. **Episodio #84** - 2008-12-01

## 🔍 Dónde Buscar

### Páginas de Archivo
Buscar en estas páginas de popcastingpop.com:

1. **Episodios 0-20**: https://popcastingpop.com/archivo-popcasting/
2. **Episodios 21-41**: https://popcastingpop.com/archivo-popcasting-21-40/
3. **Episodios 42-63**: https://popcastingpop.com/programas-anteriores-42-63/
4. **Episodios 64-91**: https://popcastingpop.com/programas-anteriores-64-91/

### Estrategia de Búsqueda
1. **Buscar por número**: Buscar "programa #60", "programa #61", etc.
2. **Buscar por fecha**: Usar las fechas del RSS para encontrar el episodio correcto
3. **Buscar por título**: Buscar "Popcasting60", "Popcasting61", etc.

## 📋 Proceso Manual

### Paso 1: Editar el archivo
```bash
# Editar el archivo de episodios faltantes
nano episodios_faltantes_actualizado.txt
```

### Paso 2: Añadir URLs encontradas
Para cada episodio, añadir la URL web encontrada en la última columna:

```
Episodio #60 | Popcasting60 | 2007-12-01 | https://www.ivoox.com/popcasting60-audios-mp3_rf_346645_1.html | https://popcastingpop.com/url-encontrada-del-episodio-60
```

### Paso 3: Procesar URLs
```bash
# Ejecutar el script de procesamiento
python procesar_urls_manuales_finales.py
```

## 🛠️ Scripts Disponibles

### 1. Generar Informe
```bash
python generar_informe_faltantes.py
```
- Muestra el estado actual de la base de datos
- Lista todos los episodios faltantes
- Proporciona recomendaciones

### 2. Procesar URLs Manuales
```bash
python procesar_urls_manuales_finales.py
```
- Lee el archivo `episodios_faltantes_actualizado.txt`
- Extrae información web de las URLs encontradas
- Actualiza la base de datos automáticamente

### 3. Verificar Estado
```bash
python -c "from services.supabase_database import SupabaseDatabase; db = SupabaseDatabase(); podcasts = db.get_all_podcasts(); total = len(podcasts); with_web = len([p for p in podcasts if p.get('wordpress_url')]); print(f'Cobertura: {with_web}/{total} ({with_web/total*100:.1f}%)')"
```

## 📈 Resultado Esperado

Una vez completados los 11 episodios faltantes:
- **Total episodios**: 486
- **Con información web**: 486
- **Cobertura**: **100%** 🎉

## 🔧 Solución de Problemas

### Si no se encuentra una URL:
1. **Verificar fechas**: Los episodios pueden estar en páginas diferentes
2. **Buscar variaciones**: "programa #60", "Popcasting 60", "episodio 60"
3. **Revisar archivos**: Algunos episodios pueden estar en archivos especiales
4. **Contactar administrador**: Si es imposible encontrar la URL

### Si el script falla:
1. **Verificar formato**: Asegurar que las URLs estén en la columna correcta
2. **Verificar conectividad**: Comprobar acceso a internet
3. **Revisar logs**: Ver mensajes de error específicos

## 📞 Soporte

Si encuentras problemas:
1. Revisar los logs del script
2. Verificar el formato del archivo de episodios
3. Comprobar la conectividad a Supabase
4. Revisar que las URLs sean válidas

---

**Última actualización**: 2025-07-19
**Estado**: 11 episodios faltantes (97.7% cobertura) 