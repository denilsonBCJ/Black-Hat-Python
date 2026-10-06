# Instale o Paramiko primeiro com "pip install paramiko"
import getpass
import paramiko

def ssh_command(ip,port,user,passwd,cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko,AutoAddPolicy())
    client.connect(ip, port=port,username=user,password=passwd)

    _, stdout, stderr = client.exec_command(cmd)
    output= stdout.readlines() + stderr.readlines()
    if output:
        print("-------------| Saida |---------------")
        for line in output:
            print(line.strip())

if __name__ == "__main__":
    # User = getpass.getuser()
    user = input('Username ')
    password = getpass.getpass()
    ip = input('Insira um IP do servidor: ') or '127.0.0.1'
    port = int(input('Insira a porta ou <CR>: ') or '2222')
    cmd = input('Insira o comando: ')
    ssh_command(ip, port, user, password, cmd)