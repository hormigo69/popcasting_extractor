#!/usr/bin/env python3
"""
Script para restaurar los enlaces extras correctos de los episodios #0-#20.
Basado en la información proporcionada por el usuario.
"""

import json
import logging
import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.supabase_database import SupabaseDatabase

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/restore_episodes_0_to_20_links.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class EpisodesLinkRestorer:
    def __init__(self):
        self.db = SupabaseDatabase()

        # Episodios que deben limpiarse (sin enlaces)
        self.episodes_to_clean = [42, 46, 48, 49, 70, 71]

        # Enlaces extras correctos basados en la información proporcionada
        self.correct_links = {
            3: [
                {
                    "text": "mp3 blogs",
                    "url": "http://www.londonleben.co.uk/london_leben/2005/04/two_hundred_and.html",
                },
                {
                    "text": "sandie shaw",
                    "url": "http://smiths.arcaneoldwardrobe.com/interviews/1984/glove.htm",
                },
                {"text": "franzferdinand.org", "url": "http://www.franzferdinand.org/"},
            ],
            5: [
                {"text": "colleen", "url": "http://www.colleenplays.org/"},
                {
                    "text": "spoilt victorian child",
                    "url": "http://www.spoiltvictorianchild.co.uk/",
                },
            ],
            6: [
                {"text": "copy, right?", "url": "http://copycommaright.blogspot.com/"},
                {
                    "text": "the peel tapes",
                    "url": "http://www.jonhorne.co.uk/jptapes/jptapes.html",
                },
                {
                    "text": "jenny wilson",
                    "url": "http://www.jennywilson.net/music.htm#",
                },
            ],
            7: [
                {"text": "bill fay", "url": "http://www.billfay.co.uk/"},
                {
                    "text": "dave graney",
                    "url": "http://www.spill-label.org/sound/davegraney-myschtick.mp3",
                },
            ],
            8: [
                {
                    "text": "devendra banhart",
                    "url": "http://www.xlrecordings.com/devendrabanhart/",
                },
                {
                    "text": "brenton wood",
                    "url": "http://20-248-e.onlinestoragesolution.com/spikepriggen/public/gimme%20little.mov",
                },
                {
                    "text": "bob dylan's scrapbook",
                    "url": "/Popcasting/antigua%20web%20(geocities)/00%20-%2026/popcastingpop%201/dylanscrapbook.html",
                },
            ],
            9: [
                {
                    "text": "thomas fersen",
                    "url": "http://www.totoutard.com/pointEcoute.php",
                },
                {
                    "text": "Marc & the Mambas live on Richard Skinner (7-23-83) -In My Room & My Former Self",
                    "url": "/Popcasting/antigua%20web%20(geocities)/00%20-%2026/popcastingpop%201/MarcAlmond.mp3",
                },
            ],
            10: [
                {
                    "text": "Hubert Mounier",
                    "url": "http://hubertmounier.artistes.universalmusic.fr/",
                }
            ],
            11: [
                {"text": "shelflife", "url": "http://www.shelflife.com/"},
                {"text": "vinylpodcast", "url": "http://www.vinylpodcast.com/"},
                {"text": "joe meek", "url": "http://www.rhis.co.uk/jmas/"},
            ],
            13: [
                {
                    "text": "wrong-eyed jesus",
                    "url": "http://www.searchingforthewrongeyedjesus.com/",
                },
                {
                    "text": "good weather for an air strike",
                    "url": "http://goodweatherforairstrike.blogspot.com/2005/12/m3-holiday-edition.html",
                },
                {"text": "falalalala", "url": "http://www.falalalala.com/"},
                {
                    "text": "red ryder bb gun",
                    "url": "http://redryderbbgun.blogspot.com/",
                },
                {"text": "soulshower", "url": "http://soulshower.blogspot.com/"},
                {
                    "text": "elton john xmas cd",
                    "url": "http://www.starbucks.com/hearmusic/product.asp?category%5Fname=Our+Compilations&amp;product%5Fid=895678",
                },
            ],
            14: [
                {
                    "text": "geeshie willey en archive.org",
                    "url": "http://www.archive.org/search.php?query=creator:%22Geeshie%20Wiley%22",
                },
                {"text": "archive.org", "url": "http://www.archive.org/"},
            ],
            15: [
                {
                    "text": "the office",
                    "url": "http://homepage.mac.com/elliottday/theoffice/references.html",
                },
                {
                    "text": "ricky gervais podcast",
                    "url": "http://www.guardian.co.uk/rickygervais",
                },
                {"text": "big star", "url": "http://jefitoblog.com/blog/?p=567"},
            ],
            16: [
                {
                    "text": "lost and found",
                    "url": "http://www.lacoctelera.com/lostandfound",
                },
                {"text": "tom tom club", "url": "http://www.tomtomclub.net/"},
                {"text": "the deaths", "url": "http://www.thedeaths.net/"},
            ],
            17: [
                {
                    "text": "the peachwaves MP3",
                    "url": "http://profile.myspace.com/index.cfm?fuseaction=user.viewprofile&amp;friendid=25598013",
                },
                {
                    "text": "the peachwaves video",
                    "url": "http://video.google.com/videoplay?docid=1801998643765982491&amp;q=the+peachwaves",
                },
                {"text": "crud crud", "url": "http://crudcrud.blogspot.com/"},
            ],
            18: [
                {
                    "text": "one kiss leads to another",
                    "url": "/Popcasting/antigua%20web%20(geocities)/00%20-%2026/popcastingpop%201/onekiss.html",
                },
                {
                    "text": "sorry angel",
                    "url": "http://www.youtube.com/watch?v=ecfgTaixOCs&amp;search=jane%20birkin",
                },
                {
                    "text": "les filles n'ont…",
                    "url": "http://www.youtube.com/watch?v=KWctrxXFDt4&amp;search=birkin",
                },
            ],
            19: [
                {"text": "one ring zero", "url": "http://oneringzero.com/"},
                {"text": "josh rouse", "url": "http://www.joshrouse.com/"},
            ],
            20: [
                {
                    "text": "the cars",
                    "url": "http://www.youtube.com/watch?v=nxu5m6Ot9UU&amp;search=hello%20again%20the%20cars",
                }
            ],
            28: [
                {
                    "text": "guillaume fedou",
                    "url": "http://www.greenufos.com/web/grupos/g/guillaume.htm",
                },
                {
                    "text": "boys · a new girl born",
                    "url": "http://chromewaves.org/chromeblog.php3?which=txt&amp;x=2004_05",
                },
            ],
            29: [
                {
                    "text": "katie melua",
                    "url": "http://www.youtube.com/watch?v=eETjNikl0Uc&amp;search=melua",
                }
            ],
            31: [
                {
                    "text": "lily allen",
                    "url": "http://www.youtube.com/watch?v=D_jjuCfdksQ",
                }
            ],
            32: [
                {"text": "uffie myspace", "url": "http://www.myspace.com/uffie"},
                {
                    "text": "sing your life",
                    "url": "http://www.singyourlife.se/artists/ohm/index.php",
                },
                {"text": "ohm myspace", "url": "http://www.myspace.com/ohmsthlm"},
                {
                    "text": "diana est · tenax",
                    "url": "http://www.youtube.com/watch?v=eyWRh3JiFuM",
                },
            ],
            33: [
                {
                    "text": "joe meek (the independent)",
                    "url": "http://enjoyment.independent.co.uk/music/news/article1220485.ece",
                },
                {"text": "square america", "url": "http://squareamerica.com/"},
                {
                    "text": "when the deal goes down (video)",
                    "url": "http://www.youtube.com/watch?v=aNv02iE_9rU",
                },
                {
                    "text": "jarvis cocker myspace",
                    "url": "http://www.myspace.com/jarvspace",
                },
            ],
            34: [
                {
                    "text": "lambchop · crackers (mp3)",
                    "url": "http://www.cityslang.com/artist/17",
                }
            ],
            35: [
                {
                    "text": "yo la tengo mp3",
                    "url": "http://www.yolatengo.com/audio.html",
                },
                {"text": "mahogany", "url": "http://www.myspace.com/mahoganyinthecity"},
                {
                    "text": "music like dirt (lily allen samples)",
                    "url": "http://link: http://www.musiclikedirt.com/2006/09/27/lily-allen-alright-steal/",
                },
                {
                    "text": "pilkipedia (the ricky gervais show)",
                    "url": "http://www.pilkipedia.co.uk/wiki/index.php/Download:Xfm",
                },
            ],
            36: [
                {"text": "jenny wilson", "url": "http://www.jennywilson.net/"},
                {
                    "text": "jenny wilson & robyn carlsson – list of demands",
                    "url": "http://video.google.com/videoplay?docid=-418537696859973739",
                },
            ],
            37: [
                {
                    "text": "tom waits – christmas card from a hooker in minneapolis",
                    "url": "http://www.seikilos.com.ar/Hooker.html",
                }
            ],
            38: [
                {
                    "text": "mark kermode bbc podcast",
                    "url": "http://www.bbc.co.uk/fivelive/entertainment/kermode.shtml",
                },
                {
                    "text": "mark kermode comenta 'heart of gold' (avanzar hasta 1h 08')",
                    "url": "http://www.bbc.co.uk/radio/aod/fivelive_aod.shtml?fivelive/film061006",
                },
            ],
            39: [
                {"text": "soul-sides", "url": "http://soul-sides.com/"},
                {
                    "text": "joseph moskovitz – archive.org)",
                    "url": "http://www.archive.org/details/Joseph_Moskowitz-Panama_Pacific_Drag",
                },
            ],
            41: [
                {
                    "text": "the vinyl villain",
                    "url": "http://www.thevinylvillain.blogspot.com/",
                },
                {
                    "text": "airport girl myspace",
                    "url": "http://www.myspace.com/shamboliclofiindiepop",
                },
                {
                    "text": "sally shapiro",
                    "url": "http://www.johanagebjorn.info/sally.html",
                },
                {
                    "text": "sally shapiro myspace",
                    "url": "http://www.myspace.com/shapirosally",
                },
                {"text": "radio3.org", "url": "http://www.radiotres.org/"},
            ],
            43: [{"text": "the vinyl villain", "url": ""}],
            44: [
                {"text": "teki latex interview", "url": ""},
                {"text": "teki latex myspace", "url": ""},
                {"text": "j star myspace", "url": ""},
            ],
            45: [{"text": "steven johnson", "url": "https://stevenberlinjohnson.com/"}],
            47: [
                {"text": "crud crud", "url": "http://crudcrud.blogspot.com/"},
                {
                    "text": "jackie de shannon",
                    "url": "http://members.tripod.com/~jackiedeshannon/",
                },
                {
                    "text": "lio · 'fallait pas commencer' (youtube)",
                    "url": "http://www.youtube.com/watch?v=uT3iNeU_SQ8",
                },
                {
                    "text": "escuchas de desayuno",
                    "url": "http://escuchasdedesayuno.blogspot.com/",
                },
                {"text": "popjustice", "url": "http://www.popjustice.com/"},
                {
                    "text": "calvin harris",
                    "url": "http://www.myspace.com/calvinharristv",
                },
            ],
            50: [{"text": "sol seppy", "url": "http://www.solseppy.com/"}],
            51: [
                {
                    "text": "adam green · jessica",
                    "url": "http://www.adamgreen.net/video/video_jessica_tv.html",
                },
                {
                    "text": "vincent delerm a-z",
                    "url": "http://www.visseaux.org/delerm/personnages.htm",
                },
                {"text": "steve adey", "url": "http://www.myspace.com/steveadey"},
                {
                    "text": "alain chamfort · sinatra",
                    "url": "http://www.dailymotion.com/AlainChamfort/video/x1fmw9_sinatra?from=rss",
                },
                {
                    "text": "stereototal mp3s",
                    "url": "http://www.stereototal.de/music/download_rare.html",
                },
            ],
            53: [
                {
                    "text": "portadas escaneadas (flickr)",
                    "url": "http://www.flickr.com/gp/10215790@N05/v66q06",
                },
                {
                    "text": "delaney and bonnie video",
                    "url": "http://www.youtube.com/watch?v=8EOxy3TF3OY",
                },
                {
                    "text": "the flirtations video",
                    "url": "http://www.youtube.com/watch?v=39SjyMvBbk4",
                },
            ],
            54: [
                {
                    "text": "jane birkin & françoise hardy · comment lui dire adieu",
                    "url": "http://www.youtube.com/watch?v=Up1R81EWQJ8",
                }
            ],
            55: [
                {
                    "text": "bat for lashes video",
                    "url": "http://www.dailymotion.com/related/4258253/video/x26wnt_bat-for-lashes-whats-a-girl-to-do_music",
                },
                {
                    "text": "50 best duets ever (daily telegraph)",
                    "url": "http://www.telegraph.co.uk/arts/main.jhtml?xml=/arts/2003/11/08/bmduet08.xml",
                },
                {"text": "cloetta paris", "url": "http://www.myspace.com/cloettaparis"},
                {"text": "sally shapiro", "url": "http://www.myspace.com/shapirosally"},
                {
                    "text": "welcome collection",
                    "url": "http://www.wellcomecollection.org",
                },
                {
                    "text": "catriona irving",
                    "url": "http://www.myspace.com/catrionairving",
                },
                {
                    "text": "roisin purphy foto",
                    "url": "http://viewmorepics.myspace.com/index.cfm?fuseaction=viewImage&amp;friendID=28819230&amp;albumID=0&amp;imageID=9638276",
                },
                {
                    "text": "nick drake · a skin too few",
                    "url": "http://www.youtube.com/watch?v=_R7vzeEVoV0",
                },
                {
                    "text": "cally interview",
                    "url": "http://www.robinfrederick.com/cally.html",
                },
                {"text": "espoiler", "url": "http://blogs.elpais.com/espoiler/"},
                {
                    "text": "darren & barry (extras) · system addict",
                    "url": "http://es.youtube.com/watch?v=cy6q9T43Iyc&amp;mode=related&amp;search=",
                },
                {
                    "text": "this is england",
                    "url": "http://www.thisisenglandmovie.co.uk",
                },
            ],
            56: [
                {
                    "text": "muchachada nui",
                    "url": "https://www.youtube.com/watch?v=ok4JDaH6FRc&amp;mode=related&amp;search=",
                },
                {
                    "text": "reg kehoe video",
                    "url": "http://www.archive.org/details/SoundieF",
                },
                {
                    "text": "ojete calor · 0'60 video",
                    "url": "https://www.youtube.com/watch?v=80AvBcggCnY",
                },
                {
                    "text": "ojete calor myspace",
                    "url": "http://www.myspace.com/ojetecalorfn",
                },
                {"text": "espoiler", "url": "http://blogs.elpais.com/espoiler/"},
                {
                    "text": "a dos metros bajo tierra · final",
                    "url": "https://www.youtube.com/watch?v=WWdYMuo3_B4&amp;mode=related&amp;search=",
                },
            ],
            57: [
                {"text": "appaloosa", "url": "http://myspace.com/intimate"},
                {"text": "radio nº 1", "url": "http://radionoone.blogspot.com/"},
                {
                    "text": "bob dylan · visions of johanna (youtube)",
                    "url": "http://uk.youtube.com/watch?v=6i6NOfD48Gk",
                },
            ],
            58: [
                {
                    "text": "rachel unthank & the winterset",
                    "url": "http://www.myspace.com/rachelunthank",
                }
            ],
            59: [
                {
                    "text": "black kids myspace",
                    "url": "http://www.myspace.com/blackkidsrock",
                },
                {
                    "text": "black kids descargar disco",
                    "url": "http://www.blackkidsmusic.com/",
                },
                {
                    "text": "new yorker podcast",
                    "url": "http://www.newyorker.com/online/2007/10/22/071022on_audio_frerejones",
                },
                {"text": "blowupdoll", "url": "http://blow-up-doll.blogspot.com/"},
                {
                    "text": "une petite tasse d'anxieté (video)",
                    "url": "http://www.dailymotion.com/melodynelson1972/video/x18ebn_sgainsbourg-une-petite-tasse-danxie",
                },
                {"text": "arp myspace", "url": "http://www.myspace.com/arp001"},
                {
                    "text": "johan agebjörn myspace",
                    "url": "http://www.myspace.com/johanagebjoern",
                },
            ],
            60: [
                {
                    "text": "slumber party",
                    "url": "http://www.myspace.com/slumberpartyband",
                },
                {
                    "text": "the true story of the travelling wilburys",
                    "url": "http://www.youtube.com/watch?v=sNEFSA7sKXA",
                },
                {
                    "text": "el extraño viaje (baile de angelines)",
                    "url": "http://es.youtube.com/watch?v=1L8b3fUcF9s",
                },
                {"text": "ava leigh", "url": "http://www.myspace.com/avaleigh"},
                {"text": "duffy", "url": "http://www.myspace.com/duffymyspace"},
                {
                    "text": "swingin' mademoiselle vol I",
                    "url": "http://spikedcandy.blog-city.com/swing_mademoiselle.htm",
                },
            ],
            61: [
                {
                    "text": "slumber party",
                    "url": "http://www.myspace.com/slumberpartyband",
                },
                {
                    "text": "the true story of the travelling wilburys",
                    "url": "http://www.youtube.com/watch?v=sNEFSA7sKXA",
                },
                {
                    "text": "el extraño viaje (baile de angelines)",
                    "url": "http://es.youtube.com/watch?v=1L8b3fUcF9s",
                },
                {"text": "ava leigh", "url": "http://www.myspace.com/avaleigh"},
                {"text": "duffy", "url": "http://www.myspace.com/duffymyspace"},
                {
                    "text": "swingin' mademoiselle vol I",
                    "url": "http://spikedcandy.blog-city.com/swing_mademoiselle.htm",
                },
            ],
            62: [
                {
                    "text": "lykke li myspace/video",
                    "url": "http://www.myspace.com/lykkeli",
                },
                {"text": "winter family", "url": "http://www.myspace.com/winterfamily"},
                {
                    "text": "simone white myspace",
                    "url": "http://www.myspace.com/simonewhite",
                },
                {
                    "text": "simone white · christmas makes me blue (video)",
                    "url": "http://www.dailymotion.com/tag/white/video/x3r4gq_simone-white-christmas-makes-me-blu_music",
                },
                {"text": "fluo kids", "url": "http://fluokids.blogspot.com/"},
            ],
            63: [
                {
                    "text": "bylle baier myspace",
                    "url": "http://www.myspace.com/sibyllebaier",
                },
                {
                    "text": "robert forster · the monthly",
                    "url": "https://www.themonthly.com.au/tm/node/246",
                },
                {
                    "text": "this is tomorrow (advance)",
                    "url": "https://uk.youtube.com/profile?user=loversunitefilms",
                },
            ],
            64: [
                {"text": "flairs", "url": "http://www.myspace.com/mightyflairs"},
                {
                    "text": "benjamin biolay · les cerfs-volants",
                    "url": "http://www.dailymotion.com/video/xyheq_les-cerfsvolants_music",
                },
                {
                    "text": "the fut",
                    "url": "http://www.boingboing.net/2008/01/17/bee-gees-were-excell.html",
                },
                {"text": "boing boing", "url": "http://www.boingboing.net/"},
                {
                    "text": "hercules & love affair",
                    "url": "http://www.myspace.com/herculesandloveaffair",
                },
                {
                    "text": "twin peks · just you",
                    "url": "http://www.youtube.com/watch?v=m0t2er3qhMo&amp;feature=related",
                },
            ],
            65: [
                {
                    "text": "the independent",
                    "url": "http://www.independent.co.uk/arts-entertainment/music/features/a-star-is-born-but-is-adele-worth-all-the-hype-777865.html",
                },
                {
                    "text": "les inrockuptibles",
                    "url": "http://www.lesinrocks.com/index.php?id=62&amp;tx_article[notule]=207842&amp;tx_article[backPid]=49&amp;cHash=048183f20b",
                },
                {
                    "text": "adam & joe bbc 6",
                    "url": "http://www.bbc.co.uk/6music/shows/adamandjoe",
                },
                {"text": "trunk records", "url": "http://www.trunkrecords.com/"},
                {
                    "text": "jimmy scott · sycamore trees",
                    "url": "http://es.youtube.com/watch?v=ZA-9b69mLCA",
                },
                {
                    "text": "angelo badalamenti – laura palmer's theme",
                    "url": "http://es.youtube.com/watch?v=SwvSFOEfHJE",
                },
            ],
            66: [
                {
                    "text": "marissa nadler",
                    "url": "http://www.myspace.com/songsoftheend",
                }
            ],
            67: [
                {"text": "irene myspace", "url": "http://www.myspace.com/ireneswe"},
                {
                    "text": "irene · by your side",
                    "url": "http://es.youtube.com/watch?v=Gg_14hwF9TU",
                },
                {
                    "text": "butcher boy myspace",
                    "url": "http://www.myspace.com/butcherboymusic",
                },
            ],
            69: [
                {
                    "text": "beach house myspace",
                    "url": "http://www.myspace.com/beachhousemusic",
                },
                {
                    "text": "mort garson · music for maniacs",
                    "url": "http://musicformaniacs.blogspot.com/2008/01/mort-garson-rip.html",
                },
                {
                    "text": "gary numan @ the old grey whistle test",
                    "url": "http://es.youtube.com/watch?v=Uu6MDdxBork&amp;feature=related",
                },
                {
                    "text": "gary numan @ totp",
                    "url": "http://es.youtube.com/watch?v=y9W3y-qCkso",
                },
                {
                    "text": "victrola favourites",
                    "url": "http://www.boomkat.com/item.cfm?id=73098",
                },
                {"text": "jim flora", "url": "http://www.jimflora.com/"},
            ],
            72: [
                {"text": "mojo4music", "url": "http://www.mojo4music.com"},
                {
                    "text": "pet shop boys · my girl",
                    "url": "http://www.petshopboys.co.uk/",
                },
                {"text": "gangstagrass", "url": "http://www.renchaudio.com/"},
            ],
            73: [
                {
                    "text": "bo diddley · roadrunner",
                    "url": "http://es.youtube.com/watch?v=qs8FJergjas",
                },
                {
                    "text": "mystery jets · two doors down",
                    "url": "http://es.youtube.com/watch?v=qs8FJergjas",
                },
                {
                    "text": "elli et jacno · téléphone",
                    "url": "http://www.youtube.com/watch?v=djgxWoqdeQY",
                },
            ],
            74: [
                {"text": "volume", "url": "http://volume-lemag.com/"},
                {
                    "text": "myspace dessous chics",
                    "url": "http://www.myspace.com/dessouschics",
                },
            ],
            75: [
                {
                    "text": "sunny summer day (letterbox records",
                    "url": "http://www.letterboxrecords.com/sunbio.htm",
                }
            ],
            76: [
                {
                    "text": "popcasting 76 en FLICKR · cintas, cds y mojo escaneados",
                    "url": "http://www.flickr.com/photos/10215790@N05/sets/72157605722212133/detail/",
                },
                {
                    "text": "cassette from my ex",
                    "url": "http://www.cassettefrommyex.com/",
                },
                {
                    "text": "thompson twins · lay your hands on m (tve, 'tocata')",
                    "url": "http://www.youtube.com/watch?v=N37wpBoxey0",
                },
                {
                    "text": "mojo blog · 'C30, C60, C90 …gone?'",
                    "url": "http://www.mojo4music.com/blog/2008/04/c30_c60_c90_gone_1.html",
                },
                {
                    "text": "thurston moore en wired",
                    "url": "http://www.wired.com/wired/archive/13.04/play.html?pg=3",
                },
                {
                    "text": "flickr group · 'c30, c60, c90, go!'",
                    "url": "http://www.flickr.com/groups/c30c60c90go/pool/",
                },
                {
                    "text": "dalston oxfam shop",
                    "url": "http://dalstonoxfamshop.blogspot.com/2008/05/euro-disco.html",
                },
                {"text": "mixwit", "url": "http://www.mixwit.com/create"},
            ],
            77: [
                {
                    "text": "santi campos en rock indiana",
                    "url": "http://www.rockindiana.biz/santicampos/index.html",
                }
            ],
            78: [{"text": "archivo de cuñas de popcasting", "url": "cues.html"}],
            79: [
                {
                    "text": "kitty daisy & lewis",
                    "url": "http://www.myspace.com/kittydaisyandlewis",
                },
                {
                    "text": "woman's world · graham rawle",
                    "url": "http://www.grahamrawle.com/books_womans/popup.html",
                },
                {"text": "peggy sue's", "url": "http://www.peggysues.es/"},
                {"text": "son of rambow", "url": "http://www.sonoframbow.com"},
                {
                    "text": "serge gainsbourg · la naissance de initials bb",
                    "url": "http://es.youtube.com/watch?v=spJVbTMSFfI&amp;feature=related",
                },
                {
                    "text": "max richter · 24 postcards in full colour",
                    "url": "http://www.24postcards.co.uk/",
                },
            ],
            80: [
                {
                    "text": "jerry wexler video",
                    "url": "http://es.youtube.com/watch?v=0l1F_8DEAbs",
                },
                {
                    "text": "bbc the producers",
                    "url": "http://www.bbc.co.uk/radio2/musicclub/doc_recordproducers.shtml",
                },
                {
                    "text": "the producers · especial brian wilson",
                    "url": "http://www.mediafire.com/?5qwnjgitwqy",
                },
            ],
            82: [
                {"text": "gastmans myspace", "url": "http://www.myspace.com/gastmans"},
                {
                    "text": "jarvis cocker on bbc 6music",
                    "url": "http://www.mediafire.com/?mzvyemymtyy",
                },
            ],
            83: [
                {
                    "text": "parenthetical girls myspace",
                    "url": "http://www.myspace.com/parentheticalgirlsband",
                }
            ],
            84: [
                {
                    "text": "pete drake · forever (video)",
                    "url": "http://www.boingboing.net/2008/11/17/old-video-of-talking.html",
                },
                {
                    "text": "john and jehn myspace",
                    "url": "http://www.myspace.com/johnjehn",
                },
                {
                    "text": "mojo november 1993",
                    "url": "http://cover.mojo4music.com/Item.aspx?pageNo=1568&amp;year=1993",
                },
                {
                    "text": "françoise breut · el pais",
                    "url": "http://www.elpais.com/articulo/cultura/Francoiz/Breut/estrena/disco/ELPAIScom/elpepucul/20081128elpepucul_2/Tes",
                },
                {"text": "green ufos", "url": "http://www.greenufos.com"},
            ],
            85: [
                {
                    "text": "bob dylan's theme time radio",
                    "url": "http://croz.fm/pages/ttrh.html",
                },
                {
                    "text": "the american song poem christmas",
                    "url": "http://www.hdtracks.com/index.php?file=catalogdetail&amp;valbum_code=032862014727",
                },
                {"text": "sir shambling", "url": "http://www.sirshambling.com"},
                {
                    "text": "sir shambling soulful christmas",
                    "url": "http://www.sirshambling.com/articles/soulful_christmas.html",
                },
            ],
            86: [
                {
                    "text": "greatest decade weekly",
                    "url": "http://www.greatestdecadeweekly.podomatic.com",
                },
                {
                    "text": "myspace mittens",
                    "url": "http://www.myspace.com/mittensmittens",
                },
            ],
            87: [
                {
                    "text": "m ward at npr",
                    "url": "http://www.npr.org/templates/story/story.php?storyId=99084694",
                },
                {
                    "text": "the alchemists of sound",
                    "url": "http://www.youtube.com/watch?v=cKPGzX5kZd0&amp;feature=related",
                },
            ],
            88: [
                {
                    "text": "paisley underground",
                    "url": "http://www.youtube.com/watch?v=liud5ZPtteI",
                }
            ],
            89: [
                {
                    "text": "club quebrantahuesos",
                    "url": "http://www.myspace.com/clubquebranta",
                },
                {"text": "numero group", "url": "http://www.myspace.com/clubquebranta"},
                {
                    "text": "nick garrie elefant records",
                    "url": "http://www.elefant.com/grupos/nick-garrie/discografia",
                },
                {
                    "text": "westex digs speedy west",
                    "url": "https://westexdigs.blogspot.com/2008/06/swingin-summer-sounds-of-speedy-west.html",
                },
                {
                    "text": "westex digs nancy jukebox",
                    "url": "https://westexdigs.blogspot.com/2008/06/swingin-summer-sounds-of-speedy-west.html",
                },
            ],
            90: [
                {
                    "text": "dust on the stylus",
                    "url": "http://dustonthestylus.blogspot.com/2009/01/johnny-johnson-his-bandwagon-mr.html",
                },
                {
                    "text": "jarvis cocker & richard hawley bbc 6music",
                    "url": "http://www.mediafire.com/?zlcnmnghuud",
                },
            ],
            91: [
                {
                    "text": "cramps MP3s",
                    "url": "http://www.phawker.com/2009/02/09/listen-like-thieves-songs-the-cramps-taught-us/",
                },
                {"text": "very short list", "url": "http://www.veryshortlist.com/"},
            ],
        }

    def get_episodes_to_process(self) -> list[dict]:
        """Obtiene los episodios que necesitan restauración o limpieza de enlaces."""
        try:
            # Obtener todos los episodios que tienen enlaces definidos o necesitan limpieza
            episode_numbers = list(self.correct_links.keys()) + self.episodes_to_clean
            response = (
                self.db.client.table("podcasts")
                .select("id, program_number, title, web_extra_links")
                .in_("program_number", episode_numbers)
                .order("program_number")
                .execute()
            )

            return response.data
        except Exception as e:
            logger.error(f"Error obteniendo episodios para procesar: {e}")
            return []

    def process_episodes_links(self) -> dict:
        """Restaura o limpia los enlaces extras de los episodios especificados."""
        logger.info("🔄 Procesando enlaces extras de episodios...")

        episodes = self.get_episodes_to_process()
        restored_count = 0
        cleaned_count = 0
        errors = 0
        total_links_restored = 0

        for episode in episodes:
            program_number = episode["program_number"]
            episode_id = episode["id"]

            # Verificar si este episodio debe limpiarse
            if program_number in self.episodes_to_clean:
                try:
                    # Limpiar enlaces extras
                    response = (
                        self.db.client.table("podcasts")
                        .update({"web_extra_links": None, "last_web_check": "now()"})
                        .eq("id", episode_id)
                        .execute()
                    )

                    if response.data:
                        logger.info(
                            f"🧹 Episodio #{program_number} limpiado (sin enlaces)"
                        )
                        cleaned_count += 1
                    else:
                        logger.error(
                            f"❌ No se pudo limpiar episodio #{program_number}"
                        )
                        errors += 1

                except Exception as e:
                    logger.error(f"❌ Error limpiando episodio #{program_number}: {e}")
                    errors += 1

            # Verificar si este episodio tiene enlaces correctos definidos
            elif program_number in self.correct_links:
                correct_links = self.correct_links[program_number]

                try:
                    # Actualizar con los enlaces correctos
                    response = (
                        self.db.client.table("podcasts")
                        .update(
                            {
                                "web_extra_links": json.dumps(correct_links),
                                "last_web_check": "now()",
                            }
                        )
                        .eq("id", episode_id)
                        .execute()
                    )

                    if response.data:
                        logger.info(
                            f"✅ Episodio #{program_number} restaurado ({len(correct_links)} enlaces)"
                        )
                        restored_count += 1
                        total_links_restored += len(correct_links)
                    else:
                        logger.error(
                            f"❌ No se pudo actualizar episodio #{program_number}"
                        )
                        errors += 1

                except Exception as e:
                    logger.error(
                        f"❌ Error restaurando episodio #{program_number}: {e}"
                    )
                    errors += 1
            else:
                logger.info(
                    f"ℹ️  Episodio #{program_number} no tiene enlaces definidos (se mantiene NULL)"
                )

        return {
            "total_episodes": len(episodes),
            "restored": restored_count,
            "cleaned": cleaned_count,
            "errors": errors,
            "total_links_restored": total_links_restored,
        }

    def verify_processing(self) -> str:
        """Verifica que el procesamiento se realizó correctamente."""
        logger.info("🔍 Verificando procesamiento...")

        episodes = self.get_episodes_to_process()

        report = []
        report.append("=" * 80)
        report.append("VERIFICACIÓN DE PROCESAMIENTO - EPISODIOS CON ENLACES")
        report.append("=" * 80)
        report.append("")

        episodes_with_links = 0
        episodes_without_links = 0

        report.append("📄 ESTADO DE LOS EPISODIOS:")
        for episode in episodes:
            program_number = episode["program_number"]
            web_extra_links = episode.get("web_extra_links")
            current_links = []

            if web_extra_links:
                try:
                    current_links = json.loads(web_extra_links)
                    if not isinstance(current_links, list):
                        current_links = []
                except json.JSONDecodeError:
                    current_links = []

            has_links = len(current_links) > 0
            expected_links = len(self.correct_links.get(program_number, []))
            should_be_clean = program_number in self.episodes_to_clean

            if has_links:
                episodes_with_links += 1
                status = "✅" if not should_be_clean else "❌"
            else:
                episodes_without_links += 1
                status = "✅" if should_be_clean else "❌"

            report.append(f"  {status} #{program_number:2d}: {episode['title']}")
            report.append(f"      Enlaces actuales: {len(current_links)}")
            report.append(f"      Enlaces esperados: {expected_links}")

            if should_be_clean:
                if not has_links:
                    report.append("      Estado: ✅ CORRECTO (limpiado)")
                else:
                    report.append("      Estado: ❌ INCORRECTO (debería estar limpio)")
            elif has_links and expected_links > 0:
                if len(current_links) == expected_links:
                    report.append("      Estado: ✅ CORRECTO")
                else:
                    report.append("      Estado: ⚠️  DISCREPANCIA")
            elif not has_links and expected_links == 0:
                report.append("      Estado: ✅ CORRECTO (sin enlaces)")
            else:
                report.append("      Estado: ❌ INCORRECTO")
            report.append("")

        report.append("📊 RESUMEN DE VERIFICACIÓN:")
        report.append(f"  - Total de episodios: {len(episodes)}")
        report.append(f"  - Episodios con enlaces: {episodes_with_links}")
        report.append(f"  - Episodios sin enlaces: {episodes_without_links}")

        report.append("=" * 80)
        return "\n".join(report)


def main():
    """Función principal."""
    restorer = EpisodesLinkRestorer()

    print("=" * 80)
    print("RESTAURACIÓN DE ENLACES EXTRAS - EPISODIOS ESPECÍFICOS")
    print("=" * 80)
    print("🔄 Restaurando enlaces extras correctos basados en información original")
    print("")

    # Procesar episodios
    results = restorer.process_episodes_links()

    # Mostrar resumen
    print("=" * 80)
    print("RESUMEN DE PROCESAMIENTO")
    print("=" * 80)
    print(f"📊 Total de episodios: {results['total_episodes']}")
    print(f"✅ Episodios restaurados: {results['restored']}")
    print(f"🧹 Episodios limpiados: {results['cleaned']}")
    print(f"❌ Errores: {results['errors']}")
    print(f"🔗 Enlaces restaurados: {results['total_links_restored']}")
    print("=" * 80)

    # Verificar procesamiento
    verification_report = restorer.verify_processing()
    print(verification_report)

    logger.info("✅ Restauración de episodios completada")


if __name__ == "__main__":
    main()
