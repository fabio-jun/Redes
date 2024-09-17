import socket
import time

# Configurações do cliente
HOST = '191.52.78.213'  # Endereço IP do servidor
PORT = 65432            # Porta do servidor

def format_all_speeds(bps):
    gbps = bps / 10**9
    mbps = bps / 10**6
    kbps = bps / 10**3
    return (
        f"{gbps:,.2f} Gbps\n"
        f"{mbps:,.2f} Mbps\n"
        f"{kbps:,.2f} Kbps\n"
        f"{bps:,.2f} bps"
    )

def generate_test_string():
    base_string = "teste de rede *2024*"
    repeated_string = (base_string * (500 // len(base_string)))[:500]
    return repeated_string.encode('utf-8')  # Converter para bytes

def start_tcp_client():
    while True:  # Manter o cliente em execução para realizar múltiplas transferências
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print(f"Conectado ao servidor {HOST}:{PORT}")

            # FASE 1: Enviar múltiplos pacotes de 500 bytes por 20 segundos (UPLOAD)
            data_to_send = generate_test_string() * 2000
            packet_size = 500
            total_bytes_sent = 0
            packet_count = 0
            start_time = time.time()
            while time.time() - start_time < 20:  # Loop de upload por 20 segundos
                for i in range(0, len(data_to_send), packet_size):
                    s.sendall(data_to_send[i:i+packet_size])
                    total_bytes_sent += packet_size
                    packet_count += 1
            end_time = time.time()

            upload_time = end_time - start_time
            print(f"Tempo de upload: {upload_time} segundos")
            if upload_time == 0:
                upload_time = 1e-9  # Prevenir divisão por zero

            upload_bps = (total_bytes_sent * 8) / upload_time
            upload_pps = packet_count / upload_time
            print(f"Taxa de Upload:\n{format_all_speeds(upload_bps)}")
            print(f"Pacotes por segundo: {upload_pps:,.2f}")
            print(f"Pacotes enviados: {packet_count:,}")
            print(f"Bytes enviados: {total_bytes_sent:,} bytes\n")

            # Enviar uma notificação ao servidor indicando que o upload terminou
            s.sendall(b'UPLOAD_COMPLETE')

            # FASE 2: Receber os dados por 20 segundos (DOWNLOAD)
            total_bytes_received = 0
            packet_count = 0
            start_time = time.time()
            while time.time() - start_time < 20:  # Loop de download por 20 segundos
                data = s.recv(packet_size)
                if not data:
                    break
                total_bytes_received += len(data)
                packet_count += 1
            end_time = time.time()

            download_time = end_time - start_time
            print(f"Tempo de download: {download_time} segundos")
            if download_time == 0:
                download_time = 1e-9  # Prevenir divisão por zero

            download_bps = (total_bytes_received * 8) / download_time
            download_pps = packet_count / download_time
            print(f"Taxa de Download:\n{format_all_speeds(download_bps)}")
            print(f"Pacotes por segundo: {download_pps:,.2f}")
            print(f"Pacotes recebidos: {packet_count:,}")
            print(f"Bytes recebidos: {total_bytes_received:,} bytes")

            # Aguardar antes de realizar nova transferência
            input("Pressione Enter para realizar uma nova transferência...")

if __name__ == "__main__":
    start_tcp_client()
