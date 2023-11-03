import requests
import oracledb


def linha():
    print('------------------------------')

# Função para criar a tabela de jogadores (executar apenas uma vez)

def criar_tabela_jogadores():
    conn = oracledb.connect(user="RM99585", password="210305", dsn="oracle.fiap.com.br/orcl")
    cursor = conn.cursor()

    # Consulta SQL para verificar se a tabela já existe
    cursor.execute("SELECT count(*) FROM user_tables WHERE table_name = 'JOGADORES'")
    tabela_existe = cursor.fetchone()

    if not tabela_existe or tabela_existe[0] == 0:
        # A tabela não existe, então criamos
        cursor.execute('''
        CREATE TABLE jogadores (
            id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            nome VARCHAR2(50),
            senha VARCHAR2(50),
            saldo NUMBER
        )
        ''')
        conn.commit()
        print("Tabela 'jogadores' criada com sucesso.")
    else:
        print("A tabela 'jogadores' já existe.")

    cursor.close()
    conn.close()

# Função para registrar um novo jogador

def registrar_jogador(nome, senha):
    conn = oracledb.connect(user="RM99585", password="210305", dsn="oracle.fiap.com.br/orcl")
    cursor = conn.cursor()

    cursor.execute('INSERT INTO jogadores (nome, senha, saldo) VALUES (:1, :2, :3)', (nome, senha, 100))
    
    cursor.close()
    conn.commit()
    conn.close()

# Função para fazer login

def fazer_login():
        nome = input("Nome de usuário: ")
        senha = input("Senha: ")

        conn = oracledb.connect(user="RM99585", password="210305", dsn="oracle.fiap.com.br/orcl")
        cursor = conn.cursor()

        cursor.execute('SELECT nome, saldo FROM jogadores WHERE nome = :1 AND senha = :2', (nome, senha))
        resultado = cursor.fetchone()

        conn.close()

        if resultado:
            return resultado[0], resultado[1]
        else:
            print("Nome de usuário ou senha incorretos.")
            return None, None


# Função para atualizar o saldo do jogador
def atualizar_saldo(nome, novo_saldo):
    conn = oracledb.connect(user="RM99585", password="210305", dsn="oracle.fiap.com.br/orcl")
    cursor = conn.cursor()

    cursor.execute('UPDATE jogadores SET saldo = :novo_saldo WHERE nome = :nome', novo_saldo=novo_saldo, nome=nome)
    
    conn.commit()
    conn.close()

# Resto do código do jogo
def criar_baralho():
    response = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1")
    deck_data = response.json()
    deck_id = deck_data["deck_id"]
    return deck_id

def sortear_cartas(deck_id, quantidade):
    response = requests.get(f"https://deckofcardsapi.com/api/deck/{deck_id}/draw/?count={quantidade}")
    cards_data = response.json()
    return cards_data["cards"]

def calcular_valor_mao(mao):
    valor = 0
    as_contagem = 0

    for carta in mao:
        if carta["value"] in ["KING", "QUEEN", "JACK"]:
            valor += 10
        elif carta["value"] == "ACE":
            valor += 11
            as_contagem += 1
        else:
            valor += int(carta["value"])

    while as_contagem > 0 and valor > 21:
        valor -= 10
        as_contagem -= 1

    return valor


def determinar_vencedor(mao_jogador, mao_dealer):
    valor_jogador = calcular_valor_mao(mao_jogador)
    valor_dealer = calcular_valor_mao(mao_dealer)

    if valor_jogador > 21:
        return "Dealer"  # Jogador estourou, o dealer vence
    elif valor_dealer > 21:
        return "Jogador"  # Dealer estourou, o jogador vence
    elif valor_jogador > valor_dealer:
        return "Jogador"  # Jogador tem maior pontuação
    elif valor_dealer > valor_jogador:
        return "Dealer"  # Dealer tem maior pontuação
    else:
        return "Empate"  # Empate

def fazer_aposta(saldo ):
    while True:
        try:
            aposta = int(input(f'Seu saldo atual é {saldo}. Quanto você deseja apostar? '))
            if 0 < aposta <= saldo:
                return aposta
            else:
                print("Aposta inválida. O valor deve estar entre 1 e o seu saldo atual.")
        except ValueError:
            print("Digite um valor numérico válido.")

