import eth_client
from flask import Flask, jsonify, make_response
from flask_restful import Resource, Api, reqparse
import argparse
import os

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
        txns = eth_client.get_event_logs(ts_from, ts_to, address)
        return make_response(jsonify([t.get_dict() for t in txns]), 200)


api = Api(app)
api.add_resource(Transfers, '/transfers')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", help="getblock.io API key")
    args = parser.parse_args()
    if args.key:
        eth_client.GETBLOCKIO_KEY = args.key
    elif "GETBLOCKIO_KEY" in os.environ:
        eth_client.GETBLOCKIO_KEY = os.environ["GETBLOCKIO_KEY"]
    else:
        print("Getblock.io API key not found")
        exit(1)

    app.run(port=3000)
