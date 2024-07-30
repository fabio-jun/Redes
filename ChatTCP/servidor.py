import socket # Módulo usado para criar conexões de rede
import threading # Permite a execução de threads, a fim de realizar operações simultaneamente


clients = [] # Lista para armazenamento dos sockets de clientes conectados 

def broadcast(message):
    """
    Envia uma mensagem para todos os clientes conectados.

    Args:
        message(bytes): Mensagem a ser enviada para todos os clientes.
    """
    for client in clients:
        try: # Itera sobre ps cliente conectados
            client.send(message)
        except:
            clients.remove(client)

def handle_client(client_socket):
    """
    Gerencia a comunicação com um único cliente.

    Args:
        client_socket (socket.socket): O socket do cliente conectado.

    Recebe mensagens do cliente e as retransmite para todos os outros clientes.
    Caso a conexão seja encerrada, o cliente é removido da lista.
    """
    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                print(f"Mensagem recebida: {message.decode('utf-8')}")
                broadcast(message) # Retransmite a mensagens aos demais clientes
            else:
                clients.remove(client_socket)
                break
        except:
            clients.remove(client_socket)
            break

def send_messages():
    """
    Permite que o servidor envie mensagens para todos os clientes conectados.

    Lê mensagens do console e as envia para todos os clientes.
    """
    while True:
        message = input("Servidor: ")
        broadcast(message.encode('utf-8'))

def start_server(ip, port):
    """
    Inicia o servidor, aceita conexões de clientes e inicia threads para gerenciar cada cliente.

    Args:
        ip (str): O endereço IP do servidor.
        port (int): A porta do servidor.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Criação de um socket de servidor
    server_socket.bind((ip, port)) # Associa o socket a um endereço IP e porta especificadas
    server_socket.listen(5) # Escuta até 5 conexões de entrada
    print(f"Servidor iniciado em {ip}:{port}")

    threading.Thread(target=send_messages).start() # Inicia uma thread para a função 'send_messages'

    while True:
        client_socket, client_address = server_socket.accept() # Aceita novas conexões
        print(f"Conexão estabelecida com {client_address}")
        clients.append(client_socket) # Adiciona o socket do cliente à lista
        threading.Thread(target=handle_client, args=(client_socket,)).start() #  Inicia uma nova thread para a função

if __name__ == "__main__":
    """
    Bloco principal que solicita ao usuário o endereço IP e a porta do servidor,
    e então inicia o servidor com esses valores.
    """
    ip = input("Digite o endereço IP do servidor: ")
    port = int(input("Digite a porta do servidor: "))
    start_server(ip, port)
