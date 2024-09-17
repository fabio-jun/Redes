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

def handle_client(conn):
    """Função para lidar com a conexão de um cliente"""
    with conn:
        print(f"Conectado a {conn.getpeername()}")

        # FASE 1: Receber múltiplos pacotes do cliente (esperando 1 MB, 2000 pacotes)
        start_time = time.time()
        data_received = 0
        packet_count = 0
        while True:
            data = conn.recv(500)  # Recebe 500 bytes por vez
            if b'UPLOAD_COMPLETE' in data:
                print("Upload completo")
                break
            if not data:
                break
            data_received += len(data)
            packet_count += 1
        end_time = time.time()

        upload_time = end_time - start_time
        print(f"Tempo de upload: {upload_time} segundos")
        if upload_time == 0:
            upload_time = 1e-9  # Prevenir divisão por zero

        upload_bps = (data_received * 8) / upload_time  # bits por segundo
        upload_pps = packet_count / upload_time  # pacotes por segundo
        print(f"Taxa de Upload:\n{format_all_speeds(upload_bps)}")
        print(f"Pacotes por segundo: {upload_pps:,.2f}")
        print(f"Pacotes recebidos: {packet_count:,}")
        print(f"Bytes recebidos: {data_received:,} bytes")

        # FASE 2: Enviar dados ao cliente (fase de download)
        try:
            data_to_send = generate_test_string() * 2000  # Enviar 2000 pacotes de 500 bytes (1 MB)
            packet_size = 500
            total_bytes_sent = 0
            packet_count = 0
            start_time = time.time()

            while time.time() - start_time < 20:  # Limitar a transferência para 20 segundos
                for i in range(0, len(data_to_send), packet_size):
                    try:
                        conn.sendall(data_to_send[i:i+packet_size])
                        total_bytes_sent += packet_size
                        packet_count += 1
                    except socket.error as e:
                        print(f"Erro ao enviar dados para o cliente: {e}")
                        break
            end_time = time.time()

            download_time = end_time - start_time
            print(f"Tempo de download: {download_time} segundos")
            if download_time == 0:
                download_time = 1e-9  # Prevenir divisão por zero

            download_bps = (total_bytes_sent * 8) / download_time  # bits por segundo
            download_pps = packet_count / download_time  # pacotes por segundo
            print(f"Taxa de Download:\n{format_all_speeds(download_bps)}")
            print(f"Pacotes por segundo: {download_pps:,.2f}")
            print(f"Pacotes enviados: {packet_count:,}")
            print(f"Bytes enviados: {total_bytes_sent:,} bytes")
        except socket.error as e:
            print(f"Erro ao enviar dados para o cliente: {e}")

def start_tcp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor ouvindo na porta {PORT}...")

        while True:
            conn, addr = s.accept()  # Aceitar conexões indefinidamente
            print(f"Nova conexão de {addr}")
            handle_client(conn)  # Lida com a conexão do cliente

if __name__ == "__main__":
    start_tcp_server()
