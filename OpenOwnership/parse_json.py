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

                #
                # Vi må konvertere viktige typer til "ekte" typer
                # De ser ut til å være 64 bit (og 63 er trolig max)
                #if "statementDate" in objekt:
                #    try:
                #        objekt["statementDate"] = datetime.strptime(objekt["statementDate"], "%Y-%m-%d")
                #    except ValueError:
                #        print(objekt)
                #        raise
                #
                #if "statementID" in objekt:
                #    objekt["statementID"] = int(objekt["statementID"])
	            #
                #if "interestedParty" in objekt:
                #    if "describedByPersonStatement" in objekt["interestedParty"]:
                #        objekt["interestedParty"]["describedByPersonStatement"] = \
                #            int(objekt["interestedParty"]["describedByPersonStatement"])
                #    #
                #
                #if "identifiers" in objekt:
                #    # Er en liste (sukk og dobbeltsukk)
                #    if "id" in objekt["identifiers"][0]:
                #        ids = objekt["identifiers"]
                #        objekt["identifiers"][0]["id"] = \
                #            int(objekt["identifiers"][0]["id"])
                #    #
	            #
                #if "subject" in objekt:
                #    if "describedByEntityStatement" in objekt["subject"]:
                #        objekt["subject"]["describedByEntityStatement"] = \
                #            int(objekt["subject"]["describedByEntityStatement"])
                #    #fi
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

# Databasen
from neo4j import GraphDatabase
driver = GraphDatabase.driver("neo4j://localhost", auth=("neo4j", "Velkommen"))
driver.verify_connectivity()
print(driver)

# Å opprette en index er idempotent
cypher = "CREATE INDEX index_person IF NOT EXISTS for (p:Person) on (p.ident)"
summary = driver.execute_query(cypher)
cypher="CREATE INDEX index_statement IF NOT EXISTS for (p:Statement) on (p.ident)"
summary = driver.execute_query(cypher)
cypher="CREATE INDEX index_firma IF NOT EXISTS for (p:Firma) on (p.ident)"
summary = driver.execute_query(cypher)
cypher="CREATE INDEX index_tilperson IF NOT EXISTS FOR ()-[r:TILPERSON]-() ON (r.ident)"
summary = driver.execute_query(cypher)
cypher="CREATE INDEX index_tilfirma IF NOT EXISTS FOR ()-[r:TILFIRMA]-() ON (r.ident)"
summary = driver.execute_query(cypher)

typer = {"personStatement": 0,
         "entityStatement": 0,
        "ownershipOrControlStatement": 0}

# For stdin
import sys

with open("logfile", "w") as log_fd:
    teller = 0
    start = datetime.now()
    for objekt in json_parse(sys.stdin):
        teller += 1
        if teller % 1000 == 0:
            print(f"{teller} {datetime.now() - start}")
            log_fd.write(f"{teller} {datetime.now() - start}\n")
            start = datetime.now()
            
        typer[objekt["statementType"]] += 1
        # Vi lager noder med bare den viktige informasjonen
        #print(f'StatementType: {objekt["statementType"]}')
        #print(f'\tStatementID: {objekt["statementID"]}')
        if objekt["statementType"] == "personStatement":
            # Legg til personen om den ikke allerede finnes
            #print(f'\tIdentifier: {objekt["identifiers"][0]["id"]}')
            cypher = f'MERGE (p:Person {{ident: \"{objekt["statementID"]}\" }})'
            #print(cypher)
            summary = driver.execute_query(cypher).summary
            #print(f"Created {summary.counters.nodes_created} nodes in {summary.result_available_after} ms.")
            
        elif objekt["statementType"] == "ownershipOrControlStatement":
            #print(f'\tSubject: {objekt["subject"]["describedByEntityStatement"]}')
            #print(f'\tPerson: {objekt["interestedParty"]["describedByPersonStatement"]}')
            cypher = f'CREATE (s:Statement {{ ident: \"{objekt["statementID"]}\" }}) \
                    MERGE (p:Person {{ ident: \"{objekt["interestedParty"]["describedByPersonStatement"]}\" }}) \
                    MERGE (f:Firma {{ ident: \"{objekt["subject"]["describedByEntityStatement"]}\" }}) \
                    CREATE (s) - [:TILPERSON {{ ident:  \"{objekt["statementID"]}\" }} ] -> (p) \
                    CREATE (s) - [:TILFIRMA {{ ident: \"{objekt["statementID"]}\" }}] -> (f)'
            #print(cypher)
            summary = driver.execute_query(cypher).summary
            #print(f"Created {summary.counters.nodes_created} nodes in {summary.result_available_after} ms.")
        elif objekt["statementType"] == "entityStatement":
            # Fjerne ulovlige tegn
            if '"' in objekt["name"]:
                objekt["name"] = objekt["name"].replace('"', ' ')
            #            
            #print(f'\tNavn: {objekt["name"]}')
            cypher = f'MERGE (f:Firma {{ ident: \"{objekt["statementID"]}\", name: \"{objekt["name"]}\" }})'
            #print(cypher)
            summary = driver.execute_query(cypher).summary
            #print(f"Created {summary.counters.nodes_created} nodes in {summary.result_available_after} ms.")
        else:
            assert(0 == "Ukjent type")
        #fi
    print(typer)
#