def mostrar_mao(mao, jogador):
    print(f"Cartas do {jogador}:")
    for carta in mao:
        print(f'{carta["value"]} de {carta["suit"]}')

def mostrar_valor(mao, jogador):
    valor = calcular_valor_mao(mao)
    print(f"Valor da mão do {jogador}: {valor}")

def jogar_rodada(nome_jogador, saldo_jogador):
    while saldo_jogador > 0:
        continuar_jogando = input("Iniciar rodada (S/N): ")
        if continuar_jogando.upper() != 'S':
            exibir_podio()
            exit()
        aposta = fazer_aposta(saldo_jogador)
        saldo_jogador -= aposta

        deck_id = criar_baralho()

        cartas_do_jogador = sortear_cartas(deck_id, 2)
        cartas_do_dealer = sortear_cartas(deck_id, 2)

        mostrar_mao(cartas_do_jogador, "Jogador")
        linha()
        mostrar_mao(cartas_do_dealer, "Dealer")
        linha()
        mostrar_valor(cartas_do_jogador, "Jogador")
        linha()
        for _ in range(10):  # Defina um limite máximo de 10 cartas (você pode ajustar isso)
            escolha = input("Deseja pedir mais cartas (P) ou parar (S)? ").upper()

            if escolha == "P":
                nova_carta = sortear_cartas(deck_id, 1)[0]
                cartas_do_jogador.append(nova_carta)
                mostrar_mao([nova_carta], "Jogador")
                mostrar_valor(cartas_do_jogador, "Jogador")

                if calcular_valor_mao(cartas_do_jogador) > 21:
                    print("Jogador estourou com mais de 21 pontos!")
                    resultado = "Dealer"
                    break
            elif escolha == "S":
                while calcular_valor_mao(cartas_do_dealer) < 16:
                    nova_carta = sortear_cartas(deck_id, 1)[0]
                    cartas_do_dealer.append(nova_carta)

                resultado = determinar_vencedor(cartas_do_jogador, cartas_do_dealer)
                break
            else:
                print("Escolha inválida. Digite P para pedir mais cartas ou S para parar.")

        mostrar_mao(cartas_do_dealer, "Dealer")

        if resultado == "Jogador":
            saldo_jogador += 2 * aposta
            print(f"Jogador vence! Saldo atual: {saldo_jogador}")
        elif resultado == "Empate":
            saldo_jogador += aposta
            print(f"Empate! Saldo atual: {saldo_jogador}")
        else:
            print(f"Dealer vence! Saldo atual: {saldo_jogador}")

        atualizar_saldo(nome_jogador, saldo_jogador)


def jogar_blackjack():
    nome_jogador = None
    saldo_jogador = None

    while True:
        opcao = input("Escolha uma opção:\n1 - Fazer login\n2 - Registrar novo jogador\n3 - Sair\nOpção: ")

        if opcao == "1":
            nome_jogador, saldo_jogador = fazer_login()
            if nome_jogador:
                print(f"Bem-vindo, {nome_jogador}!")
                break
        elif opcao == "2":
            nome = input("Nome de usuário: ")
            senha = input("Senha: ")
            registrar_jogador(nome, senha)
            print("Jogador registrado com sucesso!")
        elif opcao == "3":
            exit()
        else:
            print("Opção inválida. Escolha novamente.")

    while saldo_jogador > 0:
        jogar_rodada(nome_jogador, saldo_jogador)
        linha()

def obter_podio():
    conn = oracledb.connect(user="RM99585", password="210305", dsn="oracle.fiap.com.br/orcl")
    cursor = conn.cursor()

    # Recupere os jogadores com os maiores saldos em ordem decrescente
    cursor.execute('SELECT nome, saldo FROM jogadores ORDER BY saldo DESC')

    # Obtenha os 3 melhores jogadores
    top_jogadores = cursor.fetchmany(3)

    conn.close()

    return top_jogadores


def exibir_podio():
    top_jogadores = obter_podio()

    if top_jogadores:
        print("Pódio dos Melhores Jogadores:")
        for i, (nome, saldo) in enumerate(top_jogadores, start=1):
            print(f"{i}. {nome}: Saldo - {saldo}")
    else:
        print("Nenhum jogador encontrado no pódio.")


if __name__ == "__main__":
    criar_tabela_jogadores()
    jogar_blackjack()
