import asyncio
import orjson as json


from os import name
from socket import gethostname, gethostbyname
from flask import Flask, request
from flask_restful import Resource, Api

port = 5000


class Introduction(Resource):
    ''' '''
    
    def get(self):
        '''Introduction  Welcome to aspireDb'''
        
        return {
            "text": f"aspireDB   Available on host {gethostname()} On The Local Network at {gethostbyname(gethostname())}:{port} ... Enjoy!",
            "score": 'tyme'
            }
    
    def post(self):
        try:
            result = request.get_json(['force', 'silent', 'cache'])
            data = result.get('data')
            if result.get('password'):
                return self.get_data(data, result.get('password'))
            else: return data
        except:
            data = request.form.get('data')
            if request.form.get('password'):
                return self.get_data(data, request.form.get('password'))
            else: return data

    def options(self, uri, access):
        data = uri.split("-")
        return {"status":"options", "handle": data, "access": access}

        

    def get_data(self, dn,pw):
        return {"success": "true", "dbn": dn, "access": pw }



    


app = Flask(__name__.split('.')[0])
api = Api(app)


api.add_resource(Introduction, '/<string:uri>/<string:access>')

if __name__ == '__main__':
    app.run(debug=True)
