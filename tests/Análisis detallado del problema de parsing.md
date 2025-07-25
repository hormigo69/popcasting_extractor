# Análisis detallado del problema de parsing

## Problema identificado

El parser actual no maneja correctamente los separadores y está mezclando múltiples canciones en una sola entrada.

## Ejemplo del episodio 317 en el RSS original:

```
yyxy · love4eva  :: en attendant ana · the violence inside  :: young scum · freak out :: bob dylan · simple twist of fate  :: pi ja ma · ponytail :: let's eat grandma · falling into me ::  evie sands · one fine summer morning :: the sadies · a good flying day  :: bruno mars · magic :: jean-françois coen · vive l'amour :: bobbie gentry · thunder in the afternoon  :: véronique jannot & laurent voulzy · désir désir :: kelley stoltz · where you will :: chic · i want your love  :: mcguinn clark & hillman · surrender to me :: melenas · gira :: the goon sax · time 4 love :: las felindras · françoise implose  :: dusk · leaf :: elvis presley · are you lonesome tonight? (live) :: chin up · the rhythm method :: tristen · glass jar :: maki asakawa · konna fu ni sugite iku  ::  sugar and tiger · perruque rose :: alger patcho · rocky patcho :: módulos · nada me importa :: betty troupe · ms 20 :: bmx bandits · I can't stand mad at you  :: bombón · i wanna surf like anette :: daddy issues · all my girls :: scott mannion · the substance that i can't live without
```

## Resultado actual (incorrecto):

```json
{
  "position": 1,
  "artist": "yyxy",
  "song": "love4eva  :: en attendant ana · the violence inside  :: young scum · freak out"
},
{
  "position": 2,
  "artist": "bob dylan",
  "song": "simple twist of fate  :: pi ja ma · ponytail"
}
```

## Resultado esperado (correcto):

```json
{
  "position": 1,
  "artist": "yyxy",
  "song": "love4eva"
},
{
  "position": 2,
  "artist": "en attendant ana",
  "song": "the violence inside"
},
{
  "position": 3,
  "artist": "young scum",
  "song": "freak out"
},
{
  "position": 4,
  "artist": "bob dylan",
  "song": "simple twist of fate"
},
{
  "position": 5,
  "artist": "pi ja ma",
  "song": "ponytail"
}
```

## Análisis del formato:

1. **Separador principal**: ` :: ` (espacio + dos puntos + dos puntos + espacio)
2. **Separador artista-canción**: ` · ` (espacio + punto medio + espacio)
3. **Problema**: El parser actual divide por ` :: ` pero no verifica si cada parte tiene el formato correcto `artista · canción`
4. **Espacios variables**: Algunos separadores tienen espacios extra o faltantes

## Solución propuesta:

1. Dividir por ` :: ` como separador principal
2. Para cada parte, verificar si contiene ` · `
3. Si contiene ` · `, dividir en artista y canción
4. Si no contiene ` · `, es probablemente parte de la canción anterior o un error
5. Manejar espacios extra y caracteres especiales
6. Filtrar enlaces y texto extra al final

