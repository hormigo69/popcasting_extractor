import json
import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


from dotenv import load_dotenv
from supabase_database import get_supabase_connection  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))


#!/usr/bin/env python3
"""
Script para actualizar manualmente la playlist y el número de canciones de episodios concretos en Supabase.

Incluye todas las correcciones manuales realizadas:
- #64, #72, #76, #92, #96, #109, #143, #200, #245, #283

Uso: Ejecuta este script para aplicar todas las correcciones manuales de playlists.
"""


# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))


def update_playlist(program_number, playlist):
    db = get_supabase_connection()
    response = (
        db.client.table("podcasts")
        .select("id")
        .eq("program_number", program_number)
        .execute()
    )
    if not response.data:
        print(f"❌ Episodio #{program_number} no encontrado en la base de datos")
        return False
    podcast_id = response.data[0]["id"]
    db.update_web_info(
        podcast_id=podcast_id,
        web_playlist=json.dumps(playlist, ensure_ascii=False),
        web_songs_count=len(playlist),
    )
    print(f"✅ Episodio #{program_number} actualizado con {len(playlist)} canciones.")
    return True


def main():
    # --- PLAYLISTS MANUALES ---
    playlists = {
        64: [
            {"position": 1, "artist": "sandra", "title": "secret land"},
            {"position": 2, "artist": "flairs", "title": "better than prince"},
            {"position": 3, "artist": "supergrass", "title": "diamond hoo ha man"},
            {"position": 4, "artist": "lykke li", "title": "i'm good i'm gone"},
            {"position": 5, "artist": "tennessee ernie ford", "title": "16 tons"},
            {"position": 6, "artist": "benjamin biolay", "title": "les cerfs volants"},
            {"position": 7, "artist": "the fut", "title": "have you heard the word"},
            {
                "position": 8,
                "artist": "hercules and love affair (ft antony)",
                "title": "blind",
            },
            {
                "position": 9,
                "artist": "the paris sisters",
                "title": "love how you love me",
            },
            {
                "position": 10,
                "artist": "julee cruise",
                "title": "rockin' back inside my heart",
            },
            {"position": 11, "artist": "james, donna, maddie", "title": "just you"},
        ],
        72: [
            {
                "position": 1,
                "artist": "vincent vincent and the villains",
                "title": "killing time",
            },
            {
                "position": 2,
                "artist": "bobby gentry and jody reynolds",
                "title": "requiem for love",
            },
            {
                "position": 3,
                "artist": "michèle mercier",
                "title": "la fille qui fait tchic tit chic",
            },
            {"position": 4, "artist": "pete molinari", "title": "sweet louise"},
            {
                "position": 5,
                "artist": "fabienne del sol",
                "title": "i'm gonna catch me a rat",
            },
            {"position": 6, "artist": "scarlett johansson", "title": "fannin' street"},
            {"position": 7, "artist": "pet shop boys", "title": "my girl"},
            {"position": 8, "artist": "the go-go's", "title": "our lips are sealed"},
            {"position": 9, "artist": "gangstagrass", "title": "goin' down"},
            {"position": 10, "artist": "marie gillain", "title": "sans mensonge"},
        ],
        76: [
            {
                "position": 1,
                "artist": "the detroit spinners",
                "title": "i'll always love you",
            },
            {"position": 2, "artist": "the chills", "title": "doledrums"},
            {
                "position": 3,
                "artist": "thompson twins",
                "title": "lay your hands on me",
            },
            {
                "position": 4,
                "artist": "bande à part",
                "title": "le courant passe… te quiero",
            },
            {
                "position": 5,
                "artist": "cowboy junkies",
                "title": "murder, tonight, in the trailer park",
            },
            {"position": 6, "artist": "adrienne poster", "title": "backstreet girl"},
            {"position": 7, "artist": "r.e.m.", "title": "sitting still"},
            {"position": 8, "artist": "10,000 maniacs", "title": "sally ann"},
            {"position": 9, "artist": "chantays", "title": "wayward nile"},
            {"position": 10, "artist": "dani", "title": "ding dong"},
            {"position": 11, "artist": "sharpe & numan", "title": "change your mind"},
            {"position": 12, "artist": "charlie mccoy", "title": "cherry berry wine"},
            {
                "position": 13,
                "artist": "dalida & alain delon",
                "title": "parole, parole",
            },
            {"position": 14, "artist": "helen merrill", "title": "willow weep for me"},
        ],
        92: [
            {"position": 1, "artist": "dolly parton", "title": "jolene"},
            {"position": 2, "artist": "eels", "title": "my timing is off"},
            {"position": 3, "artist": "bat for lashes", "title": "a forest"},
            {
                "position": 4,
                "artist": "siouxie and the banshees",
                "title": "hong kong garden",
            },
            {"position": 5, "artist": "peaches", "title": "lose you"},
            {"position": 6, "artist": "johnny legend", "title": "green light"},
            {"position": 7, "artist": "asobi seksu", "title": "transparence"},
            {
                "position": 8,
                "artist": "little boots",
                "title": "new in town (no one is safe · al kapranos remix)",
            },
            {
                "position": 9,
                "artist": "mickey and silvia",
                "title": "love is strange (take 4)",
            },
            {"position": 10, "artist": "the coasters", "title": "i'm a hog for you"},
            {"position": 11, "artist": "johnny burnette trio", "title": "honey hush"},
        ],
        96: [
            {"position": 1, "artist": "dolly parton", "title": "jolene"},
            {"position": 2, "artist": "eels", "title": "my timing is off"},
            {"position": 3, "artist": "bat for lashes", "title": "a forest"},
            {
                "position": 4,
                "artist": "siouxie and the banshees",
                "title": "hong kong garden",
            },
            {"position": 5, "artist": "peaches", "title": "lose you"},
            {"position": 6, "artist": "johnny legend", "title": "green light"},
            {"position": 7, "artist": "asobi seksu", "title": "transparence"},
            {
                "position": 8,
                "artist": "little boots",
                "title": "new in town (no one is safe · al kapranos remix)",
            },
            {
                "position": 9,
                "artist": "mickey and silvia",
                "title": "love is strange (take 4)",
            },
            {"position": 10, "artist": "the coasters", "title": "i'm a hog for you"},
            {"position": 11, "artist": "johnny burnette trio", "title": "honey hush"},
        ],
        109: [
            {"position": 1, "artist": "bob dylan", "title": "must be santa"},
            {
                "position": 2,
                "artist": "the paris sisters",
                "title": "christmas in my hometown",
            },
            {
                "position": 3,
                "artist": "the leisure society",
                "title": "the last of the melting snow",
            },
            {
                "position": 4,
                "artist": "jacques dutronc",
                "title": "la fille du père noël",
            },
            {
                "position": 5,
                "artist": "julian casablancas",
                "title": "i wish it was christmas today",
            },
            {
                "position": 6,
                "artist": "the free design",
                "title": "close your mouth (it's christmas)",
            },
            {"position": 7, "artist": "the hit parade", "title": "i love christmas"},
            {
                "position": 8,
                "artist": "electric jungle",
                "title": "funky funky christmas",
            },
            {"position": 9, "artist": "jimmy butler", "title": "trim your tree"},
            {"position": 10, "artist": "the trashmen", "title": "dancin' with santa"},
            {"position": 11, "artist": "valerie masters", "title": "christmas calling"},
            {
                "position": 12,
                "artist": "vashti & twice as much",
                "title": "the coldest night of the year",
            },
            {
                "position": 13,
                "artist": "rufus wainwright",
                "title": "spotlight on christmas",
            },
            {"position": 14, "artist": "the waitresses", "title": "christmas wrappin'"},
        ],
        143: [
            {"position": 1, "artist": "cyril díaz", "title": "taboo"},
            {"position": 2, "artist": "metronomy", "title": "the look"},
            {"position": 3, "artist": "daphné", "title": "l'homme à la peau musicale"},
            {"position": 4, "artist": "ramones", "title": "i can't make it on time"},
            {"position": 5, "artist": "george jones", "title": "the door"},
            {"position": 6, "artist": "lykke li", "title": "i follow rivers"},
            {
                "position": 7,
                "artist": "dobie gray",
                "title": "out on the floor (neil's all night mix)",
            },
            {"position": 8, "artist": "yo la tengo", "title": "can't forget"},
            {"position": 9, "artist": "freddy", "title": "tengo"},
            {"position": 10, "artist": "kid congo", "title": "rare as the yeti"},
            {"position": 11, "artist": "veronica maggio", "title": "jag kommer"},
            {"position": 12, "artist": "summer fiction", "title": "chandeliers"},
            {"position": 13, "artist": "john maus", "title": "believer"},
        ],
        200: [
            {"position": 1, "artist": "the go-betweens", "title": "people say"},
            {"position": 2, "artist": "king nawahi", "title": "honolulu bound"},
            {"position": 3, "artist": "pulp", "title": "something changed"},
            {
                "position": 4,
                "artist": "the waterboys",
                "title": "the whole of the moon",
            },
            {"position": 5, "artist": "world party", "title": "is it like today?"},
            {"position": 6, "artist": "paul mauriat", "title": "meme si tu revenais"},
            {"position": 7, "artist": "scott walker", "title": "i threw it all away"},
            {"position": 8, "artist": "boys", "title": "a new girl born"},
            {"position": 9, "artist": "april showers", "title": "abandon ship"},
            {"position": 10, "artist": "the bats", "title": "calm before the storm"},
            {"position": 11, "artist": "astropuppees", "title": "underdog"},
            {"position": 12, "artist": "los bichos", "title": "nip of hate"},
            {"position": 13, "artist": "the walkabouts", "title": "nightbirds"},
            {
                "position": 14,
                "artist": "charles trenet",
                "title": "le retour des saisons",
            },
        ],
        245: [
            {"position": 1, "artist": "femme fantasm", "title": "moon weather"},
            {"position": 2, "artist": "lonnie donegan", "title": "ham and eggs"},
            {
                "position": 3,
                "artist": "david werner",
                "title": "the ballad of trixie silver",
            },
            {
                "position": 4,
                "artist": "david kauffman & eric caboor",
                "title": "kiss another day goodbye",
            },
            {"position": 5, "artist": "phil harvey", "title": "bumbershoot"},
            {
                "position": 6,
                "artist": "bob b. soxx & the blue jeans",
                "title": "zip a dee doo dah",
            },
            {
                "position": 7,
                "artist": "the pailey brothers",
                "title": "come out and play",
            },
            {
                "position": 8,
                "artist": "the mamas and the papas",
                "title": "glad to be unhappy",
            },
            {"position": 9, "artist": "frank wilson", "title": "do i love you"},
            {"position": 10, "artist": "slim twig", "title": "slippin' and slidin'"},
            {
                "position": 11,
                "artist": "velvet morning",
                "title": "you're blue, i'm blue",
            },
            {"position": 12, "artist": "finnmark", "title": "transpennine express"},
            {"position": 13, "artist": "randy newman", "title": "rollin'"},
            {"position": 14, "artist": "lou christie", "title": "if my car could talk"},
            {
                "position": 15,
                "artist": "nato",
                "title": "je t'apprendrai à faire l'amour",
            },
            {
                "position": 16,
                "artist": "steely dan",
                "title": "only a fool would say that",
            },
            {"position": 17, "artist": "kevin morby", "title": "motors running"},
            {"position": 18, "artist": "pale lights", "title": "fourteen stories tall"},
            {"position": 19, "artist": "the shadows", "title": "shindig"},
            {
                "position": 20,
                "artist": "gerry rafferty",
                "title": "right down the line",
            },
            {"position": 21, "artist": "aline", "title": "avenue des armées"},
            {"position": 22, "artist": "niagara", "title": "l'amour à la plage"},
            {"position": 23, "artist": "ronnie spector", "title": "try some, buy some"},
            {"position": 24, "artist": "hinds", "title": "chili town"},
            {"position": 25, "artist": "kyo", "title": "le graal"},
            {"position": 26, "artist": "the marketts", "title": "out of limits"},
            {
                "position": 27,
                "artist": "the beach boys",
                "title": "keep an eye on summer",
            },
            {"position": 28, "artist": "tame impala", "title": "let it happen"},
            {"position": 29, "artist": "botibol", "title": "croyez moi"},
            {"position": 30, "artist": "bad bad hats", "title": "super america"},
            {"position": 31, "artist": "les fils de joie", "title": "plaisirs chers"},
            {
                "position": 32,
                "artist": "sharon van etten",
                "title": "i don't want to let you down",
            },
            {"position": 33, "artist": "aimee mann", "title": "stupid thing"},
        ],
        283: [
            {
                "position": 1,
                "artist": "plastic bertrand",
                "title": "tout petit la planete",
            },
            {"position": 2, "artist": "jodie foster", "title": "la vie c'est chouet'"},
            {"position": 3, "artist": "sylvan", "title": "we don't belong"},
            {
                "position": 4,
                "artist": "charlotte rampling",
                "title": "les grains de sable",
            },
            {"position": 5, "artist": "eggstone", "title": "supermeaningfecktyless"},
            {"position": 6, "artist": "exnovios", "title": "ahhhhh!"},
            {
                "position": 7,
                "artist": "the orielles",
                "title": "sugar tastes like salt",
            },
            {
                "position": 8,
                "artist": "john andrews & the yawns",
                "title": "the drivers",
            },
            {"position": 9, "artist": "linda mccartney", "title": "i got up"},
            {"position": 10, "artist": "chuck berry", "title": "down bound train"},
            {"position": 11, "artist": "chuck berry", "title": "you can't catch me"},
            {"position": 12, "artist": "anna makirere", "title": "e avatea e"},
        ],
    }

    for program_number, playlist in playlists.items():
        print(f"\n--- Actualizando episodio #{program_number} ---")
        update_playlist(program_number, playlist)


if __name__ == "__main__":
    main()
