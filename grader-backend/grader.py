import socket
import json
import time

from random import randint
from nacl.encoding import Base64Encoder
from colorama import Fore, Style

import hashlib
import json_canonical
from nacl.signing import SigningKey

from config import *

from Task1Grader import Task1Grader
from OldTask2Grader import Task2Grader


class Grader:

    @staticmethod
    def check_host(host_credentials):
        # split the host into ip and port
        host_ip, host_port = host_credentials.split(":")
        host_port = int(host_port)

        if host_ip in ip_names:
            print(Fore.RESET + "Running grader on " + ip_names[host_ip])
        else:
            print(Fore.RESET + "Running Grader on " + host_ip + "...\n")

        result = 0
        result_json = {
            "ip": host_ip,
            "results": []
        }

        buffer = ""
        message_stack = []

        # create socket, check if it can connect
        try:
            client_socket = socket.socket()
            client_socket.connect((host_ip, host_port))
            client_socket.settimeout(TIMEOUT_SECONDS)
            print(Fore.RESET + "Connected to " + host_ip)
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't connect to " + host_ip + ":" + str(host_port))
            result_json["results"].append({"name": "connect", "result": 0})
            return result_json

        task1_res = Task1Grader.grade_task_1(client_socket)
        result_json["results"] += task1_res["results"]

        task2_res = Task2Grader.grade_task_2(client_socket)
        result_json["results"] += task2_res["results"]

        return result_json


def run_grader():

    ips_to_check = ["127.0.0.1:18018"]
    results = []


    for ip in ips_to_check:
        res = Grader.check_host(ip)
        results.append(res)

    print(Fore.RESET + "\n\nAll tests finished\n")
    print(Fore.RESET + "==================")
    print(Fore.RESET + "\nResults:\n")

    for res in results:
        ip = res["ip"]
        if ip in ip_names:
            ip = ip_names[ip]
        print(Fore.RESET + "Results for " + ip + ":")

        if res["results"][0]["name"] == "connect":
            print(Fore.RED + "  FAILED: Couldn't connect to node\n")
            continue
        for result in res["results"]:
            task_name = result["name"]
            points = result["points"]
            total = result["total"]
            if points == total:
                print(Fore.GREEN + "  " + task_name + ": " + str(points) + "/" + str(total))
            else:
                print(Fore.RED + "  " + task_name + ": " + str(points) + "/" + str(total))
        print("")

    print("\n")


