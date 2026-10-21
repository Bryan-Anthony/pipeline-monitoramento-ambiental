
from getpass import getpass
import os
import logging
import hashlib
from src.operadors.operador import Operador
from src.database.repository import MonitoramentoRepository 
from src.utils.logger import Logger 


class CadastroOperador:

    logger = Logger.configurar()
    def __init__(self):
        self.repository = MonitoramentoRepository()
        self.codigo_projeto = 2412377

    @staticmethod
    def gerar_hash_senha(senha):
        salt = os.urandom(16)

        hash_senha = hashlib.scrypt(
            senha.encode("utf-8"),
            salt=salt,
            n=2**14,
            r=8,
            p=1
        )
        return f"scrypt${salt.hex()}${hash_senha.hex()}"

    def selecionar_estacao(self):
        estacoes = self.repository.listar_estacoes(
            self.codigo_projeto
        )

        if not estacoes:
            print(
                "Nenhuma estação encontrada para esse projeto."
            )
            return None

        print("\n=== ESTAÇÕES DISPONÍVEIS ===")

        for indice, estacao in enumerate(estacoes, start=1):
            print(
                f"{indice} - {estacao['nome']} "
                f"(ID: {estacao['idEstacao']})"
            )

        while True:
            opcao = input(
                "Selecione o número da estação: "
            ).strip()

            try:
                indice = int(opcao)
            except ValueError:
                print("Digite um número válido.")
                continue

            if 1 <= indice <= len(estacoes):
                estacao_escolhida = estacoes[indice - 1]

                print(
                    f"Estação selecionada: "
                    f"{estacao_escolhida['nome']}"
                )

                return estacao_escolhida

            print(
                f"Escolha um número entre 1 e {len(estacoes)}."
            )

    def cadastrar(self):
        print("\n=== CADASTRO DE OPERADOR ===")

        cpf = input(
            "Digite o CPF (somente números): "
        ).strip()

        nome = input("Digite o nome: ").strip()
        email = input("Digite o e-mail: ").strip()
        senha = getpass("Digite a senha: ")

        if not all([cpf, nome, email, senha]):
            print("Todos os campos são obrigatórios.")
            return

        if len(cpf) != 11 or not cpf.isdigit():
            print("O CPF deve conter exatamente 11 números.")
            return

        estacao = self.selecionar_estacao()

        if estacao is None:
            return

        operador = Operador(
            cpf=cpf,
            nome=nome,
            email=email,
            senha=self.gerar_hash_senha(senha)
        )

        try:
            self.repository.inserir_operador(
                operador=operador,
                id_estacao=estacao["idEstacao"],
                codigo_projeto=self.codigo_projeto
            )

            print("\nOperador cadastrado com sucesso!")
            operador.exibir_dados()

        except Exception:
            self.logger.exception(
                "Falha no cadastro do operador."
            )
            print(
                "Não foi possível cadastrar o operador. "
                "Verifique o log e os dados informados."
            )
