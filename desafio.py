menu = """
Digite o número para a operação que deseja realizar:  

[0] Depositar
[1] Sacar
[2] Extrato
[3] Sair

->:  """

saldo = 0
limite = 500
extrato = ""
numero_saques = 0
LIMITE_SAQUES = 3

while True:

    opcao = int(input(menu))

    if opcao == 0:
        valor = float(input("Informe o valor a ser depositado: "))

        if valor > 0:
            saldo += valor
            extrato += f"Depósito: R$ {valor:.2f}\n"

        else:
            print("Operação não pode ser efetuada! O valor informado é inválido.")

    elif opcao == 1:
        valor = float(input("Informe o valor a ser sacado: "))

        excedeu_saldo = valor > saldo

        excedeu_limite = valor > limite

        excedeu_saques = numero_saques >= LIMITE_SAQUES

        if excedeu_saldo:
            print("Operação não pode ser efetuada! Você não tem saldo suficiente.")

        elif excedeu_limite:
            print("Operação não pode ser efetuada! O valor do saque excede o limite.")

        elif excedeu_saques:
            print("Operação não pode ser efetuada! Número máximo de saques excedido.")

        elif valor > 0:
            saldo -= valor
            extrato += f"Saque: R$ {valor:.2f}\n"
            numero_saques += 1

        else:
            print("Operação não pode ser efetuada! O valor informado é inválido.")

    elif opcao == 2:
        print("\n************* EXTRATO *************")
        print("Não foram realizadas movimentações." if not extrato else extrato)
        print(f"\nSaldo: R$ {saldo:.2f}")
        print("*************************************")

    elif opcao == 3:
        break

    else:
        print("Operação inválida, por favor selecione novamente o número da operação que deseja realizar.")