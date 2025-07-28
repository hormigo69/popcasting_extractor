#!/bin/bash

echo "🚀 Desplegando función RSS..."

# Desplegar la función
supabase functions deploy rss --project-ref ndhmlymnbrewflharfmr

echo ""
echo "✅ Función desplegada correctamente!"
echo ""
echo "🔧 IMPORTANTE: Ahora necesitas hacer la función pública:"
echo "1. Ve a: https://supabase.com/dashboard/project/ndhmlymnbrewflharfmr/functions"
echo "2. Haz clic en la función 'rss'"
echo "3. Ve a Settings"
echo "4. Desactiva 'Verify JWT with legacy secret'"
echo "5. Guarda los cambios"
echo ""
echo "🌐 Tu RSS estará disponible en:"
echo "https://ndhmlymnbrewflharfmr.supabase.co/functions/v1/rss"
echo ""
echo "📝 Para probar:"
echo "curl https://ndhmlymnbrewflharfmr.supabase.co/functions/v1/rss" 