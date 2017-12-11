import socket

target_host = "localhost"
target_port = 9999

# create a client object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to client
client.connect((target_host, target_port))

# send data
client.send("GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")

# receive data
response = client.recv(4096)

print response
