import time
import calefaccio

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from distutils.util import strtobool

app = Flask(__name__)
api = Api(app)

class Calefaccio(Resource):
    def get(self):
        return { 'is_active': str(calefaccio.status()=="on") }
    def post(self):
        print(request.json)
        active = strtobool(request.json['active'])

        if active:
            calefaccio.on()
        else:
            calefaccio.off()

        return { 'is_active': str(calefaccio.status()=="on") }

api.add_resource(Calefaccio, '/calefaccio')

if __name__ == '__main__':
    calefaccio.init()
    time.sleep(1)
    app.run(host='0.0.0.0', port='5002')
