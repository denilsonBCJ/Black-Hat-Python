import sys
import socket
import threading

HEX_FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])

def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):
        src = src.decode()
    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i + length])
        printable = word.translate(HEX_FILTER)
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        hexwidth = length * 3
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results

def receive_from(connection):
    buffer = b''
    connection.settimeout(2)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer

def request_handler(buffer):
    return buffer

def response_handler(buffer):
    return buffer

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        remote_buffer = response_handler(remote_buffer)
        if len(remote_buffer):
            print(f'[<==] Recebido {len(remote_buffer)} bytes do localhost.')
            client_socket.send(remote_buffer)
    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            print(f'[==>] Recebido {len(local_buffer)} bytes do localhost.')
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print('[==>] Enviado para o servidor remoto.')
        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print(f'[<==] Recebido {len(remote_buffer)} bytes do servidor remoto.')
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print('[<==] Enviado para localhost.')
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print('[*] Não ha mais dados. Fechando conexões.')
            break

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print(f'Falha ao conectar na porta {local_port}.')
        print(f'[!!] Erro: {e}')
        print('[!!] Falha ao ouvir em %s:%d' % (local_host, local_port))
        print('[!!] Verifique outros socket de escuta ou corrija as permissões.')
        sys.exit(0)
    print("[*] Escutando em %s:%d" % (local_host, local_port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        # imprimir as informações de conexão local
        line - "> Conexão recebida de %s:%d" % (addr[0], addr[1])
        # iniciar uma thread para tratar a conexão remota
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 5:
        print("Uso: ./Proxy_TCP.py [localhost] [localport] [remotehost] [remoteport] [receive_first]")
        print("Exemplo: ./Proxy_TCP.py 127.0.0.1 8080 127.0.0.1 8081 True")
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    receive_first = sys.argv[5].lower() == 'true'

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == '__main__':
    main()