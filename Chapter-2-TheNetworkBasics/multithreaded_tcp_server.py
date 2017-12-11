import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip, bind_port))

server.listen(5)

print "[*] Listening on {0}:{1}".format(bind_ip, bind_port)

# client handling thread
def handle_client(client_socket):
    # print client data
    request = client_socket.recv(1024)

    print "[*] Received {0}".format(request)

    # send back response
    client_socket.send("ACK!")

    client_socket.close()

while True:
    client, addr = server.accept()

    print "[*] Accepted connection from: {0}:{1}".format(addr[0], addr[1])

    # create a new thread to handle client
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()