import socket  # Biblioteca nativa para conexões de rede (sockets TCP/UDP)
import time    # Biblioteca para medir o tempo de execução do script

# Importa o ThreadPoolExecutor para gerenciar o Multithreading (várias tarefas ao mesmo tempo)
from concurrent.futures import ThreadPoolExecutor

# Lista global que armazenará apenas os dados das portas que forem encontradas ABERTAS
resultados_finais = []

def get_service_name(port):
    """
    Função que tenta identificar o nome padrão do serviço rodando na porta.
    Exemplo: 80 -> HTTP, 22 -> SSH, 443 -> HTTPS
    """
    try:
        # socket.getservbyport tenta traduzir o número da porta e o protocolo ('tcp') no nome do serviço
        return socket.getservbyport(port, 'tcp').upper()
    except (OSError, OverflowError):
        # Se a porta não tiver um serviço padrão registrado no sistema, retorna "Desconhecido"
        return "Desconhecido"

def get_banner(s):
    """
    Função para capturar o "Banner" (a mensagem de boas-vindas do software do servidor).
    Recebe o objeto do socket ('s') já conectado.
    """
    try:
        # Envia uma mensagem genérica simulando uma quebra de linha. 
        # Isso força alguns servidores (como HTTP, FTP, SSH) a responderem algo de volta.
        s.send(b'Hello\r\n')
        
        # Aguarda e lê os primeiros 1024 bytes enviados pelo servidor.
        # .decode('utf-8', errors='ignore') transforma os bytes recebidos em texto legível.
        banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
        
        # Remove quebras de linha (\n ou \r) para o texto não quebrar o layout do terminal/arquivo,
        # e limita o tamanho do banner em 50 caracteres para ficar organizado.
        return banner.replace('\n', ' ').replace('\r', '')[:50] 
    except Exception:
        # Se o servidor não responder nada ou fechar a conexão, define como sem banner
        return "Sem banner disponível"

def check_port(host, port):
    """
    Função principal de teste. Ela será disparada por várias Threads simultaneamente.
    Verifica se a porta está aberta. Se sim, coleta o serviço e o banner.
    """
    try:
        # Cria um novo socket IPv4 (AF_INET) usando o protocolo TCP (SOCK_STREAM)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Define um tempo limite de 1.5 segundos para a tentativa de conexão.
        # Um tempo muito baixo pode ignorar portas abertas em conexões lentas.
        s.settimeout(1.5)  
        
        # Tenta se conectar ao host e porta. 
        # connect_ex não joga uma exceção se falhar; ele apenas retorna um código (0 = Sucesso)
        result = s.connect_ex((host, port))
        
        # Se o resultado for 0, significa que a conexão foi aceita (Porta Aberta)
        if result == 0:
            servico = get_service_name(port) # Descobre o nome do serviço (ex: SSH)
            banner = get_banner(s)           # Tenta capturar o banner do serviço aberto
            s.close()                        # Fecha o socket após coletar os dados
            
            # Retorna um dicionário estruturado com as informações coletadas
            return {"porta": port, "status": "ABERTA", "servico": servico, "banner": banner}
        
        # Se o resultado não for 0, a porta está fechada ou filtrada por firewall
        s.close()
        return {"porta": port, "status": "FECHADA", "servico": "", "banner": ""}
    except socket.error:
        # Captura erros inesperados de rede durante a criação do socket
        return {"porta": port, "status": "ERRO", "servico": "", "banner": ""}

# ==========================================
# INTERAÇÃO COM O USUÁRIO (MENU)
# ==========================================

# 1. Entrada do Host (IP ou Domínio)
host = input("Digite o IP ou domínio para escanear (ex: 192.168.1.1): ")

# 2. Menu de Opções visual
print("\n" + "-"*40)
print("       ESCOLHA O TIPO DE SCAN")
print("-"*40)
print("[1] Escanear uma Porta Única")
print("[2] Escanear um Range de Portas")
print("-"*40)
opcao = input("Digite a opção desejada (1 ou 2): ")

# 3. Tratamento da escolha do usuário para definir o início e o fim da varredura
if opcao == "1":
    porta_unica = int(input("Digite o número da porta (ex: 80): "))
    start_port = porta_unica # Início e fim serão iguais
    end_port = porta_unica
elif opcao == "2":
    port_range = input("Digite o range de portas (ex: 1-100): ")
    # Divide a string digitada no "-" e transforma em números inteiros (ex: "1" e "100")
    start_port, end_port = map(int, port_range.split("-"))
