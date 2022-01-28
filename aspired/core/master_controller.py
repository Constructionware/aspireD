# master_controller.py

# aspireDb master storage controller
# The Concept of a master in this usecase is a mutable directory that contains
# one index.json file that keeps a record of new and deleted directories from the 
# master directory 

#---------------------------- DEPENDENTS ----------------------------------------

import orjson as json
from datetime import datetime
from http import HTTPStatus as status
from time import sleep
from pathlib import Path
from genericpath import isfile
from os import  getlogin, mkdir, name, remove,listdir, rmdir
from os.path import abspath, join, isdir, expanduser
import shutil

#------------------------ LOCAL DEPENDENCIES -----------------------------------



# ----------------------------- UTILITIES ---------------------------------------


# Timestamp 
def timestamp():
        return  int((datetime.now().timestamp() * 1000))

# JSON Document writer
def writeJsonData(data, handle):
    try:
        data = json.dumps(data, indent = 4) # serialize data       
        with open(handle, "w") as outfile:
            outfile.write(data) # Save               
        outfile.close()
        del(handle) # cleanup
        del(outfile)
        del(data)
        return status.HTTP_201_CREATED
    except Exception as e:
        return e

def updateIndex(data, handle):  
    """Pushes data onto the repository index """ 
    try:        
        with open(handle, 'r') as infile: # open index file
            file = infile.read()
            index = json.loads(file)             
            index['index'].append(data)  # insert data into list 
        del(file)        
        sleep(0.1) # rest
        data = json.dumps(index, indent=4) # serialize data
        del(index)
        with open(handle, 'w') as outfile:
            outfile.write(data)
        outfile.close()
        del(outfile)
        del(data)
        del(handle)        
        return True
    except Exception as e:
        return e
    


# ------------------------------- ASPIRED MASTER CONTROLLER -------------------

