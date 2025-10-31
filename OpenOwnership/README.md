# Lese og forstå OpenOwnership

Det er to problemer:
- Filene er ikke syntaktisk riktig JSON, ettersom de inneholder mange
  objekter; strengt tatt skal en fil som holder JSON bare ha ett (1)
  objekt, og
- Det er vanskelig å forstå hva som er de interessante feltene.

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
    # Anta at objekt holder et Python-objekt, lest inn fra JSON 
	from datetime import datetime
	if "statementDate" in objekt:
	    statementDate = datetime.strptime(objekt[statementDate"], "%y-%m-%d")
	#
	if "statementID" in objekt:
	    statementID = int(objekt[statementID"])
	#
	if "identifiers" in objekt:
	    if "id" in objekt["identifiers"]:
		    objekt["identifiers"]["id"] =
			int(objekt["identifiers"]["id"])
		#
	#
```

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

### Link mellom objektene

Når objektene er lastet inn (i Neo4j) må det settes opp relasjoner.
De relevante er:
```
