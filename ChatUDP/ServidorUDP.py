import socket
import threading

SERVER_IP = '192.168.0.211'  # IP do servidor
SERVER_PORT = 12345  # Porta do servidor
BUFFER_SIZE = 1500  # Tamanho limite do buffer de pacote

# Criação do socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

print(f"Servidor ouvindo em {SERVER_IP}:{SERVER_PORT}")

def receber_mensagens():
    """
    Função para receber mensagens dos clientes.
    Fica em loop aguardando mensagens até que receba 'sair'.
    """
    while True:
        # Recebe dados do cliente
        data, client_address = server_socket.recvfrom(BUFFER_SIZE)
        message = data.decode('utf-8')
        print(f"Recebido de {client_address}: {message}")
        if message.lower() == 'sair':
            # Se a mensagem for 'sair', encerra a conexão
            print("Cliente encerrou a conexão.")
            break

def enviar_mensagens():
    """
    Função para enviar mensagens aos clientes.
    Fica em loop até que a mensagem 'sair' seja enviada.
    """
    while True:
        # Recebe entrada do usuário para enviar aos clientes
        message = input("Digite a mensagem a ser enviada: ")
        server_socket.sendto(message.encode('utf-8'), (SERVER_IP, SERVER_PORT))
        if message.lower() == 'sair':
            # Se a mensagem for 'sair', encerra o servidor
            print("Encerrando o servidor.")
            break

# Criação das threads para recebimento e envio de mensagens
thread_receber = threading.Thread(target=receber_mensagens)
thread_enviar = threading.Thread(target=enviar_mensagens)

# Inicia as threads
thread_receber.start()
thread_enviar.start()

# Espera que as threads terminem
thread_receber.join()
thread_enviar.join()

# Fecha o socket do servidor
server_socket.close()
