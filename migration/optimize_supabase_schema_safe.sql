-- Script SQL SEGURO para optimizar los tipos de campo en Supabase
-- Ejecutar este script en el SQL Editor de Supabase
-- IMPORTANTE: Hacer backup antes de ejecutar

-- =====================================================
-- PASO 1: VERIFICAR ESTADO ACTUAL
-- =====================================================

-- Verificar tipos actuales de las columnas
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'podcasts' 
  AND column_name IN ('date', 'program_number')
ORDER BY column_name;

-- Verificar datos actuales
SELECT 
    'program_number' as column_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN program_number ~ '^[0-9]+$' THEN 1 END) as valid_numbers,
    COUNT(CASE WHEN program_number !~ '^[0-9]+$' THEN 1 END) as invalid_numbers,
    COUNT(CASE WHEN program_number IS NULL THEN 1 END) as null_values
FROM podcasts
UNION ALL
SELECT 
    'date' as column_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN date ~ '^\d{4}-\d{2}-\d{2}$' THEN 1 END) as valid_dates,
    COUNT(CASE WHEN date !~ '^\d{4}-\d{2}-\d{2}$' THEN 1 END) as invalid_dates,
    COUNT(CASE WHEN date IS NULL THEN 1 END) as null_values
FROM podcasts;

-- =====================================================
-- PASO 2: LIMPIAR DATOS ANTES DE CONVERTIR
-- =====================================================

-- Limpiar program_number: convertir a entero y limpiar caracteres no numéricos
UPDATE podcasts 
SET program_number = REGEXP_REPLACE(program_number, '[^0-9]', '', 'g')
WHERE program_number IS NOT NULL 
  AND program_number !~ '^[0-9]+$';

-- Limpiar date: asegurar formato YYYY-MM-DD
UPDATE podcasts 
SET date = TO_CHAR(TO_DATE(date, 'YYYY-MM-DD'), 'YYYY-MM-DD')
WHERE date IS NOT NULL 
  AND date ~ '^\d{4}-\d{2}-\d{2}$';

-- =====================================================
-- PASO 3: CAMBIAR TIPOS DE COLUMNA
-- =====================================================

-- Cambiar program_number de TEXT a INTEGER
ALTER TABLE podcasts 
ALTER COLUMN program_number TYPE INTEGER USING program_number::INTEGER;

-- Cambiar date de TEXT a DATE
ALTER TABLE podcasts 
ALTER COLUMN date TYPE DATE USING date::DATE;

-- =====================================================
-- PASO 4: RECREAR ÍNDICES
-- =====================================================

-- Eliminar índices existentes
DROP INDEX IF EXISTS idx_podcasts_date;
DROP INDEX IF EXISTS idx_podcasts_program_number;

-- Crear nuevos índices optimizados
CREATE INDEX idx_podcasts_date ON podcasts(date);
CREATE INDEX idx_podcasts_program_number ON podcasts(program_number);

-- =====================================================
-- PASO 5: VERIFICAR RESULTADO
-- =====================================================

-- Verificar tipos después del cambio
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'podcasts' 
  AND column_name IN ('date', 'program_number')
ORDER BY column_name;

-- Verificar datos después del cambio
SELECT 
    'program_number' as column_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN program_number IS NOT NULL THEN 1 END) as non_null_values,
    MIN(program_number) as min_value,
    MAX(program_number) as max_value
FROM podcasts
UNION ALL
SELECT 
    'date' as column_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN date IS NOT NULL THEN 1 END) as non_null_values,
    MIN(date) as min_value,
    MAX(date) as max_value
FROM podcasts;

-- Mostrar algunos ejemplos de datos convertidos
SELECT 
    id,
    title,
    date,
    program_number,
    url
FROM podcasts 
ORDER BY program_number 
LIMIT 10; 