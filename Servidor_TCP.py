import socket
import threading

IP = "0.0.0.0"
PORT = 9998

def main():
    # Cria um objeto socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Vincula o socket a um endereço e porta
    server.bind((IP, PORT))

    # Coloca o servidor em modo de escuta
    server.listen(5)
    print(f'[*] Ouvindo em {IP}:{PORT}')

    while True:
        client, address = server.accept()
        print(f'[*] Aceitou conexão de {address[0]}:{address[1]}')
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

def handle_client(client_socket):
    while True:
        request = client_socket.recv(1024)
        print(f'[*] Recebeu: {request.decode()}')
        client_socket.send(b'ACK')

if __name__ == "__main__":
    main()
