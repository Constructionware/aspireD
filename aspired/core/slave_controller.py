# slave_controller.py

# aspireDb slave storage controller


#---------------------------- DEPENDENTS ----------------------------------------
import json
from datetime import datetime
from http import HTTPStatus as status

from time import sleep

from genericpath import isfile
from os import  getlogin, mkdir, name, remove, listdir
from os.path import abspath, join, isdir


#------------------------ LOCAL DEPENDENCIES -----------------------------------
from aspired.core.master_controller import timestamp, writeJsonData, updateIndex, Master  
from aspired.core.encriptor import EncryptFile, EncryptMessage, GenerateId

# ----------------------------- UTILITIES ---------------------------------------

# Unique ID Generator
ugen = GenerateId()

# Timestamp 
def timestamp():
        return  int((datetime.now().timestamp() * 1000))


# ------------------------------- ASPIREDB SLAVE CONTROLLER -------------------

class  Slave:
    '''Slave controller responsible for creating, reading, updating, and destroying documents.
    updates the slave index
    '''
    def __init__(self) -> None:
        self.__set_handle()        

    def __set_handle(self):
        '''Url endpoint resolution'''
        master = Master()
        self.handle = master.handle

    @property
    def time_stamp(self):
        return timestamp()
        
    # ------------------------------------- CREATE ----------------------------------------

    def create_doc(self, args, **kwargs):
        '''Creates a new Document in theSlave Repository Requires args = slave_name and a dictionary 
        repesenting the document. in kwargs=data  must have key _id , if repository is  private kwargs=password'''        
        if "password" in kwargs.keys():
            # use password to encrypt the database repo
            return self.__create_document(args, data=kwargs.get('data'), password=kwargs.get('password'))           
        else:  
            return self.__create_document(args, data=kwargs.get('data'))             

    def __create_document(self, args, **kwargs):
        data = kwargs.get('data')       
        try:
            if data.get('_id') == None:
                    data['_id'] = ugen.gen_id('doc')     
            handle = self.handle(slave=args, doc=f"{data['_id']}.json")
            if isfile(handle): # dont overwrite on server reload
                return 0
            else:
                # a write once operation
                payload = json.dumps(data, indent = 4) # serialize data       
                with open(handle, "w") as outfile:
                    outfile.write(payload)                
                outfile.close()
                #cleanup
                del(outfile)
                del(payload)
                return data['_id']
        except Exception as e:
            return e                
        finally:
            stub = {
                "_id": self.time_stamp,
                "name": data.get('_id'),
                "role": "data",
                "access": "public"
            }
            self.__update_slave_index(args, data=stub)           
            del(data) # clean up               
           

    # setup database repository

    #--------------------------- READ --------------------------------------
       
    def get_document(self, args=None, **kwargs): 
        """ Retreives a document from a database accepts slave_name as args
        and doc.json in kwargs"""        
        
        handle = self.handle(slave=kwargs.get('slave'), doc=kwargs.get('doc') )        
        try:
            if isfile(handle):                           
                # Reading a .json            
                with open(handle, "r") as file:
                    json_object = json.load(file)          
                del(file)
                # update slave index flag_document
                del(handle)
                return json_object
            return {'status': 'file not found'}                      
        except Exception as e: 
            return {"error":str(e)}
        

    def get_documents(self, args=None, **kwargs): 
        """ Retreives all documents from a database accepts slave_name in kwargs"""        
        
        handle = self.handle(slave=kwargs.get('slave') )             
        try:
            if isdir(handle):                           
                
                data = list(filter(lambda x: "index" not in x, listdir(handle)))
                data = [self.get_document(slave=kwargs.get('slave'), doc=item) for item in data]
                del(handle)
                return data
            return {'status': 'file not found'}                      
        except Exception as e: 
            return {"error":str(e)}
        finally: 
            del(data)  


    # ---------------------------- UPDATE ----------------------------------------
    
    def update_doc(self, args=None, **kwargs):
        '''expecting args slave_name and a dictionary with update data'''
        dbname=kwargs.get('dbname')
        doc=kwargs.get("doc_id")
        data=kwargs.get('data')
        
        result = self.__update_document(dbname=dbname, doc=doc, data=data)
        return  result 

    def __update_document(self, **kwargs):
        ''' Expects in kwargs the database where the document is stored  
        dbname=dbname,  a handle to the file containing the data doc=doc_id, and
        the data data=data '''   

        try:
            dbname = kwargs.get('dbname')           
            doc_id = kwargs.get('doc')
            if ".json" in doc_id:             
                pass                
            else:
                doc_id = f"{doc_id}.json"
            handle = self.handle(slave=dbname, doc=doc_id)            
            if isfile(handle): #open file
                data = kwargs.get('data')                
                original = self.get_document(slave=dbname, doc=doc_id) 
                updated = original | data                             
                with open(handle, "w") as outfile:
                    outfile.write(json.dumps(updated))                
                outfile.close()   
                del(dbname)
                del(outfile)
                del(data)  
                del(original) # cleanup           
                return updated
        except Exception as e:
            return e                
        finally:
            print(f'Done updating Document {doc_id}') 
            

    # Flagged not to be exposed
    def __update_slave_index(self, args, **kwargs):
        '''expecting args slave_name and in kwargs a key access with value set to  public or private default to public'''             
        try:
            data=kwargs.get('data') 
            
            handle = self.handle(args, index='index.json')
            with open(handle, 'r') as infile: # open index file
                file = infile.read()
            index = json.loads(file)             
            index['index'].append(data)  # insert data into list 
            del(data)
            del(file) 
            del(infile)
            sleep(0.1) # rest
            updated = json.dumps(index, indent=4) # serialize data            
            with open(handle, 'w') as outfile:
                outfile.write(updated)
            outfile.close()  
            del(index)
            del(updated)
            del(outfile)
            del(handle)
            return 1       
        except Exception as e:
            return e            

    #-------------------------------- CLONE / COPY --------------------------------------------------------------

    def clone_doc(self, **kwargs):
        '''Clones an existing database . Requires a handle to the original and name for the clone
        generates a new id on the master index and is flagged as a clone of the original '''
        dbname = kwargs.get('dbname')
        doc_id = kwargs.get("doc_id")
        clone_id = kwargs.get("clone_id")
        result = self.__clone_document(dbname=dbname, doc_id=doc_id, clone_id=clone_id)
        return result

    def __clone_document(self, dbname:str=None, doc_id:str=None, clone_id:str=None):
        if '.json' in doc_id:
            origin = f"{doc_id[:-len('.json')]}-{clone_id}"
        else: 
            origin = f"{doc_id}-{clone_id}"
            doc_id = f"{doc_id}.json"
        handle = self.handle(slave=dbname, doc=doc_id)
        print(handle)
        base_doc = self.get_document(slave=dbname, doc=doc_id)
        clone = base_doc.copy()
        clone["_id"] = clone_id
        clone['meta_data'] = {
            "cloned": {
                "origin": origin,
                "date": self.time_stamp
            }
        }
        status = self.__create_document(dbname, data=clone)
        
        return clone

    #----------------------------------- DELETE -----------------------------------------------------------------    
    def __delete_slave_index_entry(self, **kwargs):
        '''expecting kwargs a key access with value set to  
        public or private default to public dbname:str=None, doc_id:str=None,'''  

        try:
            dbname=kwargs.get('dbname') 
            doc_id=kwargs.get('doc_id')
            if '.json' in doc_id: doc_id = doc_id.split('.')[0] 
            else: pass
            
            handle = self.handle(dbname, index='index.json')
            with open(handle, 'r') as infile: # open index file
                file = infile.read()
            index = json.loads(file) 
            infile.close()

            def findEntry(item):
                if doc_id not in item.get('name'):
                    return item

            new_index = list(filter(findEntry, index['index']))           
            
            
            sleep(0.1) # rest
                    
            with open(handle, 'w') as outfile:
                outfile.write(json.dumps(new_index, indent=4))
            outfile.close()            
            
            return {"status": f"document {doc_id} was deleted"}       
        except Exception as e:
            return {"error": str(e)}  
        finally:
            del(file) 
            del(infile)
            del(new_index) 
            del(index)          
            del(outfile)
            del(handle)


    async def delete_doc(self, args=None, **kwargs):
        '''deletes a document permanently from the system but keeps a reference in log, deleted documents are placed in a dump directory 
        and kept for 30days before final deletion 
        requires user password for public repositories and lock password for encrypted or private repositories 
        slave = slave doc=doc.json password=password_hash
        Expects in kwargs the database where the document is stored  
        dbname=dbname,  and handle to the file to be deleted'''
        #password_hash = kwargs.get('password')

        try:
            dbname = kwargs.get('dbname')           
            doc_id = kwargs.get('doc_id')
            if ".json" in doc_id:             
                pass                
            else:
                doc_id = f"{doc_id}.json"
            handle = self.handle(slave=dbname, doc=doc_id)            
            if isfile(handle): #open file
                remove(handle)                    
                # Flag index
                return self.__delete_slave_index_entry(dbname=dbname, doc_id=doc_id)
            else: return {'status': 'file not found'}   
        except OSError as e:
            return e
        
    
    def __repr__(self) -> str:
        return f"aspireDb Slave Controller"

if __name__ == "__main__":
    slave = Slave()

      
