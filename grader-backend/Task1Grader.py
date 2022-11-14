from colorama import Fore
from config import *
from nacl.signing import SigningKey

import socket
import json
import time

from utility import GraderUtility


class Task1Grader:

    @staticmethod
    def grade_task_1(client_socket):

        client_socket.settimeout(TIMEOUT_SECONDS)

        buffer = ""
        result = 0
        result_json = {"results": []}

        # we should receive a hello message from the node first
        try:
            while "\n" not in buffer:
                buffer += client_socket.recv(MESSAGE_SIZE).decode("utf-8")
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't receive hello message in time (" + str(TIMEOUT_SECONDS) + "s)")
        message_stack = buffer.split("\n")[0:-1]
        buffer = buffer.split("\n")[-1]
        if len(message_stack) != 0:
            data_string = message_stack.pop(0)

            # check if the hello message is valid
            try:
                data_json = json.loads(data_string)

                all_success = True

                # see if type is included
                if "type" not in data_json:
                    print(Fore.RED + "FAILED: Hello message doesn't contain type")
                    print(Fore.RED + " -> received: " + data_string)
                    all_success = False
                elif data_json["type"] != "hello":
                    print(Fore.RED + "FAILED: First message isn't a hello message")
                    print(Fore.RED + " -> received: " + data_string)
                    all_success = False
                else:
                    if "version" not in data_json:
                        print(Fore.RED + "FAILED: Hello message doesn't contain version")
                        print(Fore.RED + " -> received: " + data_string)
                        all_success = False
                    elif data_json["version"][:4] != "0.8.":
                        print(Fore.RED + "FAILED: Hello message doesn't start with 0.8")
                        print(Fore.RED + " -> received: " + data_string)
                        all_success = False

                    if "agent" not in data_json:
                        print(Fore.RED + "FAILED: Hello message doesn't contain agent")
                        print(Fore.RED + " -> received: " + data_string)
                        all_success = False
                    elif data_json["agent"] == "Kerma−Core Client 0.8":
                        print(Fore.RED + "FAILED: Agent in hello message not changed")
                        print(Fore.RED + " -> received: " + data_string)
                        all_success = False

                if all_success:
                    print(Fore.GREEN + "SUCCESS: First message is a valid hello message")
                    result += 1

            except Exception as e:
                print(Fore.RED + "FAILED: Couldn't decode first message")
                print(Fore.RED + " -> received: " + data_string)
        if len(message_stack) == 0:
            # then we should receive a getpeers message
            try:
                while "\n" not in buffer:
                    buffer += client_socket.recv(MESSAGE_SIZE).decode("utf-8")
            except socket.error as e:
                print(Fore.RED + "FAILED: Couldn't receive getpeers message in time (" + str(TIMEOUT_SECONDS) + "s)")

            message_stack = buffer.split("\n")[0:-1]
            buffer = buffer.split("\n")[-1]
        if len(message_stack) != 0:

            data_string = message_stack.pop(0)
            # check if the getpeers message is valid
            try:
                data_json = json.loads(data_string)
                if "type" not in data_json:
                    print(Fore.RED + "FAILED: Getpeers message doesn't contain type")
                    print(Fore.RED + " -> received: " + data_string)
                elif data_json["type"] != "getpeers":
                    print(Fore.RED + "FAILED: Second message isn't a getpeers message")
                    print(Fore.RED + " -> received: " + data_string)
                else:
                    print(Fore.GREEN + "SUCCESS: Second message is a valid getpeers message")
                    result += 1

            except Exception as e:
                print(Fore.RED + "FAILED: Couldn't decode getpeers message")
                print(Fore.RED + " -> received: " + data_string)

        # we should send a hello message, otherwise the node will disconnect
        try:
           client_socket.sendall(b'{"type":"hello","version":"0.8.0","agent":"Fake Grader"}\n')
           print(Fore.RESET + "INFO: Sent hello message")
        except socket.error as e:
           print(Fore.RED + "FAILED: Couldn't send hello message")
        # there might be a hello message from the node, but we don't care about it
        # so first wait, then clear message stack
        time.sleep(1)
        GraderUtility.clear_incoming_messages(client_socket)
        # we should send a getpeers message
        # we should receive a peers message
        try:
            client_socket.sendall(b'{"type": "getpeers"}\n')
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't send getpeers message")


        buffer = ""
        try:
            while "\n" not in buffer:
                buffer += client_socket.recv(MESSAGE_SIZE).decode("utf-8")
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't receive peers message in time (" + str(TIMEOUT_SECONDS) + "s)")
        message_stack = buffer.split("\n")[0:-1]
        buffer = buffer.split("\n")[-1]
        if len(message_stack) != 0:
            # check if the peers message is valid
            data_string = message_stack.pop(0)
            try:
                data_json = json.loads(data_string)
                if "type" not in data_json:
                    print(Fore.RED + "FAILED: Peers message doesn't contain type")
                    print(Fore.RED + " -> received: " + data_string)
                elif data_json["type"] != "peers":
                    print(Fore.RED + "FAILED: Peers message isn't a peers message")
                    print(Fore.RED + " -> received: " + data_string)
                else:
                    print(Fore.GREEN + "SUCCESS: Peers message is a valid peers message")
                    result += 1

            except Exception as e:
                print(Fore.RED + "FAILED: Couldn't decode peers message")
                print(Fore.RED + " -> received: " + data_string)
        # Checkpoint: We have tested the basic functionality of the node
        # quickly empty out all incoming messages
        GraderUtility.clear_incoming_messages(client_socket)
        # lets send invalid messages
        try:
            client_socket.sendall(b'{"te": "get\n')
            print(Fore.RESET + "INFO: Sent invalid message")
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't send invalid message")
        # we should receive an error message
        data = ""
        try:
            while "\n" not in data:
                data += client_socket.recv(MESSAGE_SIZE).decode("utf-8")
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't receive error message in time (" + str(TIMEOUT_SECONDS) + "s)")
        if data is not None:
            # check if the error message is valid
            data_string = data.split("\n")[0]
            try:
                items = data_string.split("\n")
                for item in items:
                    data_json = json.loads(item)
                    if "type" not in data_json:
                        print(Fore.RED + "FAILED: Error message doesn't contain type")
                        print(Fore.RED + " -> received: " + item)
                    elif data_json["type"] != "error":
                        print(Fore.RED + "FAILED: Error message isn't a error message")
                        print(Fore.RED + " -> received: " + item)
                    else:
                        print(Fore.GREEN + "SUCCESS: Error message is a valid error message")
                        result += 1

            except Exception as e:
                print(Fore.RED + "FAILED: Couldn't decode error message")
        # Now test the peers and storing of peers
        # 1. Generate a random peer
        # 2. Send it to the node
        # 3. Check if the node sends it back
        fake_peer = GraderUtility.generate_random_peer()
        # clear out all incoming messages
        GraderUtility.clear_incoming_messages(client_socket)
        # send the peer to the node
        try:
            message = "{\"type\": \"peers\", \"peers\": [\"" + fake_peer + "\"]}\n"
            client_socket.sendall(str.encode(message))
            print(Fore.RESET + "INFO: Sent peers message with fake peer " + fake_peer)
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't send peer to node")
        # clear out all incoming messages
        GraderUtility.clear_incoming_messages(client_socket)
        # send a getpeers message
        try:
            client_socket.sendall(b'{"type": "getpeers"}\n')
            print(Fore.RESET + "INFO: Sent getpeers message")
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't send getpeers message")
        # we should receive a peers message
        data = ""
        try:
            while "\n" not in data:
                new_data = client_socket.recv(MESSAGE_SIZE).decode("utf-8")
                if new_data in [None, "", b'']:
                    break
                data += new_data
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't receive peers message in time (" + str(TIMEOUT_SECONDS) + "s)")
        for line in data.split("\n"):
            if line == "":
                continue
            try:
                data_json = json.loads(line)
                if "type" not in data_json:
                    print(Fore.RED + "FAILED: Peers message doesn't contain type")
                    print(Fore.RED + " -> received: " + line)
                elif data_json["type"] != "peers":
                    print(Fore.RED + "FAILED: Expected peers message")
                    print(Fore.RED + " -> received: " + line)
                else:
                    # check if the peer is in the message
                    if fake_peer not in data_json["peers"]:
                        print(Fore.RED + "FAILED: The peer is not in the peers message")
                    else:
                        print(Fore.GREEN + "SUCCESS: The peer is in the peers message")
                        result += 1
                        break

            except Exception as e:
                print(Fore.RED + "FAILED: Couldn't decode peers message")
                print(Fore.RED + " -> received: " + line)
        # Last check: Multimessages and split messages
        # 1. Send a message that is split in two
        # TODO for Task 1:
        #  - Send a message that is split in two
        #  - Send multiple messages in one sendall call
        #  - Check how node handles disconnection
        result_text = "[" + str(result) + "/" + str(5) + "]"
        result_json["results"].append({"name": "Task 1", "points": result, "total": 5})
        print(Fore.RESET + "Task 1 test finished: " + result_text + "\n\n")
        return result_json

