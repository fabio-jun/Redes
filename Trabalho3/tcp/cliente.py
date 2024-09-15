import socket
import threading
import time

def start_client(ip, port):
    """
    Cliente TCP que envia uma quantidade fixa de dados para o servidor para medir a taxa de download.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))

    total_data = 0
    start_time = time.time()

    # Envia uma quantidade de dados durante 10 segundos
    while time.time() - start_time < 10:
        message = b'X' * 4096  # Envia blocos de 4096 bytes
        client_socket.send(message)
        total_data += len(message)

    client_socket.close()

    end_time = time.time()
    total_time = end_time - start_time
    if total_time > 0:
        download_speed = total_data / total_time  # Taxa de transferência em bytes/segundo
        print(f"Taxa de download: {download_speed / 1024:.2f} KB/s")

if __name__ == "__main__":
    ip = input("Digite o endereço IP do servidor: ")
    port = int(input("Digite a porta do servidor: "))
    start_client(ip, port)
