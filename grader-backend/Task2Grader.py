from colorama import Fore
from config import *
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder, Base64Encoder

import socket
import json
import time
import random

import json_canonical

from utility import GraderUtility


class Task2Grader:
  # TASK 2

  # Grading description:
  # Consider two nodes: Grader1 and Grader2.
  # 1. Object Exchange:
  # • If Grader 1 sends a new valid transaction object and then requests the same object, Grader 1 should receive the object.
  # • If Grader 1 sends a new valid transaction object and then Grader 2 requests the same object, Grader 2 should receive the object.
  # • If Grader 1 sends a new valid transaction object, Grader 2 must receive an ihaveobject message with the object id.
  # • If Grader 1 sends an ihaveobject message with the id of a new object, Grader 1 must receive a getobject message with the same object id.
  # 2. Transaction Validation:
  # • On receiving an object message from Grader 1 containing any invalid transactions, Grader 1 must receive an error message and the transaction must not be gossiped to Grader 2. Beware: invalid transactions may come in many different forms!
  # • On receiving an object message from Grader 1 containing a valid transaction, the trans- action must be gossiped to Grader 2.

  # We have to use middleman nodes to test this, because we can't send from two ip addresses to the same node at the same time
  
  @staticmethod
  def grade_task_2(client_socket):
    results = []
    results.append(Task2Grader.grade_task_2_1_1(client_socket))

    return results

  # 1.1. If Grader 1 sends a new valid transaction object and then requests the same object, Grader 1 should receive the object.
  @staticmethod
  def grade_task_2_1_1(client_socket):
    # generate a valid (coinbase) transaction
    private_key = SigningKey.generate()
    public_key = private_key.verify_key

    coinbase_tx_json = GraderUtility.generate_coinbase_tx(public_key)

    coinbase_txid = GraderUtility.get_id_from_json(coinbase_tx_json)
    print("INFO: Generated coinbase transaction with id " + coinbase_txid[:10] + "...")

    # we directly send the object to the node, no need to send ihaveobject first
    message = {
      "type": "object",
      "object": coinbase_tx_json
    }

    message_bytes = json_canonical.canonicalize(message) + b"\n"

    try:
      client_socket.sendall(message_bytes)
      print(Fore.RESET + "INFO: Sent object message with txid " + coinbase_txid[:10] + "...")
    except socket.error as e:
      print(Fore.RED + "FAILED: Couldn't send object message")

    # clear out all incoming messages
    time.sleep(1)
    GraderUtility.clear_incoming_messages(client_socket)

    # send getobject message
    message = {
      "type": "getobject",
      "object_id": coinbase_txid
    }

    message_bytes = json_canonical.canonicalize(message) + b"\n"

    try:
      client_socket.sendall(message_bytes)
      print(Fore.RESET + "INFO: Sent getobject message with txid " + coinbase_txid[:10] + "...")
    except socket.error as e:
      print(Fore.RED + "FAILED: Couldn't send getobject message")

    # wait for the object message
    try:
      client_socket.settimeout(TIMEOUT_SECONDS)
      response = client_socket.recv(MESSAGE_SIZE)
      print(Fore.RESET + "INFO: Received response message: " + response.decode("utf-8")[:20] + "...")
    except socket.error as e:
      print(Fore.RED + "FAILED: Couldn't receive response message")
      return {"name": "task2_1_1", "result": 0}

    # check if the response is an object message
    try:
      response_json = json.loads(response)
      if response_json["type"] != "object":
        print(Fore.RED + "FAILED: Received wrong message type")
        return {"name": "task2_1_1", "result": 0}
    except json.JSONDecodeError as e:
      print(Fore.RED + "FAILED: Received invalid JSON")
      return {"name": "task2_1_1", "result": 0}

    # check if the object is the same as the one we sent
    if response_json["object"] != coinbase_tx_json:
      print(Fore.RED + "FAILED: Received wrong object")
      return {"name": "task2_1_1", "result": 0}

    print(Fore.GREEN + "SUCCESS: Received correct object")
    return {"name": "task2_1_1", "result": 1}

  # 1.2. If Grader 1 sends a new valid transaction object and then Grader 2 requests the same object, Grader 2 should receive the object.
  @staticmethod
  def grade_task_2_1_2(client_socket):
    # we cant test this locally, because we can't send from two ip addresses to the same node at the same time
    # I'll work on a hosted version of this test
    pass

  # 1.3. If Grader 1 sends a new valid transaction object, Grader 2 must receive an ihaveobject message with the object id.
  @staticmethod
  def grade_task_2_1_3(client_socket):
    # we can only simulate this by sending a getobject message to the node
    # we have to can hand the localhost + a port of our choice to the node in a peers message
    # then we listen on that port
    # we send an object message to the node
    # on the listening port we should receive an ihaveobject message

    # generate a valid (coinbase) transaction
    private_key = SigningKey.generate()
    public_key = private_key.verify_key

    coinbase_tx_json = GraderUtility.get_coinbase_tx(public_key)

    coinbase_txid = GraderUtility.get_id_from_json(coinbase_tx_json)

    # pick a random port
    port = random.randint(10000, 60000)

    # send peers message
    message = {
      "type": "peers",
      "peers": ["127.0.0.1:" + str(port)]
    }

    message_bytes = json_canonical.canonicalize(message) + b"\n"

    try:
      client_socket.sendall(message_bytes)
      print(Fore.RESET + "INFO: Sent peers message...")
    except socket.error as e:
      print(Fore.RED + "FAILED: Couldn't send peers message")
      return {"name": "task2_1_3", "result": 0}
      
    # now we have to listen on the port
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.bind(('', port))
      s.listen(1)
      print(Fore.RESET + "INFO: Listening on port " + str(port) + "...")
    except socket.error as e:
      print(Fore.RED + "FAILED: Couldn't listen on port " + str(port))
      return {"name": "task2_1_3", "result": 0}

    # we directly send the object to the node, no need to send ihaveobject first
    message = {
      "type": "object",
      "object": coinbase_tx_json
    }

    message_bytes = json_canonical.canonicalize(message) + b"\n"

    try:
      client_socket.sendall(message_bytes)
      print(Fore.RESET + "INFO: Sent object message with txid " + coinbase_txid[:10] + "...")
    except socket.error as e:
      print(Fore.RED + "FAILED: Couldn't send object message")
      return {"name": "task2_1_3", "result": 0}

    # wait for the ihaveobject message
    # we'll probably receive a hello and getpeers message first, so we have to clear those out








