from json import JSONDecoder
from functools import partial
from datetime import datetime

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
            if "statementDate" in objekt:
                try:
                    statementDate = datetime.strptime(objekt["statementDate"], "%Y-%m-%d")
                except ValueError:
                    print(objekt)
                    raise
            if "statementID" in objekt:
                statementID = int(objekt["statementID"])
	    #
            if "identifiers" in objekt:
                if "id" in objekt["identifiers"]:
                    objekt["identifiers"]["id"] = int(objekt["identifiers"]["id"])
		#
	    #
	#elihw
     #rof
#fed

with open("100000.json", "r") as fd:
    teller = 0
    for objekter in json_parse(fd):
        teller += 1
    #rof
    print(f"Antall objekter: {teller}")
#

