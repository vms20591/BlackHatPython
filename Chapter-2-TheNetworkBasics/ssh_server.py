import socket
import paramiko
import threading
import sys

# using key from paramiko demo files
host_key = paramiko.RSAKey(filename="test_rsa.key")

paramiko.util.log_to_file("filename.log")

class Server(paramiko.ServerInterface):
  def __init__(self):
    self.event = threading.Event()

  def check_channel_request(self, kind, chanid):
    if kind == "session":
      return paramiko.OPEN_SUCCEEDED
    return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

  def check_auth_password(self, username, password):
    if username == "localhost" and password == "localhost":
      return paramiko.AUTH_SUCCESSFUL
    return paramiko.AUTH_FAILED

server = sys.argv[1]
ssh_port = int(sys.argv[2])

try:
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind((server, ssh_port))
  sock.listen(100)

  print "[+] Listening for connection..."

  client,addr = sock.accept()
except Exception, e:
  print "[-] Listen failed: ", str(e)
  sys.exit(1)

print "[+] Got a connection..."

try:
  session = paramiko.Transport(client)
  session.add_server_key(host_key)
  server = Server()

  try:
    session.start_server(server = server)
  except paramiko.SSHException, se:
    print "[-] SSH negotiation failed: ", str(se)

  chan = session.accept(20)

  print "[+] Authenticated..."
  print chan.recv(1024)

  chan.send("Welcome to ssh server")

  while 1:
    try:
      command = raw_input("Enter command: ").strip("\n")

      if command != "exit":
        chan.send(command)
        
        print chan.recv(1024) + "\n"
      else:
        chan.send("exit")

        print "Exiting..."

        session.close()

        raise Exception("exit")
    except KeyboardInterrupt, ki:
      session.close()
except Exception, e:
  print "[-] Caught exception: ", str(e)

  sys.exit(1)
finally:
  session.close()
