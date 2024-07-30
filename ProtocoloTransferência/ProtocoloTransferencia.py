# O programa não está exibindo a contagem dos pacotes perdidos, porém, caso necessário, o mesmo consegue detectar a perda e reenviar.

import socket
import threading
import struct
import hashlib
import time
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def get_local_ip():
    """
    Obtém o IP local da máquina. Tenta conectar a um servidor externo (Google DNS)
    para descobrir o IP local, caso não consiga, retorna '127.0.0.1'.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception as e:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def calculate_checksum(data):
    """
    Calcula o checksum MD5 dos dados fornecidos.
    """
    return hashlib.md5(data).hexdigest()

def format_number(num):
    """
    Formata um número com duas casas decimais e vírgulas para separação de milhares.
    """
    return "{:,.2f}".format(num)

def receive_file(peer_socket, buffer_size, report):
    """
    Função para receber um arquivo de um peer.
    Valida os pacotes recebidos através de checksum e contabiliza pacotes recebidos e perdidos.
    """
    expected_packet_number = 0
    received_packets = 0
    lost_packets = 0
    start_time = time.time()

    # Recebe o tamanho e o nome do arquivo
    filename_size_data = peer_socket.recv(4)
    filename_size = struct.unpack('!I', filename_size_data)[0]
    filename = peer_socket.recv(filename_size).decode()

    with open(filename, 'wb') as f:
        while True:
            # Recebe o cabeçalho do pacote
            header = peer_socket.recv(36)
            if not header:
                break
            packet_number, received_checksum = struct.unpack('!I32s', header)
            # Recebe os dados do pacote
            data = peer_socket.recv(buffer_size)
            if not data:
                break
            calculated_checksum = calculate_checksum(data).encode()

            # Verifica se o pacote é esperado e se o checksum corresponde
            if packet_number == expected_packet_number and received_checksum == calculated_checksum:
                f.write(data)
                received_packets += 1
                peer_socket.sendall(struct.pack('!I', packet_number))
                expected_packet_number += 1
            else:
                lost_packets += 1
                peer_socket.sendall(struct.pack('!I', expected_packet_number - 1))

    end_time = time.time()
    file_size = os.path.getsize(filename)
    duration = end_time - start_time
    speed = (file_size * 8) / duration

    # Preenche o relatório com os dados da transferência
    report['filename'] = filename
    report['file_size'] = file_size
    report['received_packets'] = received_packets
    report['lost_packets'] = lost_packets
    report['duration'] = duration
    report['speed'] = speed

    peer_socket.close()
    print_report(report)
    generate_pdf_report(report)
    print("Arquivo recebido com sucesso!")

def send_file(peer_socket, filename, buffer_size, report):
    """
    Função para enviar um arquivo para um peer.
    Calcula o checksum dos pacotes e valida o recebimento dos acks.
    """
    packet_number = 0
    sent_packets = 0
    lost_packets = 0
    start_time = time.time()

    # Envia o tamanho e o nome do arquivo
    filename_size = len(filename)
    peer_socket.sendall(struct.pack('!I', filename_size))
    peer_socket.sendall(filename.encode())

    with open(filename, 'rb') as f:
        while True:
            # Lê dados do arquivo
            data = f.read(buffer_size)
            if not data:
                break
            checksum = calculate_checksum(data).encode()
            header = struct.pack('!I32s', packet_number, checksum)
            while True:
                # Envia o cabeçalho e os dados
                peer_socket.sendall(header + data)
                ack = peer_socket.recv(4)
                ack_number = struct.unpack('!I', ack)[0]

                if ack_number == packet_number:
                    packet_number += 1
                    sent_packets += 1
                    break
                else:
                    lost_packets += 1
                    f.seek(-buffer_size, 1)

    end_time = time.time()
    file_size = os.path.getsize(filename)
    duration = end_time - start_time
    speed = (file_size * 8) / duration

    # Preenche o relatório com os dados da transferência
    report['filename'] = filename
    report['file_size'] = file_size
    report['sent_packets'] = sent_packets
    report['lost_packets'] = lost_packets
    report['duration'] = duration
    report['speed'] = speed

    peer_socket.close()
    print_report(report)
    generate_pdf_report(report)
    print("Arquivo enviado com sucesso!")

def handle_peer(peer_socket, buffer_size, filename=None):
    """
    Gerencia a conexão com o peer, decidindo se envia ou recebe um arquivo com base na presença do nome do arquivo.
    """
    report = {}
    if filename:
        send_file(peer_socket, filename, buffer_size, report)
    else:
        receive_file(peer_socket, buffer_size, report)

def start_peer(port, buffer_size, filename=None):
    """
    Inicia um peer no modo servidor, aguardando conexões na porta especificada.
    """
    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_socket.bind(('0.0.0.0', port))
    peer_socket.listen(1)
    
    print(f"Peer aguardando conexão na porta {port}...")

    conn, addr = peer_socket.accept()
    print(f"Conectado por {addr}")

    peer_thread = threading.Thread(target=handle_peer, args=(conn, buffer_size, filename))
    peer_thread.start()

def connect_to_peer(peer_ip, peer_port, buffer_size, filename=None):
    """
    Conecta a um peer remoto e gerencia a transferência de arquivos.
    """
    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_socket.connect((peer_ip, peer_port))
    handle_peer(peer_socket, buffer_size, filename)

def print_report(report):
    """
    Imprime o relatório da transferência de arquivos.
    """
    print("\nRelatório de Transferência:")
    print(f"Nome do arquivo: {report['filename']}")
    print(f"Tamanho do arquivo: {format_number(report['file_size'] / 1024)} KB")
    print(f"Pacotes enviados: {format_number(report.get('sent_packets', 0))}")
    print(f"Pacotes recebidos: {format_number(report.get('received_packets', 0))}")
    print(f"Pacotes perdidos: {format_number(report.get('lost_packets', 0))}")
    print(f"Velocidade de transmissão: {format_number(report['speed'])} bits/s")

def generate_pdf_report(report):
    """
    Gera um relatório da transferência de arquivos em formato PDF.
    """
    c = canvas.Canvas("relatorio_transferencia.pdf", pagesize=letter)
    c.drawString(100, 750, "Relatório de Transferência")
    c.drawString(100, 730, f"Nome do arquivo: {report['filename']}")
    c.drawString(100, 710, f"Tamanho do arquivo: {format_number(report['file_size'] / 1024)} KB")
    c.drawString(100, 690, f"Pacotes enviados: {format_number(report.get('sent_packets', 0))}")
    c.drawString(100, 670, f"Pacotes recebidos: {format_number(report.get('received_packets', 0))}")
    c.drawString(100, 650, f"Pacotes perdidos: {format_number(report.get('lost_packets', 0))}")
    c.drawString(100, 630, f"Velocidade de transmissão: {format_number(report['speed'])} bits/s")
    c.save()

if __name__ == "__main__":
    # Recebe o tamanho do buffer e o modo de operação (envio ou recebimento) do usuário
    buffer_size = input("Enter buffer size: ")
    buffer_size = int(buffer_size)
    mode = input("Select send or receive mode: ")
    peer_port = 5001
    peer_ip = '0.0.0.0'
    if mode == 'send':
        # Configura o peer para enviar arquivos
        peer_ip = input("Enter IP address of receiver: ")
        filename = input("Enter filename: ")
        connect_to_peer(peer_ip, peer_port, buffer_size, filename)
    else:
        # Configura o peer para receber arquivos
        ip = get_local_ip()
        print(f"{ip} ")
        start_peer(peer_port, buffer_size)
