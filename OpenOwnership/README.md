# Lese og forstå OpenOwnership

## Splitte datasettet
Datasettet er `3.981.754.847`bytes **komprimert** mens det i full
størrelse er `40.140.119.733` bytes (ca 38 GB).  Det inneholder
`36.508.905` linjer hvor hver linje er ett objekt som beskriver et
selskap, en person, eller en økonomisk relasjon mellom selskap og/eller
person(er).

For å hente ut et gitt antall linjer, for eksempel 100, lager man en
datastrøm:
```
unzip -p datasett.zip  | head -n 100 > fil.json
```

## Syntaktiske problemer
Det er noen utfordringer:
- Filene er ikke syntaktisk riktig JSON, ettersom de inneholder mange
  objekter; strengt tatt skal en fil som holder JSON bare ha ett (1)
  objekt;
- Alle verdier er `str` selv om de burde være tall eller dato, og
- Det er vanskelig å forstå hva som er de interessante feltene.
- 

## Lese inn objektene

For å lese (vilkårlige) JSON-objekter på fil, uten å anta at alle
objektene er på egen linje, krever en litt komplisert parser.  Den
leser et stykke data, leter fra begynnelsen etter objekter, og
returnerer dem ett og ett.  Den antar ikke at objektene er inntil
hverandre (uten _white space_ mellom dem).

Her er koden for å lese filene:
```
from json import JSONDecoder
from functools import partial


def json_parse(fileobj, 
	decoder = JSONDecoder(), 
	maxbuffer = 1048576): # 1 << 20
    
    data = ''
    for pakke in iter(partial(fileobj.read, maxbuffer), ''):
        data += pakke
        while data:
            try:
                renset = data.strip()
                objekt, index = decoder.raw_decode(renset)
                yield objekt
                data = renset[index:]
            except ValueError:
                # Trenger mer data; leser inn
                break
	    #yrt
	#elihw
     #rof
#fed
```
og den brukes slik:
```
with open("100000.json", "r") as fd:
    teller = 0
    for objekter in json_parse(fd):
        teller += 1
		# Gjør noe med objektet, for eksempel laste
		# det inn i en database
    #rof
    print(f"Antall objekter: {teller}")
#
#
# Antall objekter: 100000
```

### Type på objektet

Typen på objektet er å finne i feltet `objekt["statementType"]`.  Jeg
har kun funnet tre typer så langt:

- `personStatement` som beskriver en person
- `entityStatement` beskriver et selskap
- `ownershipOrControlStatement` viser eierskap i selskap (knytter
person og selskaper sammen 

I **første runde** setter vi typen av nodene til én av disse tre.

Koden
```
with open("100000.json", "r") as fd:
    typer = {"personStatement": 0,
             "entityStatement": 0,
             "ownershipOrControlStatement": 0}
    for objekter in json_parse(fd):
        typer[objekter["statementType"]] += 1
    #rof
    print(typer)
#
```
skriver ut
```
{'personStatement': 21497, 
'entityStatement': 36573,
'ownershipOrControlStatement': 41930}
```
og en rask summering viser at det er akkurat 100.000 (som forventet).


### Konvertere datafelt

I filene så er alle dataelementer kodet som strenger.  Det vil si at 
```
   "id" : "12345",
   "dato": "2025-10-31",
   ...
```
Det må vi gjøre noe, for ytelsens skyld.  Her er koden for de feltene
jeg tror er viktige:
```
	if "statementID" in objekt:
		objekt["statementID"] = int(objekt["statementID"])
	#
	if "interestedParty" in objekt:
		if "describedByPersonStatement" in objekt["interestedParty"]:
			objekt["interestedParty"]["describedByPersonStatement"] = \
				int(objekt["interestedParty"]["describedByPersonStatement"])
	    #
	#
	if "identifiers" in objekt:
		# Er en liste (sukk og dobbeltsukk)
		if "id" in objekt["identifiers"][0]:
			ids = objekt["identifiers"]
			objekt["identifiers"][0]["id"] = \
				int(objekt["identifiers"][0]["id"])
	    #
	#
	if "subject" in objekt:
		if "describedByEntityStatement" in objekt["subject"]:
			objekt["subject"]["describedByEntityStatement"] = \
				int(objekt["subject"]["describedByEntityStatement"])
	    #fi
	#fi
```
Det er sikkert flere!


## Knytte objektene sammen

### Unik id for alle objekter

Det første er å finne den unike identifikatoren.  Her er koden:
```
    # Vi kjører koden over, slik at objekt holder et JSON-objekt
	try:
        unik_id = int(objekt["identifiers"]["id"])
	except ValueError:
	    print(f"Error ikke INT: {unik_id}")
	
```
Variabelen `unik_id` holder nå en `int` som er unik i datasettet.  Den
kan brukes til å identifisere noder.

### Aksjeeiere

Objekter av type `ownershipOrControlStatement` viser eierskap, altså
hvor mange aksjer en person eier i et selskap.  Hvilket selskap det er
snakk om, det finner vi i feltet
```
    objekt["subject"]["describedByEntityStatement"]
```
Selskapet vil være av typen `entityStatement`.  Personen det er
snakk om, som altså eier aksjene, er beskrevet i feltet
```
	objekt["interestedParty"]["describedByPersonStatement"]
```
Jeg har så langt ikke funnet aksjeeiere som ikke er personer, men det
synes jeg er litt snodig.  Trolig er det bare at jeg ikke har kommet
over det enda.


