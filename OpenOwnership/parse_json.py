# Standard bibliotek
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

                # Vi må konvertere viktige typer til "ekte" typer
                if "statementDate" in objekt:
                    try:
                        objekt["statementDate"] = datetime.strptime(objekt["statementDate"], "%Y-%m-%d")
                    except ValueError:
                        print(objekt)
                        raise
                #
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
                # Send det avgårde
                yield objekt
                data = renset[index:]
            except ValueError:
                # Trenger mer data; leser inn
                break
            #yrt
	#elihw
     #rof
#fed

from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687",
                              auth=("neo4j", "Velkommen"))

with open("100000.json", "r") as fd:
    typer = {"personStatement": 0,
             "entityStatement": 0,
             "ownershipOrControlStatement": 0}
    for objekt in json_parse(fd):
        typer[objekt["statementType"]] += 1
        # Vi lager noder med bare den viktige informasjonen
        print(f'StatementType: {objekt["statementType"]}')
        print(f'\tStatementID: {objekt["statementID"]}')        
        if objekt["statementType"] == "personStatement":        
            print(f'\tIdentifier: {objekt["identifiers"][0]["id"]}')
        elif objekt["statementType"] == "ownershipOrControlStatement":
            print(f'\tSubject: {objekt["subject"]["describedByEntityStatement"]}')
            print(f'\tPerson: {objekt["interestedParty"]["describedByPersonStatement"]}')
        elif objekt["statementType"] == "entityStatement":
            print(f'\tNavn: {objekt["name"]}')
        else:
            assert(0 == "Ukjent type")
        #fi
    #rof
    print(typer)
#

