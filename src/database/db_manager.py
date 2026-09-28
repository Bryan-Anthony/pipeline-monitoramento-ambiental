import pyodbc

class DatabaseManager:
    
    def __init__(self):

        self.connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            #"SERVER=localhost\\SQLEXPRESS;"
            #"SERVER=localhost\SQLEXPRESS;"
            #"SERVER=.\SQLEXPRESS;"
            #"SERVER=localhost;"
            "SERVER=(localdb)\MSSQLLocalDB;"
            "DATABASE=Walter;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
    )

    def conectar(self):
            try:
                conexao = pyodbc.connect(self.connection_string)

                print("Conexão com SQL Server realizada com sucesso!")

                return conexao

            except pyodbc.Error as erro:
                print(f"Erro ao conectar com o banco: {erro}")
                raise

    def fechar(self, conexao):
            if conexao:
                conexao.close()
                print("Conexão encerrada.")