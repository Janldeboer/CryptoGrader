from colorama import Fore
from config import *
from nacl.signing import SigningKey
from nacl.encoding import Base64Encoder

import socket
import json
import time

from utility import GraderUtility


class Task2Grader:

    @staticmethod
    def grade_task_2(client_socket):
        # TASK 2
        result = 0
        result_json = {"results": []}

        # if we send a new object with ihaveobject, the node should send us the object when we ask for it
        # 1. Generate a new keypair
        # 2. Generate a new coinbase transaction with the public key
        # 3. Send the ihaveobject message to the node
        # 4. Node should ask for the object
        # 5. Send the object to the node
        # 6. Send getobject message
        # 7. Node should send the transaction from before
        
        # 1. generate a new keypair
        private_key = SigningKey.generate()
        public_key = private_key.verify_key
        # 2. generate a new coinbase transaction
        coinbase_tx_json = {
            "height": 0,
            "outputs": [
                {
                    "pubkey": public_key.encode(encoder=Base64Encoder).decode("utf-8"),
                    "value": 1000
                }
            ],
            "type": "transaction"
        }
        print(public_key.encode(encoder=Base64Encoder).decode("utf-8"))
        coinbase_txid = GraderUtility.get_id_from_json(coinbase_tx_json)
        message = "{\"type\": \"ihaveobject\", \"object_id\": \"" + coinbase_txid + "\"}\n"
        # clear out all incoming messages
        time.sleep(1)
        GraderUtility.clear_incoming_messages(client_socket)
        # 3. send the ihaveobject message
        try:
            client_socket.sendall(str.encode(message))
            print(Fore.RESET + "INFO: Sent ihaveobject message with txid " + coinbase_txid[:10] + "...")
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't send ihaveobject message")
        # 4. see if the node asks for the object
        data = ""
        try:
            while "\n" not in data:
                new_data = client_socket.recv(MESSAGE_SIZE).decode("utf-8")
                if new_data in [None, "", b'']:
                    break
                data += new_data
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't receive getobject message in time (" + str(TIMEOUT_SECONDS) + "s)")
        for line in data.split("\n"):
            if line == "":
                continue
            try:
                data_json = json.loads(line)
                if "type" not in data_json:
                    print(Fore.RED + "FAILED: Getobject message doesn't contain type")
                    print(Fore.RED + " -> received: " + line)
                elif data_json["type"] != "getobject":
                    print(Fore.RED + "FAILED: Expected getobject message")
                    print(Fore.RED + " -> received: " + line)
                else:
                    # check if the object_id is in the message
                    if coinbase_txid not in data_json["object_id"]:
                        print(Fore.RED + "FAILED: The object_id is not in the getobject message")
                    else:
                        print(Fore.GREEN + "SUCCESS: The object_id is in the getobject message")
                        result += 1
                        break
            except Exception as e:
                print(Fore.RED + "FAILED: Couldn't decode getobject message")
                print(Fore.RED + " -> received: " + line)
        # 5. send the object to the node
        try:
            message = "{\"type\": \"object\", \"object\": " + json.dumps(coinbase_tx_json) + "}\n"
            client_socket.sendall(str.encode(message))
            print(Fore.RESET + "INFO: Sent coinbase transaction")
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't send object message")
        # 6. send the getobject message
        message = "{\"type\": \"getobject\", \"object_id\": \"" + coinbase_txid + "\"}\n"
        try:
            client_socket.sendall(str.encode(message))
            print(Fore.RESET + "INFO: Sent getobject message with txid " + coinbase_txid[:10] + "...")
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't send getobject message")
        # 7. see if the node sends the transaction
        data = ""
        try:
            while "\n" not in data:
                new_data = client_socket.recv(MESSAGE_SIZE).decode("utf-8")
                if new_data in [None, "", b'']:
                    break
                data += new_data
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't receive transaction in time (" + str(TIMEOUT_SECONDS) + "s)")
        for line in data.split("\n"):
            if line == "":
                continue
            try:
                data_json = json.loads(line)
                if "type" not in data_json:
                    print(Fore.RED + "FAILED: Transaction message doesn't contain type")
                    print(Fore.RED + " -> received: " + line)
                elif data_json["type"] != "object":
                    print(Fore.RED + "FAILED: Expected transaction message")
                    print(Fore.RED + " -> received: " + line)
                else:
                    # calculate the transaction id
                    tx = data_json["object"]
                    txid = GraderUtility.get_id_from_json(tx)

                    # check if the transaction id matches the one we sent
                    if txid != coinbase_txid:
                        print(Fore.RED + "FAILED: The transaction id doesn't match / Wrong transaction")
                        print(Fore.RED + " -> received: " + data_json + " with id " + txid[:10] + "...")
                    else:
                        print(Fore.GREEN + "SUCCESS: The transaction id matches")
                        result += 1
                        break
            except Exception as e:
                print(Fore.RED + "FAILED: Couldn't decode transaction message")
                print(Fore.RED + " -> received: " + line)


        # transaction validation test
        # send hardcoded transaction that have to be valid

        print(Fore.RESET + "INFO: Starting transaction validation test with valid transactions")

        valid_coinbase_tx_json = {"height":0,"outputs":[{"pubkey":"5e3f197d8b63a853b79330d96a82d2ad51ff06605879f5f4b664c1d9a6b9c02e","value":50}],"type":"transaction"}
        valid_followup_tx_json = {"inputs":[{"outpoint":{"index":0,"txid":"8a6fdba6541db169d9bb3249e91bfde5692048818031aa55062a41c673bd01ea"},"sig":"6f3d4522bf29e55becb3ce707830f62954cb109464737ea37bd0213f14ea52b530fe0c13d56c9496fa72466cbd94fb0a927e53a57786bca2dfa7214c89580403"}],"outputs":[{"pubkey":"5e3f197d8b63a853b79330d96a82d2ad51ff06605879f5f4b664c1d9a6b9c02e","value":50}],"type":"transaction"}

        # 1. send the ihaveobject message
        message = "{\"type\": \"ihaveobject\", \"object_id\": \"" + GraderUtility.get_id_from_json(valid_coinbase_tx_json) + "\"}\n"
        try:
            client_socket.sendall(str.encode(message))
            print(Fore.RESET + "INFO: Sent ihaveobject message with txid " + GraderUtility.get_id_from_json(valid_coinbase_tx_json)[:10] + "...")
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't send ihaveobject message")
        # 2. see if the node sends the getobject message
        data = ""
        try:
            while "\n" not in data:
                new_data = client_socket.recv(MESSAGE_SIZE).decode("utf-8")
                if new_data in [None, "", b'']:
                    break
                data += new_data
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't receive getobject message in time (" + str(TIMEOUT_SECONDS) + "s)")
        for line in data.split("\n"):
            if line == "":
                continue
            try:
                data_json = json.loads(line)
                if "type" not in data_json:
                    print(Fore.RED + "FAILED: Getobject message doesn't contain type")
                    print(Fore.RED + " -> received: " + line)
                elif data_json["type"] != "getobject":
                    print(Fore.RED + "FAILED: Expected getobject message")
                    print(Fore.RED + " -> received: " + line)
                else:
                    # check if the object_id is in the message
                    if GraderUtility.get_id_from_json(valid_coinbase_tx_json) not in data_json["object_id"]:
                        print(Fore.RED + "FAILED: The object_id is not in the getobject message")
                    else:
                        print(Fore.GREEN + "SUCCESS: The object_id is in the getobject message")
                        result += 1
                        break
            except Exception as e:
                print(Fore.RED + "FAILED: Couldn't decode getobject message")
                print(Fore.RED + " -> received: " + line)

        # 3. send the object message
        message = "{\"type\": \"object\", \"object\": " + json.dumps(valid_coinbase_tx_json) + "}\n"
        try:
            client_socket.sendall(str.encode(message))
            print(Fore.RESET + "INFO: Sent object message with txid " + GraderUtility.get_id_from_json(valid_coinbase_tx_json)[:10] + "...")
            print("     The public key is: " + valid_coinbase_tx_json["outputs"][0]["pubkey"][:10] + "...")
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't send object message")

        # wait a few seconds to give the node time to validate the transaction
        time.sleep(5)

        # 4. send the ihaveobject message
        message = "{\"type\": \"ihaveobject\", \"object_id\": \"" + GraderUtility.get_id_from_json(valid_followup_tx_json) + "\"}\n"
        try:
            client_socket.sendall(str.encode(message))
            print(Fore.RESET + "INFO: Sent ihaveobject message with txid " + GraderUtility.get_id_from_json(valid_followup_tx_json)[:10] + "...")
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't send ihaveobject message")

        # 5. see if the node sends the getobject message
        data = ""
        try:
            while "\n" not in data:
                new_data = client_socket.recv(MESSAGE_SIZE).decode("utf-8")
                if new_data in [None, "", b'']:
                    break
                data += new_data
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't receive getobject message in time (" + str(TIMEOUT_SECONDS) + "s)")
        for line in data.split("\n"):
            if line == "":
                continue
            try:
                data_json = json.loads(line)
                if "type" not in data_json:
                    print(Fore.RED + "FAILED: Getobject message doesn't contain type")
                    print(Fore.RED + " -> received: " + line)
                elif data_json["type"] != "getobject":
                    print(Fore.RED + "FAILED: Expected getobject message")
                    print(Fore.RED + " -> received: " + line)
                else:
                    # check if the object_id is in the message
                    if GraderUtility.get_id_from_json(valid_followup_tx_json) not in data_json["object_id"]:
                        print(Fore.RED + "FAILED: The object_id is not in the getobject message")
                    else:
                        print(Fore.GREEN + "SUCCESS: The object_id is in the getobject message")
                        result += 1
                        break
            except Exception as e:
                print(Fore.RED + "FAILED: Couldn't decode getobject message")
                print(Fore.RED + " -> received: " + line)

        # 6. send the object message
        message = "{\"type\": \"object\", \"object\": " + json.dumps(valid_followup_tx_json) + "}\n"
        try:
            client_socket.sendall(str.encode(message))
            print(Fore.RESET + "INFO: Sent object message with txid " + GraderUtility.get_id_from_json(valid_followup_tx_json)[:10] + "...")
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't send object message")

        # wait for a few seconds so the node can process the transactions
        time.sleep(5)

        # 7. send getobject message to see if the transaction was accepted
        message = "{\"type\": \"getobject\", \"object_id\": \"" + GraderUtility.get_id_from_json(valid_followup_tx_json) + "\"}\n"
        try:
            client_socket.sendall(str.encode(message))
            print(Fore.RESET + "INFO: Sent getobject message with txid " + GraderUtility.get_id_from_json(valid_followup_tx_json)[:10] + "...")
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't send getobject message")
        # 8. see if the node sends the object message
        data = ""
        try:
            while "\n" not in data:
                new_data = client_socket.recv(MESSAGE_SIZE).decode("utf-8")
                if new_data in [None, "", b'']:
                    break
                data += new_data
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't receive object message in time (" + str(TIMEOUT_SECONDS) + "s)")
        for line in data.split("\n"):
            if line == "":
                continue
            try:
                data_json = json.loads(line)
                if "type" not in data_json:
                    print(Fore.RED + "INFO: Object message doesn't contain type")
                    print(Fore.RED + " -> received: " + line)
                elif data_json["type"] != "object":
                    print(Fore.RED + "INFO: Expected object message")
                    print(Fore.RED + " -> received: " + line)
                else:
                    object = data_json["object"]
                    object_id = GraderUtility.get_id_from_json(object)
                    if object_id != GraderUtility.get_id_from_json(valid_followup_tx_json):
                        print(Fore.RED + "INFO: The object_id is not matching")
                    else:
                        print(Fore.GREEN + "SUCCESS: The object_id is matching")
                        result += 1
                        break

            except Exception as e:
                print(Fore.RED + "FAILED: Couldn't decode object message")
                print(Fore.RED + " -> received: " + line)

        # Now check an invalid transaction
        # Just generate a random transaction and send it to the node

        print(Fore.RESET + "INFO: Sending invalid transaction to node...")

        # 1. send the tx message
        invalid_tx_json = GraderUtility.generate_random_tx()
        message = {
            "type": "object",
            "object": invalid_tx_json
        }
        try:
            client_socket.sendall(str.encode(json.dumps(message) + "\n"))
            print(Fore.RESET + "INFO: Sent object message with txid " + GraderUtility.get_id_from_json(invalid_tx_json)[:10] + "...")
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't send object message")

        # we should receive an error message
        data = ""
        try:
            while "\n" not in data:
                new_data = client_socket.recv(MESSAGE_SIZE).decode("utf-8")
                if new_data in [None, "", b'']:
                    break
                data += new_data
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't receive error message in time (" + str(TIMEOUT_SECONDS) + "s)")
        for line in data.split("\n"):
            if line == "":
                continue
            try:
                data_json = json.loads(line)
                if "type" not in data_json:
                    print(Fore.RED + "INFO: Error message doesn't contain type")
                    print(Fore.RED + " -> received: " + line)
                elif data_json["type"] != "error":
                    print(Fore.RED + "INFO: Expected error message")
                    print(Fore.RED + " -> received: " + line)
                else:
                    print(Fore.GREEN + "SUCCESS: Received an error message")
                    result += 1
                    break
            except Exception as e:
                print(Fore.RED + "FAILED: Couldn't decode error message")
                print(Fore.RED + " -> received: " + line)

        # clear up all incoming messages
        GraderUtility.clear_incoming_messages(client_socket)

        # 2. send the getobject message, to see if the node has saved the transaction
        invalid_tx_txid = GraderUtility.get_id_from_json(invalid_tx_json)
        message = {
            "type": "getobject",
            "object_id": invalid_tx_txid
        }
        try:
            client_socket.sendall(str.encode(json.dumps(message) + "\n"))
            print(Fore.RESET + "INFO: Sent getobject message with txid " + invalid_tx_txid[:10] + "...")
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't send getobject message")
            
        # we should receive an error message
        data = ""
        try:
            while "\n" not in data:
                new_data = client_socket.recv(MESSAGE_SIZE).decode("utf-8")
                if new_data in [None, "", b'']:
                    break
                data += new_data
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't receive error message in time (" + str(TIMEOUT_SECONDS) + "s)")
        for line in data.split("\n"):
            if line == "":
                continue
            try:
                data_json = json.loads(line)
                if "type" not in data_json:
                    print(Fore.RED + "INFO: Error message doesn't contain type")
                    print(Fore.RED + " -> received: " + line)
                elif data_json["type"] == "object":
                    object = data_json["object"]
                    object_id = GraderUtility.get_id_from_json(object)
                    if object_id != invalid_tx_txid:
                        print(Fore.RED + "INFO: No error message received")
                    else :
                        print(Fore.RED + "FAILED: Received an object message with the invalid transaction")
                        break
                elif data_json["type"] != "error":
                    print(Fore.RED + "INFO: Expected error message")
                    print(Fore.RED + " -> received: " + line)
                else:
                    print(Fore.GREEN + "SUCCESS: Received an error message")
                    result += 1
                    break
            except Exception as e:
                print(Fore.RED + "FAILED: Couldn't decode error message")
                print(Fore.RED + " -> received: " + line)




        # Print the result
        total_points = 7
        result_text = "[" + str(result) + "/" + str(total_points) + "]"
        result_json["results"].append({"name": "Task 2", "points": result, "total": total_points})


        return result_json
