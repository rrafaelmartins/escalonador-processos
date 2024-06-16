# Inicialização dos recursos
CPU = [None] * 4  # Inicializa 4 CPUs como None
disco = [None] * 4  # Inicializa 4 discos como None
tam = 64  # Define o tamanho da memória em unidades
MP = [None] * (32 * 1000 // tam)  # Inicializa a memória principal (MP) com tamanho ajustado
proxMP = 0  # Próximo endereço de memória disponível
processos_executando = [None] * 4  # Processos em execução nas CPUs
block_queue = []  # Fila de processos bloqueados
userprocess_queue1 = []  # Fila de processos do usuário 1
userprocess_queue2 = []  # Fila de processos do usuário 2
userprocess_queue3 = []  # Fila de processos do usuário 3
userprocess_queue4 = []  # Fila de processos do usuário 4
userprocess_queue = [userprocess_queue1, userprocess_queue2, userprocess_queue3, userprocess_queue4]  # Lista de filas de processos dos usuários
processlist = []  # Lista com os processos a serem despachados

contador = 0  # Contador de unidades de tempo
max_idle_count = 10  # Máximo de unidades de tempo ociosas antes de parar o programa
idle_count = 0  # Contador de tempo ocioso

def getMem(MP: list, tam: int, prox: int):  # Função que retorna o próximo valor disponível na memória principal
    i = 0
    for _ in range(len(MP)):
        try:
            if MP[prox + i] is None:  # Verifica se o espaço na memória está livre
                i += 1
            else:
                prox, i = prox + i + 1, 0  # Move para o próximo bloco de memória se o espaço não estiver livre
            if i >= tam:
                return prox  # Retorna o endereço inicial do bloco de memória livre
        except IndexError:
            return getMem(MP, tam, 0)  # Reinicia a busca se o final da memória foi alcançado
    return -1  # Retorna -1 se não há espaço suficiente

def exec_io(block_queue: list, user_queues: list):  # Função que contabiliza o tempo de I/O para cada processo bloqueado
    j = 0
    for i in range(len(block_queue)):
        block_queue[i - j][2] -= 1  # Decrementa o tempo de I/O do processo
        if block_queue[i - j][2] == -1:  # Se o tempo de I/O terminou
            current_queue = block_queue[i - j][7]  # Obtém a fila atual do processo
            print(f"Processo {block_queue[i - j]}") 
            print(f"FILA ATUAL de {block_queue[i - j][6]}: {current_queue}")
            next_queue = current_queue + 1 if current_queue != 4 else 1  # Calcula a próxima fila de prontos
            print(f"Processo {block_queue[i - j]} escalonado de bloqueado para pronto (userprocess_queue{next_queue})")
            current_queue = next_queue  # Atualiza o índice da fila atual
            block_queue[i - j][7] = current_queue 
            print(f"NOVA FILA DE {block_queue[i - j][6]}: {current_queue}")
            print(f"Processo {block_queue[i - j]}") 
            user_queues[next_queue -1].append(block_queue.pop(i - j))  # Move o processo para a próxima fila de prontos
            j += 1

def exec_CPU(user_process: list, processos_executando: list, n: int, disco: list, quantum: int, p: list, block_queue: list, MP: list):
    #print(processos_executando)
    if processos_executando[n] is not None:  # Se há um processo executando na CPU
        tempo_restante = processos_executando[n][1] + processos_executando[n][2] + processos_executando[n][3]
        if tempo_restante < 1:
            CPU[n] = None
        print(f"Executando processo - {processos_executando[n][6]} na CPU - {n} (Tempo restante: {processos_executando[n][1] + processos_executando[n][2] + processos_executando[n][3]})")
        if processos_executando[n][1] > 0:  # Fase 1 de CPU
            processos_executando[n][1] -= 1
        elif processos_executando[n][2] > 0:  # Fase de I/O
            processos_executando[n][2] -= 1
        elif processos_executando[n][3] > 0:  # Fase 2 de CPU
            processos_executando[n][3] -= 1

        if len(processos_executando[n]) <= 8:
            processos_executando[n].append(0)  # Incrementa o tempo executado se não estiver presente

        processos_executando[n][8] += 1  # Incrementa o tempo executado

        if processos_executando[n][1] == 0 and processos_executando[n][2] == 0 and processos_executando[n][3] == 0:
            print(f"--- Processo {processos_executando[n][6]} terminou ---\n")
            if processos_executando[n][5] > 0:
                for i in range(len(disco)):
                    if disco[i] == processos_executando[n][6]: disco[i] = None  # Libera os recursos de disco
            prox = processos_executando[n][4]
            try:
                while MP[prox] == processos_executando[n][6]: MP[prox], prox = None, prox + 1  # Libera a memória ocupada pelo processo
            except IndexError: prox = 0
            processos_executando[n] = None
            CPU[n] = None  # Libera a CPU
        elif processos_executando[n][2] > 0 and processos_executando[n][8] == quantum:
            print(f"Processo {processos_executando[n][6]} em I/O (escalonado de pronto para bloqueado)")
            processos_executando[n].append(processos_executando[n][-1])  # Armazena a fila atual antes de bloquear
            block_queue.append(processos_executando[n])  # Move o processo para a fila de bloqueados
            processos_executando[n] = None
            CPU[n] = None  # Libera a CPU
        elif (processos_executando[n][1] == 0 and processos_executando[n][2] == 0 and processos_executando[n][3] > 0 and 
              processos_executando[n][8] % quantum == 0):
            print(f"Processo {processos_executando[n][6]} atingiu o Quantum")
            current_queue = processos_executando[n][7]
            next_queue = current_queue + 1 if current_queue != 4 else 1  # Calcula a próxima fila de prontos
            processos_executando[n][7] = next_queue  # Atualiza o índice da fila atual
            user_process[next_queue].append(processos_executando[n])  # Move o processo para a próxima fila de prontos
            processos_executando[n] = None
            CPU[n] = None  # Libera a CPU
        elif processos_executando[n][3] == 0 and 'fase2_terminada' not in processos_executando[n]:
            print(f"--- Processo {processos_executando[n][6]} terminou a segunda fase de CPU ---")
            processos_executando[n].append('fase2_terminada')  # Marca que a segunda fase de CPU terminou
            CPU[n] = None  # Libera a CPU
            num_espacos_disco = processos_executando[n][5]
            id_processo = processos_executando[n][6]
            for i in range(num_espacos_disco):
                index = disco.index(id_processo)
                disco[index] = None
            for j in range(len(MP)):
                if MP[j] == id_processo:
                    MP[j] = None
            processos_executando[n] = None
            
    else:
        for queue in user_process:
            if queue:
                processos_executando[n] = queue.pop(0)  # Pega o próximo processo da fila de prontos do usuário
                CPU[n] = processos_executando[n]
                exec_CPU(user_process, processos_executando, n, disco, quantum, p, block_queue, MP)
                break

def primeirovalor(lista: list):
    return lista[0]  # Função para auxiliar na ordenação

def novo_pronto(processo: list, tempo: int, filapronto: list, disco: list, MP: list, proxMP: int, tam: int) -> int:
    if processo == []: return proxMP
    i = 0
    while i < len(processo) and processo[i][0] <= tempo:
        tp = (processo[i][4] - 1) // tam + 1  # Calcula o número de blocos de memória necessários
        prox = getMem(MP, tp, proxMP)
        if prox != -1 and processo[i][5] <= disco.count(None):
            for index in range(tp):
                MP[prox + index] = processo[i][6]  # Reserva a memória para o processo usando o ID
            processo[i][4] = prox
            k = processo[i][5]
            j = 0
            proxMP = prox + tp
            while k > 0:
                if disco[j] is None:
                    disco[j], k = processo[i][6], k - 1  # Reserva os discos para o processo usando o ID
                j += 1
            print(f"Processo {processo[i][6]} escalonado de novo para pronto")
            processo[i].append(0)  # Adiciona o índice da fila atual de prontos
            filapronto.append(processo.pop(i))  # Move o processo para a fila de prontos
        else:
            print(f"Processo {processo[i][6]} nao foi escalonado")
            i += 1
            print("Disco - {}".format(disco))

    return proxMP

# Leitura do arquivo de entrada no novo formato
with open("processos.txt") as arq:  # abre o arquivo de entrada
    for linha in arq:
        vet_linha = linha.strip().split(", ")
        if len(vet_linha) == 8:  # Garante que a linha tem 7 elementos (6 atributos + 1 ID)
            processlist.append(list(map(int, vet_linha)))  # Adiciona os processos à lista de processos

processlist.sort(key=lambda x: x[0])  # ordena os processos pelo momento de chegada

print("Processos no arquivo:")
for i in processlist:
    print("Processo ", i)

var_usuario = int(input("Digite a unidade de tempo: "))  # Solicita ao usuário a quantidade de unidades de tempo a executar
cont = 0
while var_usuario != -1:
    cont += 1
    if cont == 2:
        proxMP = novo_pronto(processlist, contador, userprocess_queue1, disco, MP, proxMP, tam) 
    else:
        for queue in userprocess_queue:
            if (len(queue) == 0):
                proxMP = novo_pronto(processlist, contador, userprocess_queue1, disco, MP, proxMP, tam)  # Atualiza a fila de prontos do usuário 1
        else:
            if len(userprocess_queue2) > 0:
                proxMP = novo_pronto(processlist, contador, userprocess_queue2, disco, MP, proxMP, tam)  # Atualiza a fila de prontos do usuário 1
            elif len(userprocess_queue3) > 0:
                proxMP = novo_pronto(processlist, contador, userprocess_queue3, disco, MP, proxMP, tam)  # Atualiza a fila de prontos do usuário 
            elif len(userprocess_queue4) > 0:
                proxMP = novo_pronto(processlist, contador, userprocess_queue4, disco, MP, proxMP, tam)  # Atualiza a fila de prontos do usuário 


    p = [None] * 4
    exec_io(block_queue, userprocess_queue)  # Executa I/O nos processos bloqueados
    for i in range(4):
        exec_CPU(userprocess_queue, processos_executando, i, disco, 3, p, block_queue, MP)  # Executa os processos nas CPUs

    print(f"FILA 1: {userprocess_queue1}")
    print(f"FILA 2: {userprocess_queue2}")
    print(f"FILA 3: {userprocess_queue3}")
    print(f"FILA 4: {userprocess_queue4}")

    # Verifica se algum processo foi escalonado
    if all(cpu is None for cpu in CPU) and not any(userprocess_queue) and not processlist:
        idle_count += 1
        if idle_count >= max_idle_count:
            print("O sistema entrou em estado de espera ociosa prolongada. Encerrando a execução.")
            break
    else:
        idle_count = 0

    # Exibir estado atual das CPUs e a fila de prontos
    for i in range(4):
        if CPU[i] is not None and (CPU[i][1] + CPU[i][2] + CPU[i][3] >= 0):
            print(f"CPU {i}: {CPU[i][6]} (Tempo restante: {CPU[i][1] + CPU[i][2] + CPU[i][3]})")
        else:
            CPU[i] = None
            print(f"CPU {i}: {CPU[i]}")
    
    print("Fila de Prontos: ", end="")
    for fila in userprocess_queue:
        for processo in fila:
            print(f"{processo[6]} (Tempo restante: {processo[1] + processo[2] + processo[3]}), ", end="")
    print("\nUnidade de tempo - ", contador)
    #print((MP)) --> PRINT PARA DEBUGGAR OS REGISTROS NA MEMÓRIA PRINCIPAL
    print("================================")
    
    var_usuario -= 1 
    contador += 1
    if var_usuario == 0:
        var_usuario = int(input("Digite a unidade de tempo: "))  # Solicita ao usuário mais unidades de tempo a executar
