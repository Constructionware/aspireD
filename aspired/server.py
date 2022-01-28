# server.py
import re
import orjson as json

from os import name
from socket import gethostname, gethostbyname
from flask import Flask, request
from flask_restful import Resource, Api

from aspired.core.api import Database, PrivateDocument, PublicDocument
from aspired.core.zen import zen_now


# ------- config ------------
debug = True  # O
port = 22090
host = "0.0.0.0"

# -----------  Application -------------

app = Flask(__name__.split('.')[0])
api = Api(app)

api.add_resource(Database, '/<string:dbname>/<string:password>')

api.add_resource(PublicDocument, '/<string:dbname>/<string:doc_id>/<string:clone_id>')

api.add_resource(PrivateDocument, '/<string:dbname>/<string:doc_id>/<string:clone_id>')

def serve():
    app.run(debug=debug)

if __name__ == '__main__':
    serve()

