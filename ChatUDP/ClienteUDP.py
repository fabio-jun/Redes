import socket
import threading

SERVER_IP = '192.168.0.211'  # IP do servidor
SERVER_PORT = 12345  # Porta do servidor
BUFFER_SIZE = 1500  # Tamanho limite do buffer de pacote

# Definição do socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Variável global para controle do encerramento das threads
encerrar = False

def receber_mensagens():
    """
    Função para receber mensagens do servidor. 
    Fica em loop até que a variável 'encerrar' seja definida como True.
    """
    global encerrar
    while not encerrar:
        try:
            # Recebe dados do servidor
            data, _ = client_socket.recvfrom(BUFFER_SIZE)
            message = data.decode('utf-8')
            print(f"Mensagem recebida do servidor: {message}")
            if message.lower() == 'sair':
                # Se a mensagem recebida for 'sair', encerra a conexão
                print("Servidor encerrou a conexão.")
                encerrar = True
                break
        except OSError:
            break

def enviar_mensagens():
    """
    Função para enviar mensagens ao servidor.
    Fica em loop até que a variável 'encerrar' seja definida como True.
    """
    global encerrar
    while not encerrar:
        # Recebe entrada do usuário para enviar ao servidor
        message = input("Digite a mensagem para enviar ao servidor: ")
        client_socket.sendto(message.encode('utf-8'), (SERVER_IP, SERVER_PORT))
        if message.lower() == 'sair':
            # Se a mensagem for 'sair', encerra o cliente
            print("Encerrando o cliente.")
            encerrar = True
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

# Fecha o socket do cliente
client_socket.close()
