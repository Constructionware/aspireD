import asyncio
import orjson as json

from os import name
from socket import gethostname, gethostbyname
from flask import request
from flask_restful import Resource

from aspired.database import Controller

port = 9092

con = Controller()


# Introduction
class Introduction(Resource):
    ''' '''
    def get(self):
        '''Introduction  Welcome to aspireDb'''
        return {"text": f"aspireDB   Available on host {gethostname()} On The Local Network at {gethostbyname(gethostname())}:{port} ... Enjoy!"}

#.................................. DATABASE ................................

#Create Database
class Database(Resource):
    '''Manages the Creation, Retreival and destruction of databases. '''

    # Create a New Database
    def post(self):
        '''Creats a new Public Database with name dbname by default.
        and a Private database if kew access:'private' key password is present.
        Expects either a Form Object with values for data and password for 
        private databases, and value for data if the database is public,
        Or a JSON object with key value 
        {"data": "name of database", "password": "secret" } for private databases
        {"data": "name of database"} for public databases. '''

        try:
            # Attempt to create database from JSON data
            result = request.get_json(['force', 'silent', 'cache'])
            data = result.get('data')
            access = result.get('access')

            if result.get('password'): 
                # create private database
                db = con.create_database(
                    dbname=data, 
                    access=access, 
                    password=result.get('password')
                ) 
            else: 
                # create public database
                db = con.create_database(dbname=data, access=access)

        except:
            # Attempt to create database from Form data
            data = request.form.get('data')
            access = request.form.get('accesss')

            if request.form.get('password'): 
                # create private database
                db = con.create_database(
                    dbname=data, 
                    access=access, 
                    password=request.form.get('password')
                ) 
                
            else: 
                # create public database
                db = con.create_database(dbname=data, access=access)

        if type(db) == bytes:
            result = json.loads(db)
        else: result = db

        return (result)


    #Get Database Health Report
    def get(self, dbname):
        '''Retreive The Database status report'''
        
        text= f"Sorry we cannot process requests for {dbname} at this time!...Please try again in a few hours."
        return {"status": text}


    def get(self):
        '''Retreive All Databases '''
        return json.loads( con.get_databases() )


    def delete(self, dbname, password):
        '''Deletes a database and its contents'''
        if password: return con.delete_database(dbname=dbname, password=password)
        else: return con.delete_database(dbname=dbname)

#.................................. DOCUMENTS ................................


class PublicDocument(Resource):
    ''' Handles CRUD operations on Databases '''
    
    #Create Document
    def post(self, dbname):
        '''Creats a new Public Database with name dbname by default.
        and a Private database if kew access: 'private' key password is present.
        '''        
        data = request.get_json(['force', 'silent'])
        result = con.create_document(database=dbname, data=data)
        if type(result) == bytes:
            result = json.loads(result)
            return result
        return result

    #Retreive one or more document or all documents 
    def get(self, dbname, doc_id):
        '''Retreive a document form The Database.
        Requires a hypenated string with database name and document id
        eg: uri = "foods-yam223" '''
            
        result = json.loads( con.get_document(dbname=dbname, doc_id=doc_id))        
        return result


    #Retreive all documents 
    def get(self, dbname):
        '''Retreive a document form The Database.
        Requires a hypenated string with database name and document id
        eg: uri = "foods-yam223" '''
        result = json.loads(con.get_documents(dbname=dbname))
        return result


    #Update Document    
    def put(self, dbname, doc_id):
        '''Updates a document with data provided.'''
        
        data = request.get_json(['force', 'silent'])    
        result = con.update_document(dbname=dbname, doc_id=doc_id, data=data)
        if type(result) == bytes:
            result = json.loads(result)
            return result
        return result
    
    
    #Delete a Document    
    def delete(self, dbname, doc_id):
        '''Deletes a document from the database
        Requires a hypenated string with database name and document id
        eg: uri = "foods-yam223" '''
        
        result = con.delete_document(dbname=dbname, doc_id=doc_id)
        if type(result) == bytes:
            result = json.loads(result)
            return result
        return result

    # Clone an Existing Document 
    def options(self, dbname, doc_id, clone_id):
        
        result = json.loads( con.clone_doc(dbname=dbname, doc_id=doc_id, clone_id=clone_id))
        return result
 

class PrivateDocument(Resource):
    '''Handles CRUD on Private Documents'''

    #Create a Private Document   
    def post(self, dbname):
        '''Creats a new Public Database with name dbname by default.
        and a Private database if kew access: 'private' key password is present.
        '''     
       
        data = request.get_json(['force', 'silent'])
        password = data.get('password')
        result = con.create_document(dbname=dbname, data=data.get('data'), password=password)
        
        if type(result) == bytes: return json.loads(result)
        else: return result


