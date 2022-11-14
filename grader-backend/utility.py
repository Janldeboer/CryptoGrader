from random import randint
from config import *

import socket
import hashlib
import json_canonical


class GraderUtility:
    @staticmethod
    def generate_random_peer():
        # generate a random ip
        peer_ip = ".".join([str(randint(0, 255)) for _ in range(4)])
        # generate a random port
        port = 420 # easy to distinguish from other ports
        return peer_ip + ":" + str(port)

    @staticmethod
    def clear_incoming_messages(client_socket):
        try:
            data = True
            client_socket.setblocking(False)
            while data not in [None, False, "", b'']:
                data = client_socket.recv(MESSAGE_SIZE)
        except socket.error as e:
            pass
        finally:
            client_socket.setblocking(True)

    @staticmethod
    def get_id_from_json(json_object):
        return hashlib.sha256(json_canonical.canonicalize(json_object)).digest().hex()

    @staticmethod
    def get_coinbase_tx(pubkey):
        coinbase_tx_json = {
            "height": 0,
            "outputs": [
                {
                    "pubkey": pubkey,
                    "value": 1000
                }
            ],
            "type": "transaction"
        }
        return coinbase_tx_json

    @staticmethod
    def generate_random_txid():
        return hashlib.sha256(str(randint(0, 1000000)).encode("utf-8")).digest().hex()

    

    @staticmethod
    def generate_random_tx(pubkey="abcdeabcde6a6d5d06ab7f85520df08a309b1a67c1e9d00e60c574885c48d540"):
        # generate a random tx
        tx_json = {
            "inputs": [
                {
                    "outpoint": {
                        "txid": GraderUtility.generate_random_txid(),
                        "index": 0
                    },
                    "sig": "abcd7d774042607c69a87ac5f1cdf92bf474c25fafcc089fe667602bfefb0494726c519e92266957429ced875256e6915eb8cea2ea66366e739415efc47a6805"
                }
            ],
            "outputs": [
                {
                    "pubkey": pubkey,
                    "value": 1000
                }
            ],
            "type": "transaction"
        }
        return tx_json


