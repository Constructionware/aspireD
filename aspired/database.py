#database.py

#---------------------- SYSTEM DEPENDENTS -------------------------------
import orjson as json
from datetime import datetime

#---------------------- LOCALS ------------------------------------------
from aspired.core.master_controller import Master, writeJsonData, updateIndex
from aspired.core.slave_controller import Slave, ugen


#---------------------- SETUP -------------------------------------------

class Setup:
    '''Setup'''

    @property
    def master(self):
        return Master()

    @property
    def slave(self):
        return Slave()  

#--------------------- Document -----------------------------------------

class Document( Setup ):
    __doc:dict = {
        "_id": None,
        "_rev": None,
        "title":None,
        "created": datetime.now()
    }

    @property
    def doc(self):
        '''Returns the document as a binary string.'''
        return json.dumps(self.__doc)

    @property
    def getdoc(self):
        '''Returns the document as a native python dictionary.'''
        return json.loads(self.doc)

    @property
    def cleardoc(self):
        ''' Clears all elements from the Document '''
        self.__doc.clear()
        return self.__doc

    @property
    def resetdoc(self):
        '''Clears all input values from the document. default fields remains.'''
        self.__doc = {
            "_id": None,
            "_rev": None,
            "title":None,
            "created": datetime.now()
        }
        return self.__doc    

    def setdoc(self, data:dict=None):
        '''Updates the Document with new data.'''
        if data: self.__doc = self.__doc | data
        return json.dumps(self.__doc)

    class DesignDocument:
        ''' '''
        design_view:dict = {
            "_id": "_design/index",
            "_view": "all",
            "function": "alldocs()"
        }

        @property
        def alldocs(self):
            pass

    def __repr__(self) -> str:
        props = list(filter(lambda x: "__" not in x,  self.__dir__()))
        return f"aspireDB Document class. Exposing fields: {props}"


#---------------------- CREATE ------------------------------------------

class Create( Setup ):
    def __init__(self):
        """Create Handles Creation of Slave Databases and Documents"""
           

    # creates a new database    
    def create_database(self, dbname:str=None, access:str="public", password:str=None):
        '''POST'''
        if dbname:
            result = self.master.create_slave(dbname, access=access, password=password)
            if type(result) == bool:
                if result:
                    return json.dumps({"status": "Success"})
                return json.dumps({"status": "That Database Already Exist."})
            return json.dumps({"status": str(result)})
        return json.dumps({"You did not provide a database name."})

   

        
    # Creates a new public Document on an existing Database
    def create_document(self, database:str=None, data:dict=None):
        '''POST'''
        if data:
            result = self.slave.create_doc(database, data=data)
            return json.dumps({"status": f"New public Document with Id: {result} Created on Database: {database}"})
        return json.dumps({"status": "Failed!  No Data Provided."})

    # Creates a new Document on an existing private Database
    def create_private_document(self, database:str=None, data:dict=None, password:str=None):
        '''POST'''
        if data:
            result = self.slave.create_doc(database, data=data, password=password)
            return json.dumps({"status": f"New privte Document with Id: {result} Created on Database: {database}"})
        return json.dumps({"status": "Failed!  No Data Provided."})


#---------------------- CLONE / COPY ------------------------------------

class Clone( Setup ):
    def __init__(self) -> None:
        super().__init__()
        """Creates a Clone of an existing document """

    def clone_doc(self, dbname:str=None, doc_id:str=None, clone_id:str=None):
        """GET"""
        result = self.slave.clone_doc(dbname=dbname, doc_id=doc_id, clone_id=clone_id)
        return json.dumps(result)
        


#---------------------- READ --------------------------------------------

class Read( Setup ):
    def __init__(self):
        """Read Retrieve single and Bulk documents from Respective database"""

    def get_database(self, dbname:str=None, password:str=None):
        '''GET'''
        pass

    def get_databases(self):
        '''GET'''        
        return json.dumps(self.master.flag_index(flag='filter-index')[0])


    def get_document(self, dbname:str=None, doc_id:str=None, password:str=None):
        '''GET'''
        if dbname and doc_id:
            if '.json' in doc_id:
                return json.dumps( self.slave.get_document(slave=dbname, doc=doc_id, password=password))
            doc_id = f"{doc_id}.json"
            return json.dumps( self.slave.get_document(slave=dbname, doc=doc_id, password=password))
        return json.dumps({"status": "A databas name and document id to retreive is required."})


    def get_documents(self, dbname:str=None):
            '''GET'''
            if dbname:            
                return json.dumps( self.slave.get_documents(slave=dbname))
            
            return json.dumps({"status": "A database name is required."})

#---------------------- UPDATE - ----------------------------------------

class Update( Setup ):
    def __init__(self):
        """Update Updates Documents and the document index
        Updated docks are flagged with a revision id and a Tommb stone of 
        the revision kept. maximum revisions 100"""

    def update_database(self, dbname:str=None, data:dict=None):
        '''PUT'''
        pass

    def update_document(self, dbname:str=None, doc_id:str=None, data:dict=None):
        '''PUT'''
        if dbname and doc_id and data:
            result = self.slave.update_doc(dbname=dbname, doc_id=doc_id, data=data)
            return json.dumps(result)
        else:
            json.dumps({"status": "Faild! Insufficient Details."})

#---------------------- DELETE ------------------------------------------

class Delete( Setup ):
    def __init__(self):
        """Delete Destroys Documents and Slaves removes entrants from 
        slave and master indexes. Deleted data is kept in dump for 30 days"""

    def delete_database(self, dbname:str=None, password:str=None):
        '''DELETE a Database'''
        try:
            if dbname and password:
                return json.dumps( self.master.destroy_slave(dbname, password=password)) 
            return json.dumps({"status": "Database Name is Required to do this operation"})
        except Exception as e:
            return json.dumps({"status": "Database was Deleted."})        

    def delete_document(self, dbname,  doc_id:str=None, password:str=None):
        '''DELETE a document from required database '''
        try:
            if dbname:
                return json.dumps( self.slave. delete_doc(dbname=dbname, doc_id=doc_id)) 
            else: return json.dumps({"status": "Database Name is Required to do this operation"})
        except Exception as e:
            return json.dumps({"status": "That Document was already Deleted."})    


#---------------------- ROLL BACK ---------------------------------------

class Rollback( Setup ):
    def __init__(self):
        """Rollback Rolls back Updates and deletions """

    def rollback_delete_database(self, dbname:str=None):
        '''DELETE'''
        pass

    def rollback_delete_document(self, doc_id:str=None):
        '''DELETE'''
        pass

    def rollback_update_database(self, dbname:str=None):
        '''DELETE'''
        pass

    def rollback_update_document(self, doc_id:str=None):
        '''DELETE'''
        pass

#----------------------CRUD-R CONTROLLER --------------------------------

class Controller(Clone, Create, Read, Update, Delete, Rollback ):
    def __init__(self):
        super(Controller).__init__()
        self.id = self.generateid.gen_id('app')

    @property
    def generateid(self):
        return ugen

    def __repr__(self) -> str:
        props = list(filter(lambda x: "__" not in x,  self.__dir__()))
        return f"\taspireDB Main Controller. \n\tRuntime ID: {self.id}\n\tExposed Fields: {props}"
    







