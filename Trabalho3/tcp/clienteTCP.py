import socket
import time

HOST = '192.168.15.61'  
PORT = 5000            

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
    while True:  
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print(f"Conectado ao servidor {HOST}:{PORT}")

            # FASE 1: Enviar múltiplos pacotes de 500 bytes por 20 segundos 
            data_to_send = generate_test_string() 
            packet_size = 500
            total_bytes_sent = 0
            packet_count = 0
            lost_packets = 0
            start_time = time.time()

            # Limitar o upload a 20 segundos
            while time.time() - start_time < 20:
                try:
                    s.sendall(data_to_send)
                    total_bytes_sent += packet_size
                    packet_count += 1
                except socket.error:
                    lost_packets += 1

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
            print(f"Bytes enviados: {total_bytes_sent:,} bytes")
            print(f"Pacotes perdidos no upload: {lost_packets:,}\n")

            s.sendall(b'UPLOAD_COMPLETE')

            # FASE 2: Receber os dados por 20 segundos 
            total_bytes_received = 0
            packet_count = 0
            lost_packets = 0
            start_time = time.time()

            # Limitar o download a 20 segundos
            while time.time() - start_time < 20:
                try:
                    data = s.recv(packet_size)
                    if not data:
                        lost_packets += 1
                        continue
                    total_bytes_received += len(data)
                    packet_count += 1
                except socket.error:
                    lost_packets += 1

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
            print(f"Pacotes perdidos no download: {lost_packets:,}")

            confirmation = s.recv(1024)
            if confirmation == b'UPLOAD_COMPLETE':
                print("Upload finalizado pelo servidor. Encerrando a conexão.")
            break 

if __name__ == "__main__":
    start_tcp_client()