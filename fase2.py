import socket
import time

def check_port(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)  # Mantive em 1 segundo para ser mais rápido
        result = s.connect_ex((host, port))
        s.close()
        return result == 0
    except socket.error:
        return False

# 1. Entrada do Host (IP ou Domínio)
host = input("Digite o IP ou domínio para escanear (ex: 192.168.1.1): ")

# 2. Menu de Opções
print("\n" + "-"*30)
print("      ESCOLHA O TIPO DE SCAN")
print("-"*30)
print("[1] Escanear uma Porta Única")
print("[2] Escanear um Range de Portas")
print("-"*30)
opcao = input("Digite a opção desejada (1 ou 2): ")

# 3. Tratamento da escolha do usuário
if opcao == "1":
    porta_unica = int(input("Digite o número da porta (ex: 80): "))
    start_port = porta_unica
    end_port = porta_unica
elif opcao == "2":
    port_range = input("Digite o range de portas (ex: 1-100): ")
    start_port, end_port = map(int, port_range.split("-"))
else:
    print("Opção inválida! Encerrando o programa.")
    exit()

# Contadores para o resumo final
open_ports = 0
closed_ports = 0

print(f"\nIniciando varredura em {host} da porta {start_port} até {end_port}...\n")

# 4. Medição do tempo de início
start_time = time.time()

# 5. Loop para varrer as portas (funciona para ambas as opções)
for port in range(start_port, end_port + 1):
    if check_port(host, port):
        print(f"[+] Porta {port}: ABERTA")
        open_ports += 1
    else:
        # Se for porta única, avisa que está fechada. Se for range, fica oculto para não poluir
        if start_port == end_port:
            print(f"[-] Porta {port}: FECHADA")
        closed_ports += 1

# 6. Medição do tempo de término
end_time = time.time()
total_time = end_time - start_time

# 7. Exibição do resumo final
print("\n" + "="*30)
print("        RESUMO DO SCAN")
print("="*30)
print(f"Portas abertas:  {open_ports}")
print(f"Portas fechadas: {closed_ports}")
print(f"Tempo total:     {total_time:.2f} segundos")
print("="*30)