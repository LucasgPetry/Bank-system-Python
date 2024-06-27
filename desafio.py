from datetime import datetime
from abc import ABC, abstractclassmethod, abstractproperty
import textwrap

class Cliente: 
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
    
    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta): 
        self.contas.append(conta) 

class PessoaFisica(Cliente): 
    def __init__(self, nome, cpf, data_nascimento, endereco):
        super().__init__(endereco) 
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento

class Conta: 
    def __init__(self, numero, cliente):
        self._saldo = 0 
        self._numero = numero 
        self._agencia = "0001"
        self._cliente = cliente 
        self._historico = Historico()
    
    @classmethod
    def nova_conta(cls, numero, cliente):
        return cls(numero, cliente) 

    @property
    def saldo(self):
        return self._saldo 
    
    @property
    def numero(self):
        return self._numero 
    
    @property
    def agencia(self):
        return self._agencia 
    
    @property
    def cliente(self):
        return self._cliente 
    
    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo 
        excedeu_saldo = valor > saldo 

        if excedeu_saldo:
            print("### Operação falhou! Você não possui saldo suficiente. ###")
        
        elif valor > 0: 
            self._saldo -= valor
            print("--- Saque realizado com sucesso! ---")
            return True 

        else: 
            print("### Operação falhou! Valor de saque inválido. ###")
        return False    
    
    def depositar(self, valor): 
        if valor > 0: 
            self._saldo += valor 
            print("--- Depósito realizado com sucesso! ---")
        
        else: 
            print("### Operação falhou! Valor de depósito inválido. ###")
            return False 
        
        return True

class ContaCorrente(Conta): 
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques 

    def sacar(self, valor): 
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"]==Saque.__name__]
        )

        excedeu_limite = valor > self._limite 
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite: 
            print("### Operação falhou! Você excedeu o valor do limite de saque. ###")

        elif excedeu_saques: 
            print("### Operação falhou! Você excedeu o número de saques. ###")

        else: 
            return super().sacar(valor)
        
        return False 
    
    def __str__(self):
        return f'''
            Agencia:\t{self.agencia}
            Conta:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        '''
    
class Historico:  
        def __init__(self):
            self._transacoes = [] 
        
        @property
        def transacoes(self): 
            return self._transacoes
        
        def adicionar_transacao(self, transacao): 
            self._transacoes.append(
                {
                    "tipo": transacao.__class__.__name__,
                    "valor": transacao.valor, 
                    "data": datetime.now().strftime("%d/%m/%Y - %H:%M:%s"),
                }
            )

class Transacao(ABC): 
    @property
    @abstractproperty
    def valor(self): 
        pass 

    @abstractclassmethod
    def registrar(self, conta): 
        pass

class Saque(Transacao): 
    def __init__(self, valor):
        self._valor = valor 

    @property
    def valor(self): 
        return self._valor
    
    def registrar(self, conta): 
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao: 
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao): 
    def __init__(self, valor):
        self._valor = valor 

    @property
    def valor(self): 
        return self._valor
    
    def registrar(self, conta): 
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao: 
            conta.historico.adicionar_transacao(self)

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

def filtrar_clientes(cpf, clientes): 
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None 

def recuperar_conta_cliente(cliente): 
    if not cliente.contas: 
        print("\n### Cliente não possui conta! ###")
        return  

    return cliente.contas[0]

def depositar(clientes): 
    cpf = input("Informe o CPF do cliente (somente números): ")
    cliente = filtrar_clientes(cpf, clientes)

    if not cliente: 
        print("\n### Cliente não encontrado! ###")
        return 
    
    valor = float(input("Informe o valor a ser depositado: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta: 
        return 
    
    cliente.realizar_transacao(conta, transacao)

def sacar(clientes): 
    cpf = input("Informe o CPF do cliente (somente números): ")
    cliente = filtrar_clientes(cpf, clientes)

    if not cliente: 
        print("\n### Cliente não encontrado! ###")
        return 
    
    valor = float(input("Informe o valor a ser depositado: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta: 
        return 
    
    cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes): 
    cpf = input("Informe o CPF do cliente (somente números): ")
    cliente = filtrar_clientes(cpf, clientes)

    if not cliente: 
        print("\n### Cliente não encontrado! ###")
        return 
    
    conta = recuperar_conta_cliente(cliente)
    if not conta: 
        return 
    
    print("\n--------------- EXTRATO ---------------")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes: 
        extrato = "Não foram realizadas movimentações"
    
    else: 
        for transacao in transacoes: 
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"
    
    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("-"*39)

def criar_cliente(clientes): 
    cpf = input("Informe o CPF do cliente (somente números): ")
    cliente = filtrar_clientes(cpf, clientes)

    if cliente: 
        print("\n### Já existe cliente com esse cpf! ###")
        return 

    nome = input("Informe o seu nome completo: ")
    data_nascimento = input("Informe a sua data de nascimento (dd/mm/aaaa): ")
    endereco = input("Informe seu endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(nome=nome, cpf=cpf, data_nascimento=data_nascimento, endereco=endereco)
    clientes.append(cliente)

    print("--- Cliente cadastrado com sucesso! ---")

def criar_conta(numero_conta, clientes, contas): 
    cpf = input("Informe o CPF do cliente (somente números): ")
    cliente = filtrar_clientes(cpf, clientes)

    if not cliente: 
        print("\n### Cliente não encontrado! Não é possível efetuar a criação da conta. ###")
        return 
    
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n--- Conta criada com sucesso! ---")

def listar_contas(contas): 
    for conta in contas: 
        print("-"*20)
        print(textwrap.dedent(str(conta)))
        print("-"*20)

def main(): 
    contas = []
    clientes = [] 
        
    while True: 
        opcao = menu()

        if opcao == "0": 
            depositar(clientes)

        elif opcao == "1": 
            sacar(clientes)

        elif opcao == "2": 
            exibir_extrato(clientes)

        elif opcao == "5": 
            criar_cliente(clientes)

        elif opcao == "3": 
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "4": 
            listar_contas(contas)

        elif opcao == "6": 
            break

        else: 
            print("\n### Operação inválida! Digite novamente o número da opção que deseja realizar ###.")

main()
