import socket
import threading
import time

clients = []  # Lista de clientes conectados

def handle_client(client_socket):
    """
    Lida com a comunicação com o cliente e calcula a taxa de transferência de upload.
    """
    total_data = 0
    start_time = time.time()

    while True:
        try:
            message = client_socket.recv(4096)  # Recebe em blocos de 4096 bytes
            if message:
                total_data += len(message)  # Calcula a quantidade de dados recebidos
            else:
                break
        except:
            break

    end_time = time.time()
    total_time = end_time - start_time
    if total_time > 0:
        upload_speed = total_data / total_time  # Taxa de transferência em bytes/segundo
        print(f"Taxa de upload do cliente: {upload_speed / 1024:.2f} KB/s")

    client_socket.close()

def start_server(ip, port):
    """
    Inicia o servidor TCP para medir a taxa de upload dos clientes.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(5)
    print(f"Servidor iniciado em {ip}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Conexão estabelecida com {client_address}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    ip = input("Digite o endereço IP do servidor: ")
    port = int(input("Digite a porta do servidor: "))
    start_server(ip, port)
