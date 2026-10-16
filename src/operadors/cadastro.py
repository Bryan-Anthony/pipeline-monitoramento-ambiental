
from getpass import getpass

from src.operators.operador import Operador


class CadastroOperador:
    def __init__(self):
        self.operadores = []

    def cadastrar(self):
        print("\n=== CADASTRO DE OPERADOR ===")

        cpf = input("Digite o CPF: ").strip()
        nome = input("Digite o nome: ").strip()
        email = input("Digite o e-mail: ").strip()
        senha = getpass("Digite a senha: ")

        operador = Operador(
            cpf=cpf,
            nome=nome,
            email=email,
            senha=senha
        )

        self.operadores.append(operador)

        print("\nOperador cadastrado com sucesso!")
        operador.exibir_dados()

    def listar_operadores(self):
        print("\n=== LISTA DE OPERADORES ===")

        if not self.operadores:
            print("Nenhum operador cadastrado.")
            return

        for operador in self.operadores:
            operador.exibir_dados()
