from src.database.db_manager import DatabaseManager
import pandas as pd


class MonitoramentoRepository:

    def __init__(self):
        self.db = DatabaseManager()

    def inserir_dados(self, df, id_projeto):

        conexao = self.db.conectar()

        try:

            cursor = conexao.cursor()

            sql = """
                INSERT INTO leitura
                (
                    dataHora,
                    temperatura,
                    ph,
                    idProjeto
                )
                VALUES (?, ?, ?, ?)
            """

            for _, linha in df.iterrows():

                data_hora = linha["data_hora"]
                temperatura = linha["temperatura"]
                ph = linha["ph"]

                # NaN / NaT -> None
                if pd.isna(data_hora):
                    data_hora = None

                if pd.isna(temperatura):
                    temperatura = None

                if pd.isna(ph):
                    ph = None

                cursor.execute(
                    sql,
                    data_hora,
                    temperatura,
                    ph,
                    id_projeto
                )

            conexao.commit()

            print("Dados inseridos com sucesso!")

            

        except Exception as erro:

            conexao.rollback()

            print(f"Erro ao inserir dados: {erro}")

            raise

        finally:

            cursor.close()

            self.db.fechar(conexao)

        #função filtro tabela leitura _ tabela cliente