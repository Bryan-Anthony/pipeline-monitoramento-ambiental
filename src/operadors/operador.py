

class Operador:
    def __init__(self, cpf, nome, email, senha):
        self.cpf = cpf
        self.nome = nome
        self.email = email
        self.senha = senha

    def exibir_dados(self):
        print("\n--- Dados do Operador ---")
        print(f"CPF: {self.cpf}")
        print(f"Nome: {self.nome}")
        print(f"E-mail: {self.email}")
        
