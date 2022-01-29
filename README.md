# aspireD
Aspire Database is a lightweight JSON Database written in Python that runs in your program and on the Network.

## Installation
pip install aspired

from aspiredb.server import serve
serve()

visit http://localhost:22090
 
 # The Api

 To create a database called games
 GET /create/games

 Creates a Document on the games database 

 doc = { "_id": "aa01", "name": "War Craft", "player":7, "score": 89}

 POST /document/games
 payload = doc

Retreive a Document from the games database 

GET /games/aa01
{ "_id": "aa01", "name": "War Craft", "player":7, "score": 89}

Update a document on the games database

update = { "_id": "aa01",  "score": 100}

PUT /games/aa01
payload=update

Delete a Document

DETETE /games/aa01

# Use In Programs

import the Database Controller into your program 


    from aspiredb.database import Controller

upon initializing the controller a hidden directory is created in the user Home directory called .aspiredb 
in which all databases and records are stored.

    con = Controller()

you can provide an alternate storage directory name upon initilization.

    con = Controller('storagename')

This will create a hidden directory called .storagename on the user Home directory.

Creating a database is quite simple,  

    con.create_database('games')

Creates a database called games to store a JSON data object.




con.create_document('games', doc_id="aa01", data=doc)

con.get_document('games', doc_id="aa01")

con.get_documents('games')

con.update_document('games', doc_id="aa01", data=payload)

con.delete_document('games', doc_id="aa01")










