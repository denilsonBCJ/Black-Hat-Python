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
