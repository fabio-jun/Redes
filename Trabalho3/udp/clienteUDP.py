import socket
import time

# Configurações do cliente
HOST = '192.168.0.120'  # Endereço IP do servidor
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
    # Gerar string de 500 bytes contendo "teste de rede *2024*"
    base_string = "teste de rede *2024*"
    repeated_string = (base_string * (500 // len(base_string)))[:500]
    return repeated_string.encode('utf-8')  # Converter para bytes

def start_udp_client():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        print(f"Conectado ao servidor {HOST}:{PORT}\n")

        # FASE 1: Enviar pacotes de 500 bytes continuamente por 20 segundos (UPLOAD)
        data_to_send = generate_test_string()
        packet_size = 500
        total_bytes_sent = 0
        total_packets_sent = 0
        start_time = time.time()

        while time.time() - start_time < 20:  # Enviar pacotes por 20 segundos
            s.sendto(data_to_send, (HOST, PORT))
            total_bytes_sent += packet_size
            total_packets_sent += 1

        end_time = time.time()

        upload_time = end_time - start_time
        print(f"Tempo de upload: {upload_time} segundos")
        upload_bps = (total_bytes_sent * 8) / upload_time
        upload_pps = total_packets_sent / upload_time
        print(f"Taxa de Upload:\n{format_all_speeds(upload_bps)}")
        print(f"Pacotes por segundo: {upload_pps:,.2f}")
        print(f"Pacotes enviados: {total_packets_sent:,}")
        print(f"Bytes enviados: {total_bytes_sent:,} bytes\n")

        # Enviar o total de pacotes enviados para o servidor
        total_packets_sent_message = str(total_packets_sent).encode('utf-8')
        s.sendto(total_packets_sent_message, (HOST, PORT))

        # Enviar uma notificação ao servidor indicando que o upload terminou
        s.sendto(b'UPLOAD_COMPLETE', (HOST, PORT))

        # FASE 2: Receber os dados por 20 segundos (DOWNLOAD)
        total_bytes_received = 0
        total_packets_received = 0
        start_time = time.time()

        # Receber pacotes de dados por 20 segundos
        while time.time() - start_time < 20:
            try:
                s.settimeout(5)  # Timeout de 5 segundos para dar mais tempo ao cliente
                data, _ = s.recvfrom(packet_size)
                total_bytes_received += len(data)
                total_packets_received += 1
            except socket.timeout:
                break  # Se não houver mais pacotes, interrompe o loop

        # Agora, esperar pela mensagem "END_OF_DATA" para saber que os pacotes de dados terminaram
        while True:
            data, _ = s.recvfrom(1024)
            if data == b'END_OF_DATA':
                break

        # Receber o número total de pacotes enviados pelo servidor
        total_packets_sent_by_server = 0
        try:
            data, _ = s.recvfrom(1024)  # Receber o número de pacotes enviados pelo servidor
            total_packets_sent_by_server = int(data.decode('utf-8'))
        except socket.timeout:
            print("Erro ao receber o número de pacotes enviados pelo servidor.")

        end_time = time.time()

        download_time = end_time - start_time
        print(f"Tempo de download: {download_time} segundos")
        download_bps = (total_bytes_received * 8) / download_time
        download_pps = total_packets_received / download_time
        print(f"Taxa de Download:\n{format_all_speeds(download_bps)}")
        print(f"Pacotes por segundo: {download_pps:,.2f}")
        print(f"Pacotes recebidos: {total_packets_received:,}")
        print(f"Bytes recebidos: {total_bytes_received:,} bytes")

        # Calcular pacotes perdidos durante o download
        if total_packets_sent_by_server > 0:
            lost_packets_download = total_packets_sent_by_server - total_packets_received
            print(f"Pacotes perdidos no download: {lost_packets_download}\n")
        else:
            print("Não foi possível calcular os pacotes perdidos, pois o número de pacotes enviados pelo servidor não foi recebido.")

        # Aguardar antes de realizar nova transferência
        input("Pressione Enter para realizar uma nova transferência...")

if __name__ == "__main__":
    start_udp_client()
