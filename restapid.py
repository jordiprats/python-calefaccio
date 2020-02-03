import calefaccio

from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class Calefaccio(Resource):
    def get(self):
        return { 'active': calefaccio.status() }

api.add_resource(Calefaccio, '/calefaccio')

if __name__ == '__main__':
     app.run(port='5002')
