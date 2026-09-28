# from src.database.db_manager import DatabaseManager


# class MonitoramentoRepository:

#     def __init__(self):
#         self.db = DatabaseManager()

#     def inserir_dados(self, df):

#         conexao = self.db.conectar()

#         try:

#             cursor = conexao.cursor()

#             sql = """
#                 INSERT INTO Temperatura
#                 (
#                     Valor,
#                     Data
#                 )
#                 VALUES (?, ?)
#             """

#             for _, linha in df.iterrows():

#                 cursor.execute(
#                     sql,
#                     linha["temperatura"],
#                     linha["data_hora"]
#                 )

#             conexao.commit()

#             print("Dados inseridos com sucesso!")

#         except Exception as erro:

#             conexao.rollback()

#             print(f"Erro ao inserir dados: {erro}")

#             raise

#         finally:

#             cursor.close()

#             self.db.fechar(conexao)