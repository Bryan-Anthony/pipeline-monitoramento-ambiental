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

    def buscar_leituras(self):
        """
        Busca todas as leituras registradas na tabela 'leitura'.
        Essas leituras foram inseridas pela ingestão da API.
        Retorna um DataFrame com as colunas: data_hora, temperatura, ph.
        """
        conexao = self.db.conectar()

        try:
            sql = """
                SELECT
                    dataHora   AS data_hora,
                    temperatura,
                    ph
                FROM leitura
            """

            # Lê o resultado direto para um DataFrame usando pandas
            df = pd.read_sql(sql, conexao)

            return df

        except Exception as erro:
            print(f"Erro ao buscar leituras: {erro}")
            raise

        finally:
            self.db.fechar(conexao)

    def buscar_clientes(self):
        """
        Busca os dados das águas engarrafadas registradas na tabela 'cliente'.
        Esses dados foram inseridos manualmente no script_db.sql como referência de comparação.
        Retorna um DataFrame com as colunas: nome, ph, temperatura.
        """
        conexao = self.db.conectar()

        try:
            sql = """
                SELECT
                    nomeCliente   AS nome,
                    phCliente     AS ph,
                    temperaturaCliente AS temperatura
                FROM cliente
            """

            # Lê o resultado direto para um DataFrame usando pandas
            df = pd.read_sql(sql, conexao)

            return df

        except Exception as erro:
            print(f"Erro ao buscar clientes: {erro}")
            raise

        finally:
            self.db.fechar(conexao)