// Deno. Edge Function para generar el RSS desde Supabase.
// Requiere variables de entorno: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

function rfc2822(date: string): string {
  // Asume date YYYY-MM-DD sin hora; fija 20:00 Europe/Madrid para consistencia
  const d = new Date(`${date}T20:00:00+02:00`);
  return d.toUTCString().replace("GMT", "+0000"); // Muchos validadores aceptan UTC string
}

function hhmmss(totalSeconds: number | null): string {
  const s = Math.max(0, Math.floor(totalSeconds || 0));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  const pad = (n: number) => n.toString().padStart(2, "0");
  return `${pad(h)}:${pad(m)}:${pad(sec)}`;
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  // Check for authorization header (optional for RSS feeds)
  const authHeader = req.headers.get('authorization');
  
  // Use service role key for database access (no need for user auth for RSS)
  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
  );

  const { data: episodes, error } = await supabase
    .from("podcasts")
    .select(
      `
      id, title, date, program_number, download_url, file_size,
      mp3_duration, duration, wordpress_url, cover_image_url
      `
    )
    .not("download_url", "is", null)
    .order("date", { ascending: false });

  if (error) {
    console.error(error);
    return new Response("Feed error", { 
      status: 500,
      headers: corsHeaders
    });
  }

  // Datos estáticos del canal (ajústalos a tu marca)
  const channel = {
    title: "Popcasting",
    link: "https://popcastingpop.com/",
    description: "Pódcast de música en español, desde 2005.",
    language: "es-es",
    imageSmall: "https://cdn.popcastingpop.com/series/logo-1400.jpg",
    imageLarge: "https://cdn.popcastingpop.com/series/logo-3000.jpg",
    explicit: "false",
    author: "Popcasting",
    // Si estás migrando, puedes incluir itunes:new-feed-url cuando toque:
    // newFeedUrl: "https://popcastingpop.com/feed.xml"
  };

  const itemsXml = (episodes || []).map((e) => {
    const length = e.file_size ? String(e.file_size) : "0";
    const dur = hhmmss((e.mp3_duration ?? e.duration) || 0);
    const guid = e.wordpress_url ? e.wordpress_url : `popcasting-${e.id}`;
    const link = `https://popcastingpop.com/episodios/${e.id}`;
    const pubDate = rfc2822(e.date);

    // Puedes enriquecer <description> con tu tracklist si quieres.
    const description = `<![CDATA[${e.title}]]>`;

    return `
      <item>
        <title>${escapeXml(e.title)}</title>
        <link>${link}</link>
        <pubDate>${pubDate}</pubDate>
        <guid isPermaLink="false">${escapeXml(guid)}</guid>
        <enclosure url="${escapeAttr(e.download_url)}" length="${length}" type="audio/mpeg"/>
        <itunes:episode>${e.program_number ?? ""}</itunes:episode>
        <itunes:duration>${dur}</itunes:duration>
        <itunes:explicit>${channel.explicit}</itunes:explicit>
        <description>${description}</description>
      </item>
    `;
  }).join("");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
  xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
  xmlns:podcast="https://podcastindex.org/namespace/1.0">
  <channel>
    <title>${escapeXml(channel.title)}</title>
    <link>${channel.link}</link>
    <language>${channel.language}</language>
    <description>${escapeXml(channel.description)}</description>

    <image>
      <url>${channel.imageSmall}</url>
      <title>${escapeXml(channel.title)}</title>
      <link>${channel.link}</link>
    </image>

    <itunes:author>${escapeXml(channel.author)}</itunes:author>
    <itunes:image href="${channel.imageLarge}"/>
    <itunes:category text="Music"/>
    <itunes:explicit>${channel.explicit}</itunes:explicit>
    ${/* channel.newFeedUrl ? `<itunes:new-feed-url>${channel.newFeedUrl}</itunes:new-feed-url>` : "" */ ""}

    ${itemsXml}
  </channel>
</rss>`;

  return new Response(xml, {
    status: 200,
    headers: {
      ...corsHeaders,
      "Content-Type": "application/rss+xml; charset=utf-8",
      "Cache-Control": "public, max-age=300, s-maxage=300"
    },
  });
});

function escapeXml(str: string) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}
function escapeAttr(str: string) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;");
} 