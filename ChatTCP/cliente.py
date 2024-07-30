import socket # Módulo usado para criar conexões de rede
import threading # Permite a execução de threads, a fim de realizar operações simultaneamente

def receive_messages(client_socket):
    """
    Lida com o recebimento das mensagens do servidor e as imprime na tela

    Args:
        client_socket (socket.socket): O socket do cliente.

    Essa função roda em um trread separado, a fim de receber e printar continuamente as mensagens recebidas a partir do servidor
    """
    while True:
        try:
            message = client_socket.recv(1024) # Mensagens são recebidas em blocos de 1024 bytes
            if message:
                print(f"Mensagem recebida: {message.decode('utf-8')}") # Decodificação de bytes para string
            else:
                break
        except:
            break

def start_client(ip, port):
    """
    Inicia o cliente, conecta-se ao servidor e permite a troca de mensagens.

    Args:
        ip (str): O endereço IP do servidor.
        port (int): A porta do servidor.

    Essa função configura o socket do cliente, conecta-se ao servidor, inicia uma thread para o recebimento de mensagens
    e permite ao usuário enviar mensagens para o servidor
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Criação de socket TCP/IP
    client_socket.connect((ip, port)) # Conecta o socket ao servidor utilizando o endereço IP e a porta fornecidas

    threading.Thread(target=receive_messages, args=(client_socket,)).start() # Inicia uma nova thread para a função, passando o socket do cliente como argumento 

    while True: # Loop para ler mensagens e enviá-las ao servidor 
        message = input()
        client_socket.send(message.encode('utf-8'))

if __name__ == "__main__":
    """
    Bloco principal que solicita ao usuário o endereço IP, a porta do servidor,
    e então inicia o cliente com esses valores.
    """
    ip = input("Digite o endereço IP do servidor: ")
    port = int(input("Digite a porta do servidor: "))
    start_client(ip, port)