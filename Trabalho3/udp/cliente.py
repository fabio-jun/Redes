import socket
import time

SERVER_IP = '192.168.0.120'  # IP do servidor
SERVER_PORT = 12345  # Porta do servidor
BUFFER_SIZE = 1500  # Tamanho limite do buffer de pacote

# Definição do socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def medir_download():
    """
    Função que envia dados ao servidor para medir a taxa de download.
    """
    total_data = 0
    start_time = time.time()

    # Envia uma quantidade de dados durante 10 segundos
    while time.time() - start_time < 10:
        message = b'X' * BUFFER_SIZE  # Envia blocos de BUFFER_SIZE bytes
        client_socket.sendto(message, (SERVER_IP, SERVER_PORT))
        total_data += len(message)

    # Enviar mensagem para encerrar a conexão
    client_socket.sendto(b'sair', (SERVER_IP, SERVER_PORT))

    end_time = time.time()
    total_time = end_time - start_time

    if total_time > 0:
        download_speed = total_data / total_time  # Taxa de transferência em bytes/segundo
        print(f"Taxa de download: {download_speed / 1024:.2f} KB/s")

    client_socket.close()

# Iniciar a medição de download
medir_download()
