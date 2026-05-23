# 🚀 Multithreaded TCP Port Scanner em Python

Este é um escaner de portas TCP desenvolvido em Python que utiliza conceitos de **Multithreading** para realizar varreduras rápidas e eficientes em endereços IP ou domínios. O projeto foi desenvolvido com fins puramente acadêmicos para compreender a integração entre arquitetura de software (concorrência) e protocolos de redes de computadores.

---

## 📌 Funcionalidades

* **Varredura Concorrente:** Capaz de testar até 100 portas simultaneamente utilizando `ThreadPoolExecutor`.
* **Identificação de Serviços:** Consulta interna para traduzir o número da porta no seu respectivo serviço padrão (ex: 80/HTTP, 22/SSH).
* **Captura de Banner (Banner Grabbing):** Envia uma requisição preliminar para tentar capturar a versão do software que está rodando na porta aberta.
* **Filtro Dinâmico:** Exibe um relatório detalhado apenas das portas abertas, evitando poluição visual no terminal.
* **Exportação de Relatórios:** Opção para salvar os resultados estruturados em um arquivo `.txt` automaticamente nomeado com o IP do alvo.

---

## 🛠️ Tecnologias Utilizadas

O projeto foi construído utilizando apenas bibliotecas nativas do Python, sem a necessidade de instalar dependências externas:

* **`socket`**: Para a criação e gerenciamento das conexões de rede de baixo nível (Sockets TCP).
* **`concurrent.futures (ThreadPoolExecutor)`**: Para gerenciar o paralelismo e a distribuição das tarefas em múltiplas threads.
* **`time`**: Para medição e análise do tempo de execução da varredura.

---

## 📊 Arquitetura do Sistema e Desafios Acadêmicos

O maior desafio deste projeto não foi a sintaxe da linguagem, mas sim a **modelagem lógica da concorrência**. 

Para conectar a lista de portas gerada ao executor de threads mantendo o IP do alvo fixo, foi necessário utilizar funções anônimas (`lambda`). Essa abordagem permitiu que as threads trabalhassem de forma independente e assíncrona, resolvendo o gargalo de tempo que um escaneamento sequencial (porta por porta) causaria.

[Usuário define Alvo/Portas] 
           │
           ▼
[ThreadPoolExecutor (100 Workers)] ──► Usando Lambda para fixar o IP
           │
     ┌─────┼─────┐
     ▼     ▼     ▼
  [P:22] [P:80] [P:443]  (Execução em Paralelo via Sockets TCP)
     │     │     │
     └─────┼─────┘
           ▼
[Filtro de Resultados: ABERTA / FECHADA]
           │
           ▼
[Exibição no Terminal & Geração de Relatório .txt]
