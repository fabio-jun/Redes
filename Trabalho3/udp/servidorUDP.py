import socket
import time

# Configurações do servidor
HOST = '0.0.0.0'  # Endereço IP do servidor
PORT = 65432      # Porta do servidor

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

def start_udp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        print(f"Servidor ouvindo na porta {PORT}...")

        while True:
            # FASE 1: Receber pacotes do cliente por 20 segundos
            print("Aguardando dados...\n")
            total_bytes_received = 0
            total_packets_received = 0
            start_time = time.time()

            while time.time() - start_time < 20:  # Receber pacotes por 20 segundos
                try:
                    data, addr = s.recvfrom(500)  # Recebe 500 bytes por vez
                    if b'UPLOAD_COMPLETE' in data:
                        print("Upload completo")
                        break
                    total_bytes_received += len(data)
                    total_packets_received += 1
                except socket.timeout:
                    break  # Caso não receba mais pacotes, saia do loop

            end_time = time.time()

            # Calcular tempo e taxa de upload (do ponto de vista do servidor, é download)
            upload_time = end_time - start_time
            print(f"Tempo de Download: {upload_time} segundos")
            upload_bps = (total_bytes_received * 8) / upload_time  # bits por segundo
            upload_pps = total_packets_received / upload_time  # pacotes por segundo
            print(f"Taxa de Download:\n{format_all_speeds(upload_bps)}")
            print(f"Pacotes por segundo: {upload_pps:,.2f}")
            print(f"Pacotes recebidos: {total_packets_received:,}")
            print(f"Bytes recebidos: {total_bytes_received:,} bytes\n")

            # FASE 2: Enviar pacotes de volta ao cliente por 20 segundos (Download para o cliente)
            try:
                data_to_send = generate_test_string()
                total_bytes_sent = 0
                total_packets_sent = 0
                start_time = time.time()

                while time.time() - start_time < 20:  # Enviar pacotes por 20 segundos
                    s.sendto(data_to_send, addr)
                    total_bytes_sent += 500
                    total_packets_sent += 1

                end_time = time.time()

                # Calcular tempo e taxa de download (do ponto de vista do servidor, é upload)
                download_time = end_time - start_time
                print(f"Tempo de Upload: {download_time} segundos")
                download_bps = (total_bytes_sent * 8) / download_time  # bits por segundo
                download_pps = total_packets_sent / download_time  # pacotes por segundo
                print(f"Taxa de Upload:\n{format_all_speeds(download_bps)}")
                print(f"Pacotes por segundo: {download_pps:,.2f}")
                print(f"Pacotes enviados: {total_packets_sent:,}")
                print(f"Bytes enviados: {total_bytes_sent:,} bytes\n")

            except socket.error as e:
                print(f"Erro ao enviar dados para o cliente: {e}\n")

if __name__ == "__main__":
    start_udp_server()
