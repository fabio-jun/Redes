import socket
import threading

# Configurações do cliente
SERVER_IP = '192.168.0.211'  # IP do servidor
SERVER_PORT = 12345
BUFFER_SIZE = 1500  # Tamanho máximo do pacote

# Criação do socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Variável global para controlar o encerramento das threads
encerrar = False

def receber_mensagens():
    global encerrar
    while not encerrar:
        try:
            data, _ = client_socket.recvfrom(BUFFER_SIZE)
            message = data.decode('utf-8')
            print(f"Recebido do servidor: {message}")
            if message.lower() == 'sair':
                print("Servidor encerrou a conexão.")
                encerrar = True
                break
        except OSError:
            break

def enviar_mensagens():
    global encerrar
    while not encerrar:
        message = input("Digite a mensagem para enviar ao servidor: ")
        client_socket.sendto(message.encode('utf-8'), (SERVER_IP, SERVER_PORT))
        if message.lower() == 'sair':
            print("Encerrando o cliente.")
            encerrar = True
            break

# Criação das threads para receber e enviar mensagens
thread_receber = threading.Thread(target=receber_mensagens)
thread_enviar = threading.Thread(target=enviar_mensagens)

thread_receber.start()
thread_enviar.start()

thread_receber.join()
thread_enviar.join()

client_socket.close()