else:
    print("Opção inválida! Encerrando o programa.")
    exit() # Encerra o script se a opção do menu for inválida

# Pergunta ao usuário se ele deseja exportar os resultados para um relatório
salvar = input("\nDeseja salvar o resultado em um arquivo .txt? (s/n): ").strip().lower()
salvar_arquivo = salvar == 's' # Retorna True se o usuário digitou 's'

# Contadores utilizados para exibir as estatísticas no resumo final
open_ports = 0
closed_ports = 0

print(f"\nIniciando varredura em {host} (com Multithreading)...")
print(f"Alvo: {host} | Portas: {start_port} até {end_port}\n")

# 4. Medição do tempo de início do escaneamento
start_time = time.time()

# Cria uma lista contendo todas as portas do intervalo selecionado. Ex: list(range(1, 5)) gera [1, 2, 3, 4]
portas_para_escanear = list(range(start_port, end_port + 1))

# ==========================================
# EXECUÇÃO DO MULTITHREADING
# ==========================================

# Criamos o gerenciador de threads. max_workers=100 significa que o Python executará
# até 100 conexões de portas ao mesmo tempo, dividindo o trabalho de forma paralela.
with ThreadPoolExecutor(max_workers=100) as executor:
    
    # executor.map envia a lista de portas para a função check_port.
    # O comando 'lambda p: check_port(host, p)' serve para passar o 'host' fixo junto com cada porta 'p'.
    # O resultado será um iterador contendo as respostas de todas as portas à medida que terminam.
    resultados = executor.map(lambda p: check_port(host, p), portas_para_escanear)
    
    # Fazemos um loop para processar as respostas que as Threads coletaram
    for res in resultados:
        port = res["porta"]
        
        if res["status"] == "ABERTA":
            # Formata a exibição no terminal usando espaçamentos fixos (ex: :<5, :<12) para alinhar as colunas
            print(f"[+] Porta {port:<5} | Status: ABERTA  | Serviço: {res['servico']:<12} | Banner: {res['banner']}")
            resultados_finais.append(res)  # Salva o dicionário na nossa lista global de portas abertas
            open_ports += 1                # Incrementa o contador de abertas
        else:
            closed_ports += 1              # Incrementa o contador de fechadas
            # Para evitar poluir a tela com milhares de linhas fechadas, só mostramos se for o scan de 1 porta única.
            if start_port == end_port:
                print(f"[-] Porta {port:<5} | Status: FECHADA")

# 6. Medição do tempo de término e cálculo da duração total do scan
total_time = time.time() - start_time

# 7. Exibição do resumo final estruturado no terminal
resumo = f"""
{"="*50}
                 RESUMO DO SCAN
{"="*50}
Alvo:            {host}
Portas abertas:  {open_ports}
Portas fechadas: {closed_ports}
Tempo total:     {total_time:.2f} segundos
{"="*50}
"""
print(resumo)

# ==========================================
# SALVAMENTO DO ARQUIVO RELATÓRIO
# ==========================================

# Verifica se o usuário pediu para salvar e se de fato encontramos alguma porta aberta
if salvar_arquivo and open_ports > 0:
    # Substitui pontos do IP por sublinhados para gerar o nome do arquivo (ex: scan_192_168_1_1.txt)
    nome_arquivo = f"scan_{host.replace('.', '_')}.txt"
    try:
        # Abre o arquivo em modo de escrita ('w') com codificação UTF-8 para evitar erros de acentos
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write(f"Relatório de Scan - {host}\n")
            f.write(f"Tempo total: {total_time:.2f} segundos\n")
            f.write("-" * 60 + "\n")
            # Cabeçalho da tabela de dados do arquivo txt
            f.write(f"{'PORTA':<8} | {'SERVIÇO':<15} | {'BANNER':<30}\n")
            f.write("-" * 60 + "\n")
            
            # Percorre a nossa lista global e escreve cada linha no arquivo de texto
            for item in resultados_finais:
                f.write(f"{item['porta']:<8} | {item['servico']:<15} | {item['banner']:<30}\n")
        
        print(f"[✓] Resultados salvos com sucesso em: {nome_arquivo}")
    except Exception as e:
        print(f"[X] Erro ao salvar o arquivo: {e}")
        
elif salvar_arquivo and open_ports == 0:
    # Mensagem de aviso caso o usuário quisesse salvar, mas o alvo não tinha portas abertas
    print("[!] Nenhuma porta aberta encontrada. Arquivo não foi gerado.")