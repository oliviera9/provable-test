import eth_client
from flask import Flask, jsonify, make_response
from flask_restful import Resource, Api, reqparse
import argparse
import os
from exceptions import *
import utils

app = Flask(__name__)


class Transfers(Resource):
    def post(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('address', required=True)  # add args
        parser.add_argument('from', type=int, required=True)
        parser.add_argument('to', type=int, required=True)

        args = parser.parse_args()  # parse arguments to dictionary

        address = args['address']
        ts_from = args['from']
        ts_to = args['to']
        if ts_from >= ts_to or not utils.is_address(address):
            return make_response(jsonify({"error": "invalid argument"}), 400)
        try:
            logs = eth_client.get_event_logs(ts_from, ts_to, address)
            return make_response(jsonify([log.get_dict() for log in logs]), 200)
        except InvalidApiKeyException:
            return make_response(jsonify({"error": "invalid apikey"}), 403)
        except FetchDataException:
            return make_response(jsonify({"error": "generic error"}), 500)


api = Api(app)
api.add_resource(Transfers, '/transfers')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", help="getblock.io API key")
    parser.add_argument("--port", type=int, help="Webserver port", default=3000)
    args = parser.parse_args()
    if args.key:
        eth_client.GETBLOCKIO_KEY = args.key
    elif "GETBLOCKIO_KEY" in os.environ:
        eth_client.GETBLOCKIO_KEY = os.environ["GETBLOCKIO_KEY"]
    else:
        print("Getblock.io API key not found")
        exit(1)

    app.run(port=args.port)
