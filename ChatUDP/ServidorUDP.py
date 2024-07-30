import socket
import threading

# Configurações do servidor
SERVER_IP = '192.168.0.211'  # Ou o IP específico do servidor
SERVER_PORT = 12345
BUFFER_SIZE = 1500  # Tamanho máximo do pacote

# Criação do socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

print(f"Servidor ouvindo em {SERVER_IP}:{SERVER_PORT}")

def receber_mensagens():
    while True:
        data, client_address = server_socket.recvfrom(BUFFER_SIZE)
        message = data.decode('utf-8')
        print(f"Recebido de {client_address}: {message}")
        if message.lower() == 'sair':
            print("Cliente encerrou a conexão.")
            break

def enviar_mensagens():
    while True:
        message = input("Digite a mensagem para enviar: ")
        server_socket.sendto(message.encode('utf-8'), (SERVER_IP, SERVER_PORT))
        if message.lower() == 'sair':
            print("Encerrando o servidor.")
            break

# Criação das threads para receber e enviar mensagens
thread_receber = threading.Thread(target=receber_mensagens)
thread_enviar = threading.Thread(target=enviar_mensagens)

thread_receber.start()
thread_enviar.start()

thread_receber.join()
thread_enviar.join()

server_socket.close()
