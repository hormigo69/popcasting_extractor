# 🎙️ RSS Feed - Popcasting

## 🚀 Quick Start

### Desplegar RSS
```bash
./deploy_rss.sh
```

### URL del Feed
```
https://ndhmlymnbrewflharfmr.supabase.co/functions/v1/rss
```

### Probar Feed
```bash
curl https://ndhmlymnbrewflharfmr.supabase.co/functions/v1/rss
```

## ⚡ Comandos Rápidos

| Acción | Comando |
|--------|---------|
| Desplegar | `./deploy_rss.sh` |
| Probar | `curl https://ndhmlymnbrewflharfmr.supabase.co/functions/v1/rss` |
| Contar episodios | `curl https://ndhmlymnbrewflharfmr.supabase.co/functions/v1/rss \| grep -c "<item>"` |
| Ver primeros episodios | `curl https://ndhmlymnbrewflharfmr.supabase.co/functions/v1/rss \| head -50` |

## 🔧 Configuración Post-Despliegue

**IMPORTANTE**: Después de cada `./deploy_rss.sh`:

1. Ve a: https://supabase.com/dashboard/project/ndhmlymnbrewflharfmr/functions
2. Haz clic en `rss`
3. Settings → Desactiva "Verify JWT with legacy secret"
4. Save

## 📊 Estado Actual

- ✅ **Episodios**: 475 (todos)
- ✅ **Formato**: RSS 2.0 + iTunes
- ✅ **Plataformas**: iTunes, Spotify, Google Podcasts
- ✅ **Cache**: 5 minutos

## 📚 Documentación Completa

Ver: [`docs/RSS_FEED_SETUP.md`](docs/RSS_FEED_SETUP.md)

---

**Última actualización**: Julio 2025 