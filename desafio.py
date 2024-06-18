import textwrap 

def menu():
    menu = """\n
    ---------------- MENU -----------------
    Digite o número para a operação que deseja realizar:  
    [0]\tDepositar
    [1]\tSacar
    [2]\tExtrato
    [3]\tNova conta
    [4]\tListar contas 
    [5]\tNovo usuário
    [6]\tSair
    -> """
    return input(textwrap.dedent(menu))

def depositar (saldo, valor, extrato, /): 
        if valor > 0:
            saldo += valor
            extrato += f"Depósito:\tR$ {valor:.2f}\n"
            print("\n--- Depósito realizado com sucesso! ---")

        else:
            print("\n### Operação falhou! O valor informado é inválido. ###")

        return saldo, extrato

def sacar (*, saldo, valor, extrato, limite, numero_saques, limite_saques):
        excedeu_saldo = valor > saldo

        excedeu_limite = valor > limite

        excedeu_saques = numero_saques >= limite_saques

        if excedeu_saldo:
            print("\n### Operação falhou! Você não tem saldo suficiente. ###")

        elif excedeu_limite:
            print("\n### Operação falhou! O valor do saque excede o limite. ###")

        elif excedeu_saques:
            print("\n### Operação falhou! Número máximo de saques excedido. ###")

        elif valor > 0:
            saldo -= valor
            extrato += f"Saque:\t\tR$ {valor:.2f}\n"
            numero_saques += 1
            print("\n--- Saque realizado com sucesso! ---")

        else:
            print("\n### Operação falhou! O valor informado é inválido. ###")

        return saldo, extrato

def exibir_extrato(saldo, /, *, extrato):
     print("\n-------------- EXTRATO --------------")
     print("Não foram realizadas movimentações." if not extrato else extrato)
     print(f"\nSaldo:\t\tR$ {saldo:.2f}")
     print("--------------------------------------")

def criar_usuario(usuarios): 
     cpf = input("Informe o CPF (somente números): ")
     usuario = filtrar_usuario(cpf, usuarios)

     if usuario: 
          print("\n### Usuário com CPF já cadastrado! ###")
          return 
     
     nome = input("Informe o nome completo: ")
     endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")
     data_nascimento = input("Informe a data de nascimento (dd/mm/aaaa) : ")
     usuarios.append({"nome": nome, 
                      "endereço": endereco, 
                      "data_nascimento": data_nascimento,
                      "CPF": cpf})
     
     print("\n--- Usuário criado com sucesso! ---")

def filtrar_usuario(cpf, usuarios):
     usuarios_filtrados = [usuario for usuario in usuarios if usuario["CPF"] == cpf] 
     return usuarios_filtrados[0] if usuarios_filtrados else None

def criar_conta(agencia, numero_conta, usuarios): 
     cpf = input("Informe o CPF (somente números): ")
     usuario = filtrar_usuario(cpf, usuarios)

     if usuario: 
          print("\n--- Conta criada com sucesso! ---")
          return {
               "agencia": agencia, 
               "conta": numero_conta, 
               "usuario": usuario
          }
     print("\n### Usuário não encontrado. Operação de criação de conta falhou. ###")
     
def listar_contas(contas): 
     for conta in contas: 
          texto_contas = f'''\n
                    Agência:\t{conta["agencia"]}
                    Conta:\t{conta["conta"]}
                    Titular:\t{conta["usuario"]["nome"]}
                    '''
          print("-"*50)
          print(textwrap.dedent(texto_contas))    
     
def main (): 
    LIMITE_SAQUES = 3
    AGENCIA = "0001"
    
    saldo = 0
    limite = 500
    extrato = ""
    numero_saques = 0
    usuarios = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "0": 
            valor = float(input("Informe o valor a ser depositado: "))
            saldo, extrato = depositar(saldo, valor, extrato)

        elif opcao == "1": 
            valor = float(input("Informe o valor a ser sacado: "))
            saldo, extrato = sacar(
                saldo = saldo, 
                valor = valor, 
                extrato = extrato, 
                limite = limite, 
                numero_saques = numero_saques, 
                limite_saques = LIMITE_SAQUES)

        elif opcao == "2": 
             exibir_extrato(saldo, extrato = extrato)

        elif opcao == "5": 
             criar_usuario(usuarios)  

        elif opcao == "3": 
             numero_conta = len(contas) + 1 
             conta = criar_conta(AGENCIA, numero_conta, usuarios)

             if conta: 
                  contas.append(conta)

        elif opcao == "4": 
             listar_contas(contas)
        
        elif opcao == "6": 
             break

        else: 
            print("\n### Operação inválida! Selecione novamente a opção desejada. ###")
    print(numero_saques)
main()    
