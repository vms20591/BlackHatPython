import paramiko
import threading
import subprocess

def ssh_command(ip, user, passwd, command, port=22):
  client = paramiko.SSHClient()
  #client.load_host_keys("/home/snape/.ssh/known_hosts")
  client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  
  client.connect(ip, port=port, username=user, password=passwd)
  
  ssh_session = client.get_transport().open_session()

  if ssh_session.active:
    ssh_session.exec_command(command)
    print ssh_session.recv(1024)

  return

ssh_command("localhost", "localhost", "localhost", "id")