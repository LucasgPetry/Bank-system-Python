from datetime import datetime, date, time
from abc import ABC, abstractclassmethod, abstractproperty
import textwrap
from pathlib import Path 

ROOT_PATH = Path(__file__).parent

class ContaIterador: 
    def __init__(self, contas):
        self.contas = contas 
        self._index = 0 

    def __iter__(self): 
        return self 

    def __next__(self): 
        try: 
            conta = self.conta[self._index]
            return f'''
                Agencia:\t{conta.agencia}
                Numero:\t\t{conta.numero} 
                Titular:\t{conta.cliente.nome} 
                Saldo:\t\tR$ {conta.saldo:.2f}
            '''
        except IndexError: 
            raise StopIteration

        finally: 
            self._index += 1 

class Cliente: 
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
        self.indice_conta = 0 
    
    def realizar_transacao(self, conta, transacao):
        if len(conta.historico.transacoes_do_dia()) >= 2:
            print("### Você excedeu o número de operações diárias. ###")
            return
         
        transacao.registrar(conta)

    def adicionar_conta(self, conta): 
        self.contas.append(conta) 

class PessoaFisica(Cliente): 
    def __init__(self, nome, cpf, data_nascimento, endereco):
        super().__init__(endereco) 
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: ('{self.nome}', '{self.cpf}')>"

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
            print("\n### Operação falhou! Você não possui saldo suficiente. ###")
        
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
    
    @classmethod
    def nova_conta(cls, cliente, numero, limite, limite_saques):
        return cls(numero, cliente, limite, limite_saques)

    def sacar(self, valor): 
        numero_saques = len(
            [
                transacao 
                for transacao in self.historico.transacoes 
                if transacao["tipo"]==Saque.__name__
             ]
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
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: ('{self.agencia}', '{self.numero}', '{self.cliente.nome}')>"

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
                    "data": datetime.utcnow().strftime("%d/%m/%Y - %H:%M:%S"),
                }
            )
        
        def gerar_relatorio(self, tipo_transacao=None): 
            for transacao in self._transacoes:
                if (
                    tipo_transacao is None
                    or transacao["tipo"].lower()==tipo_transacao.lower()
                ): 
                    yield transacao  

        def transacoes_do_dia(self): 
            data_atual = datetime.utcnow().date()
            transacoes = []
            for transacao in self._transacoes:
                data_transacao = datetime.strptime(
                    transacao["data"], ("%d/%m/%Y - %H:%M:%S")
                ).date()
                if data_transacao == data_atual:
                    transacoes.append(transacao)
            
            return transacoes

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

def log_transacao(funcao): 
    def envelope(*args, **kwargs): 
        resultado = funcao(*args, **kwargs)
        data_hora = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(ROOT_PATH / "log.txt", "a") as arquivo: 
            arquivo.write(
            f"[{data_hora}] Funcao '{funcao.__name__}' executada com argumentos {args} e {kwargs}. "
            f"Retornou {resultado}\n"
        )

        return resultado 
    
    return envelope

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

@log_transacao
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

@log_transacao
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

@log_transacao
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
    extrato = ""
    tem_transacao = False
    #Se quiser filtrar apenas um tipo de operação no extrato, coloca o tipo dentro do 
    #gerar relatório como string
    for transacao in conta.historico.gerar_relatorio(): 
        tem_transacao = True 
        extrato += f"\n{transacao["data"]}\n{transacao["tipo"]}\n\tR$ {transacao["valor"]:.2f}"
    if not tem_transacao: 
        extrato = "Não foram realizadas movimentações"
    
    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("-"*39)

@log_transacao
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

@log_transacao
def criar_conta(numero_conta, clientes, contas): 
    cpf = input("Informe o CPF do cliente (somente números): ")
    cliente = filtrar_clientes(cpf, clientes)

    if not cliente: 
        print("\n### Cliente não encontrado! Não é possível efetuar a criação da conta. ###")
        return 
    
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta, limite=500, 
                                     limite_saques=10)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n--- Conta criada com sucesso! ---")

def listar_contas(contas): 
    for conta in ContaIterador(contas): 
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
