import socket
import threading
import time

SERVER_IP = '192.168.0.120'  # IP do servidor
SERVER_PORT = 12345  # Porta do servidor
BUFFER_SIZE = 1500  # Tamanho limite do buffer de pacote

# Criação do socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

print(f"Servidor ouvindo em {SERVER_IP}:{SERVER_PORT}")

def medir_upload():
    """
    Função que mede a taxa de upload (dados recebidos) do cliente.
    """
    total_data = 0
    start_time = time.time()

    while True:
        data, client_address = server_socket.recvfrom(BUFFER_SIZE)
        total_data += len(data)

        if data.decode('utf-8').lower() == 'sair':
            break

    end_time = time.time()
    total_time = end_time - start_time

    if total_time > 0:
        upload_speed = total_data / total_time  # Taxa de transferência em bytes/segundo
        print(f"Taxa de upload: {upload_speed / 1024:.2f} KB/s")

    server_socket.close()

# Iniciar a medição de upload
medir_upload()
