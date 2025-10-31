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
    #rof
    print(f"Antall objekter: {teller}")
#
#
# Antall objekter: 100000
```
