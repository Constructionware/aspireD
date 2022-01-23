# core/encriptor.py

#----------------------------- Data Security Service ----------------------------------
from base64 import b64decode, b64encode
from cryptography.fernet import Fernet as fn
import time 
import sys


class Key:
    key_holster: str = None


    def __init__(self):
        self.load_key()

    
    @property
    def get_key(self): 
        return self.key_holster.encode()


    def load_key(self):
        ''' '''
        import subprocess
        import uuid
        current_machine_id = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()
        self.key_holster = str(uuid.UUID(int=uuid.getnode())).split('-')[-1] + current_machine_id

    
    @property
    def generate_hash_key(self):
        key = fn.generate_key()                       
        return key

        
    @property
    def generate_password_hash_key(self):
        self.load_key()
        from base64 import urlsafe_b64encode        
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.hashes import SHA256
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC  

        password = self.get_key # Convert to type bytes
        salt = b'salt_' # CHANGE THIS - recommend using a key from os.urandom(16), must be of type bytes
        kdf = PBKDF2HMAC(
            algorithm=SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = urlsafe_b64encode(kdf.derive(password)) # Can only use kdf once
        return key    

 


class EncryptMessage( Key ):

    ciphers:list = []    
    key_file_name:str = 'enc_key.key'

    def __init__(self):
        self.load_key()

    def encrypt_message(self, message): 
        ''' For backend storage and for encrypting messages on this machine only'''  
          
        key = self.generate_password_hash_key
        f = fn(key)
        time.sleep(0.005)
        ds = message.encode('utf-8')  # Convert to bytes
        encrypted = f.encrypt(ds)        
        sys.stdout.write(encrypted.decode('utf-8'))
        return encrypted.decode('utf-8')


    def decrypt_message(self, encrypted_message):
        ''' For decrypting messages that was encrypted on this machine only'''            
        key = self.generate_password_hash_key
        time.sleep(0.005)
        f = fn(key)
        if type(encrypted_message) == str:
            decrypted = f.decrypt(encrypted_message.encode('utf-8'))
        else: decrypted = f.decrypt(encrypted_message)
        
        sys.stdout.write(decrypted.decode())
        return decrypted.decode('utf-8')


    def encrypt_net_message(self, message): 
        ''' For backend storage and for encrypting messages on this machine only'''       
        key = self.generate_hash_key
        time.sleep(0.005)
        f = fn(key)
        if type(message) == str:
            encrypted = f.encrypt(message.encode('utf-8'))
        else: encrypted = f.encrypt(message)
        time.sleep(0.005)         
        payload = key.decode('utf-8') + "/" + encrypted.decode('utf-8')       
        return payload


    def decrypt_net_message(self, encrypted_message):
        ''' For decrypting messages that was encrypted on this machine only'''
        data =  encrypted_message.split('/')           
        key = data[0].encode('utf-8')
        f = fn(key)
        time.sleep(0.005)
        decrypted = f.decrypt(data[1].encode('utf-8'))      
        return decrypted.decode('utf-8')



class EncryptFile (Key):

    def encrypt_file(self, input_file, outfile_name:str = None):

        key = self.generate_password_hash_key # Use one of the methods to get a key (it must be the same when decrypting)
        input_file = input_file
        output_file = outfile_name

        with open(input_file, 'rb') as f:
            data = f.read()

        fernet = fn(key)
        encrypted = fernet.encrypt(data)

        with open(output_file, 'wb') as f:
            f.write(encrypted)

        # You can delete input_file if you want
        del(input_file)

    def decrypt_file(self, input_file, outfile_name:str = None):
        
        key = self.generate_password_hash_key # Use one of the methods to get a key (it must be the same as used in encrypting)
        input_file = input_file
        output_file = outfile_name

        with open(input_file, 'rb') as f:
            data = f.read()

        fernet = fn(key)
        decrypted = fernet.decrypt(data)

        with open(output_file, 'wb') as f:
            f.write(decrypted)


class Encoder:
    ''' '''

    def encode_pdf(self, file_handle):
            try:
                from base64 import b64encode
                with open(file_handle, "rb") as pdf_file:
                    encoded_string = b64encode(pdf_file.read())
                return encoded_string
            except ImportError:
                try:
                    import base64
                    with open("book.pdf", "rb") as pdf_file:
                        encoded_string = base64.b64encode(pdf_file.read())
                    return encoded_string
                except:
                    return None

#----------------------------- ID Generation Service ----------------------------------

from strgen import StringGenerator

class GenerateId:
    tags = dict(
            doc='[h-z5-9]{8:16}',
            app='[a-z0-9]{16:32}',
            key='[a-z0-9]{32:32}',
            job='[a-j0-7]{8:8}',
            user='[0-9]{4:6}',
            item='[a-n1-9]{8:8}',
            code='[a-x2-8]{24:32}'
        )
 
    def gen_id(self, doc_tag:str=None):
        """ 
            Doc Tags: String( doc, app, key, job, user, item, code,task,name)
            UseCase: 
                        >>> import genny
                        >>> from genny import gen_id
                        >>> from genny import gen_id as gi
                        
                        >>> id = genny.gen_id('user')
                        >>> id = gen_id('user')
                        >>> id = gi('user')
                Yeilds ... U474390
                        ... U77301642
                        ... U1593055
        
        """
        
        if doc_tag == 'user':
            #u_id = StringGenerator(str(self.tags[doc_tag])).render(unique=True)
            return f"U{StringGenerator(str(self.tags[doc_tag])).render(unique=True)}"
        return StringGenerator(str(self.tags[doc_tag])).render(unique=True)
            

    def name_id(self, fn:str='Jane',ln:str='Dear',sec:int=5):
        """ 
            Name Identification by initials fn='Jane', ln='Dear' and given number sequence sec=5.
            
            UseCase: 
                        >>> import genny
                        >>> from genny import name_id
                        >>> from genny import name_id as nid
                        
                        >>> id = genny.name_id('Peter','Built',6)
                        >>> id = name_id('Peter','Built',5)
                        >>> id = nid('Peter','Built',4)
                        >>> id = nid() # default false id 
                        
                Yeilds ... PB474390
                        ... PB77301
                        ... PB1593
                        ... JD1951
        
        """
        code = '[0-9]{4:%s}'% int(sec)
        return f"{fn[0].capitalize()}{ln[0].capitalize()}{StringGenerator(str(code)).render(unique=True)}"
               

    def short_name_id(self, fn:str='Jane',ln:str='Dear',sec:int=2):
        """ 
            Name Identification by initials fn='Jane', ln='Dear' and given number sequence sec=5.
            
            UseCase: 
                        >>> import genny
                        >>> from genny import short_name_id
                        >>> from genny import short_nameid as id
                        
                        >>> id = genny.short_name_id('Peter','Built',2)
                        >>> id = short_nameid('Peter','Built')
                        >>> id = id(p','b',3)
                        >>> id = id() # default false id 
                        
                Yeilds ... PB47
                        ... PB54
                        ... PB69
                        ... JD19
        
        """
        code = '[0-9]{2:%s}'% int(sec)
        return f"{fn[0].capitalize()}{ln[0].capitalize()}{StringGenerator(str(code)).render(unique=True)}"
        

    def event_id(self, event,event_code,sec=8):
        """EventId 
            Event Identification by initials fn='Jane', ln='Dear' and given number sequence sec=5.
            
            UseCase: 
                        >>> import genny
                        >>> from genny import event_id
                        >>> from genny import event_id as id
                        
                        >>> id = genny.event_id('Product','LAUNCH',6)
                        >>> id = event_id('Product','LAUNCH',5)
                        >>> id = id('Product', 'LAUNCH',4)                       
                Yeilds ... PROLAUNCH-884730
                        ... PROLAUNCH-18973
                        ... PROLAUNCH-4631                       
        
        """
        code = '[0-9]{4:%s}'% int(sec)
        return f"{event[:3].upper()}{event_code}-{StringGenerator(str(code)).render(unique=True)}"
        

    def short_event_id(self, event,event_code,sec=2):
        """ShortEventId 
            Event Identification by initials fn='Jane', ln='Dear' and given number sequence sec=2.
            
            UseCase: 
                        >>> import genny
                        >>> from genny import short_event_id
                        >>> from genny import short_event_id as id
                        
                        >>> id = genny.short_event_id('Product','LAUNCH',2)
                        >>> id = short_event_id('Product','LAUNCH')
                        >>> id = id('Product', 'LAUNCH',3)
                Yeilds ... PROLAUNCH-88
                        ... PROLAUNCH-90
                        ... PROLAUNCH-461                       
        
        """
        code = '[0-9]{2:%s}'% int(sec)
        return f"{event[:3].upper()}{event_code}-{StringGenerator(str(code)).render(unique=True)}"
        
        