class  Master:
    '''Main database controller responsible for creating and destroying slaves.
    creates or checks for a master directory 
    creates or checks for an index.json file in master directory
    '''
    def __init__(self) -> None:
        self.__create_master_repo
        self.__create_master_index

    @property
    def platform(self):
        try: 
            from platform import platform
            return platform().split('-')[0]
        except ImportError: return None
        finally: del(platform)


    def handle(self, args=None, **kwargs) -> str:
        '''Url endpoint resolution'''
        os_platform = self.platform
        if self.platform == "Windows":
            file_path = Path(f'C:/Users/{getlogin()}')
        elif self.platform == "Linux":
            file_path = expanduser("~")
        file_dir = join(file_path, '.aspiredb')
        if args and kwargs and 'index' in kwargs.keys():
            return join(file_dir, args, kwargs.get('index'))       
        if kwargs and 'doc' in kwargs.keys():
            return join(file_dir, kwargs.get('slave'), kwargs.get('doc'))
        if kwargs and 'slave' in kwargs.keys():
            return join(file_dir, kwargs.get('slave'))
        if args and 'doc' in kwargs.keys():            
            return join(file_dir, args, kwargs.get('doc'))
        if args:
            if 'index' in args or '.json' in args:
                return join(file_dir, 'index.json')
            return join(file_dir, args)        
        return file_dir
        
    # ------------------------------------- CREATE ----------------------------------------

    # setup database repository
    @property
    def __create_master_repo(self): 
        """ Creates a new master directory on the file system""" 
        if isdir(self.handle()):
            pass
        else:
            mkdir(self.handle())

    @property
    def __create_master_index(self):
        data={"index": [{ 
            "_id": timestamp(),
            "name": "aspiredb", 
            "role": "master", 
            "access": "public"}]            
        }          
        try:
            if isfile(self.handle('index')): # dont overwrite on server reload
                pass
            else:
                # a write once operation
                data = json.dumps(data, indent = 4) # serialize data       
                with open(self.handle('index'), "w") as outfile:
                    outfile.write(data)                
                outfile.close()
                #cleanup
                del(outfile)
                del(data)
                return 1
        except Exception as e:
            return e  

    def __create_slave_repo(self, dbname ) -> bool:
        """ Creates a new directory on the file system"""         
        if isdir(self.handle(dbname)):
            return False
        else:
            mkdir(self.handle(dbname))
            return True

    def __create_slave_index(self, args, **kwargs):
        data={"index": [{ 
            "_id": timestamp(),
            "name": args, 
            "role": "slave", 
            "access": kwargs.get("access")}]            
        }          
        try:
            handle = self.handle(args, index='index.json')
            if isfile(handle): # dont overwrite on server reload
                pass
            else:
                # a write once operation
                data = json.dumps(data, indent = 4) # serialize data       
                with open(handle, "w") as outfile:
                    outfile.write(data)                
                outfile.close()
                #cleanup
                del(outfile)
                del(data)
                return True
        except Exception as e:
            return e                
        finally:
            print(f'Slave Repository located at {handle}')  


    def create_slave(self, args, **kwargs):
        '''Creates a new Slave Repository Requires args = slave_name kwargs=access, 
        if private kwargs=password'''
        if self.__create_slave_repo(args):
            if "password" in kwargs.keys():
                self.__create_slave_index(args, access=kwargs.get('access'), password=kwargs.get('password'))
                # use password to encrypt the database repo
                return self.__update_master_index(args, access=kwargs.get("access"), password=kwargs.get('password'))
            else:
                self.__create_slave_index(args, access="public")
                return self.__update_master_index(args, access="public")
        return False
    # ---------------------------- UPDATE ----------------------------------------

    def __update_master_index(self, args, **kwargs):
        '''expecting args slave_name and in kwargs a key access with value set to  public or private default to public'''
        data={"_id": timestamp(),"name": args,"role": "slave" }
        #print(data)
        if "access" in kwargs.keys():
            data['access'] =  kwargs.get("access") 
            if data['access'] == 'private':
                data['password'] = kwargs.get('password')
        else: data['access'] = "public"
        try:
            #print(data)
            return updateIndex(data, self.handle('index'))            
        except Exception as e:
            return e
    
    def clone_slave(self, args, **kwargs):
        '''Clones an existing database . Requires a handle to the original and name for the clone
        generates a new id on the master index and is flagged as a clone of the original '''
        pass

    def destroy_slave(self, args, **kwargs):
        '''deletes a slave and its contents and remove it from the master index
        requires user password for public repositories and lock password for encrypted or private repositories ''' 
        password_hash = kwargs.get('password')
        if password_hash:
            # do validation
            handle = self.handle(args)
            try:
                if isdir(handle): 
                    if len(listdir(handle)) > 0:
                        shutil.rmtree(handle)
                    rmdir(handle)
                    # Flag index
                    return orjson.dumps(self.flag_index(args, flag='delete', password=password_hash))                    
                return {'status': 'slave not found'}   
            except OSError as e:
                return e
        return status.UNAUTHORIZED

    def flag_index(self, doc_id:str='aspiredb', flag:str=None, password:str=None):
        '''Updates the master index item with flag deleted or updated 
        Yeilds List States 
        Use:
        To get the index as a list call self.__flag_index(flag="list")
        To get the index as a dictionary call self.__flag_index(flag="index") 
        To get the entry for a particular slave on the index call self.__flag_index(doc_id="slave_name", flag="doc") Warning calling this api without a doc_id returns the Master index Tag 
        To get an entry flagged  as deleted call self.__flag_index(doc_id="slave_name", flag="delete", password="secret") throws a 403 Forbidden error if no doc_id is present or is assigned to the master 
        a 401 unautorised if entrant is private and password is incorrect or unavailable.
        To get an entry flagged  as updated call self.__flag_index(doc_id="slave_name", flag="update", password="secret") throws a 403 Forbidden error if no doc_id is present or is assigned to the master 
        and 401 unautorised if entrant is private and password is incorrect or unavailable.
        To get the location of an entry on the index call self.__flag_index(doc_id="slave_name", flag="locate")
        To get an updated index list with the updated entrant call self.__flag_index(doc_id="slave_name", flag="update-index",password="secret") password is required for private entry.'''        
        handle = self.handle('index')
        doc_id = doc_id
        flag = flag
        password = password

        def find_doc(doc):
            return doc['name'] == doc_id

        def delete(doc, password:str=None):
            if doc.get('access') == 'private':
                if doc.get('password') == password:
                    doc['deleted'] = True
                    return doc
                return status.UNAUTHORIZED
            if doc["role"] == "master":
                return {"error": status.FORBIDDEN}
            doc['deleted'] = True
            return doc

        def update(doc, password:str=None):
            if doc.get('access') == 'private':
                if doc.get('password') == password:
                    doc['updated'] = True
                    return doc
                return status.UNAUTHORIZED
            if doc["role"] == "master":
                return {"error": status.FORBIDDEN}
            doc['updated'] = True
            return doc

        def update_index(doc:dict, index:list=[], location:int=None, password:str=None):            
            if index and location:
                if type(doc) == dict:
                    if doc.get('access') == 'private':
                        if doc.get('password') == password:
                            index[location] = doc
                            return index                        
                    if doc["role"] == "master":
                        return status.FORBIDDEN
                    index[location] = doc
                    return index
                return status.UNAUTHORIZED
            return None
        
        def locate(doc, data_list:list=None):
            for item in data_list:
                if item['name'] == doc:
                    return data_list.index(item)

                            
        def index(handle):
            with open(handle, 'r') as outfile:
                json_data = json.load(outfile)
            del(outfile)
            return json_data


        def index_list(handle):
            with open(handle, 'r') as outfile:
                json_data = json.load(outfile)
            del(outfile)            
            return json_data['index']

        def filter_index(handle):
            with open(handle, 'r') as outfile:
                json_data = json.load(outfile)
            del(outfile)
            filtered = [{
                        "_id": item.get("_id"),
                        "name": item.get("name"),
                        "role": item.get("role"),
                        "access": item.get("access")
                    } for item in json_data['index'] if 'aspiredb' not in item['name']]                         
            return filtered


        def writer(index, handle):            
            data = json.dumps(index, indent=4) # serialize data            
            with open(handle, 'w') as outfile:
                outfile.write(data)
            outfile.close()
            del(outfile)
            del(data)
            del(handle)        
            del(index)        

        def process_or(flag):
            switcher = {
                'index': index(handle),
                'list': index_list(handle),               
                'doc': list(filter(find_doc, index_list(handle)))[0]                
            }  
            switcher['delete'] = delete(switcher.get('doc'), password=password) 
            switcher['locate'] = locate(doc_id, switcher.get('list')) 
            switcher['update'] = update(switcher.get('doc'), password=password)  
            switcher['update-index'] = update_index(switcher.get('update'), switcher.get('list'), switcher.get('locate')) 
            switcher['filter-index'] = filter_index(handle),

            return switcher.get(flag, None)
        return process_or(flag)
 
    
    class Signal:
        def __init__(self) -> None:
            #super(Master(), self)
            ''' '''
       
        def send( message:dict=None):
            #print(f'Signal {message} sent. Time: {timestamp()}')
            return {"message": message, "time": timestamp()}

        def recieve(payload:dict=None):
            #print(f'Recieved {payload} at Time: {timestamp()}')
            def intransit(time:int):
                duration = (timestamp() - time) / 1000 # seconds
                if duration < 60:
                    return f"{duration} - seconds"
                if duration > 60 and duration < 60 * 60:
                    return f"{duration / 60} - minutes"
                if duration > 60 * 60 and duration < (60 * 60) * 24:
                    return f"{duration / (60 * 60)} - hours"
                if duration > (60 * 60) * 24:
                    return f"{duration /((60 * 60) * 24)} - days"

            return {
                "payload": payload, 
                "time": timestamp(), 
                "intransit": intransit(payload.get('time'))
            }

        
    
    def __repr__(self) -> str:
        return f"aspireDb Master Controller controlling Master Repository located at {self.handle()}"

if __name__ == "__main__":
    master = Master()

      
