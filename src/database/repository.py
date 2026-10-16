from src.database.db_manager import DatabaseManager
import pandas as pd


class MonitoramentoRepository:

    def __init__(self):
        self.db = DatabaseManager()

    def inserir_dados(self, df, id_projeto):

        conexao = self.db.conectar()
        cursor = None

        try:
            cursor = conexao.cursor()

            sql = """
                INSERT INTO leitura
                (
                    entry_id_api,
                    dataHora,
                    ph,
                    temperaturaAgua,
                    temperaturaAr,
                    oxigenioDissolvido,
                    condutividadeEletrica,
                    turbidezAgua,
                    fkEstacao
                )
                SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM leitura
                    WHERE entry_id_api = ?
                )
            """

            total_inseridos = 0
            total_ignorados = 0

            for _, linha in df.iterrows():

                entry_id_api = linha["entry_id_api"]
                data_hora = linha["data_hora"]
                temperatura = linha["temperatura"]
                condutividade = linha["condutividade"]
                temperatura_do_ar = linha["temperatura_do_ar"]
                turbidez = linha["turbidez"]
                oxigenio_dissolvido = linha["oxigenio_dissolvido"]
                ph = linha["ph"]

                # Converter valores ausentes para None
                valores = [
                    entry_id_api,
                    data_hora,
                    temperatura,
                    condutividade,
                    temperatura_do_ar,
                    turbidez,
                    oxigenio_dissolvido,
                    ph
                ]

                valores = [
                    None if pd.isna(valor) else valor
                    for valor in valores
                ]

                (
                    entry_id_api,
                    data_hora,
                    temperatura,
                    condutividade,
                    temperatura_do_ar,
                    turbidez,
                    oxigenio_dissolvido,
                    ph
                ) = valores

                cursor.execute(
                    sql,
                    entry_id_api,
                    data_hora,
                    ph,
                    temperatura,
                    temperatura_do_ar,
                    oxigenio_dissolvido,
                    condutividade,
                    turbidez,
                    id_projeto,
                    entry_id_api
                )

                if cursor.rowcount > 0:
                    total_inseridos += 1
                else:
                    total_ignorados += 1

            conexao.commit()

            print(f"Registros inseridos: {total_inseridos}")
            print(f"Registros duplicados ignorados: {total_ignorados}")

            

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
                    entry_ID,
                    entry_id_api,
                    dataHora,
                    ph,
                    temperaturaAgua,
                    temperaturaAr,
                    oxigenioDissolvido,
                    condutividadeEletrica,
                    turbidezAgua,
                    idOperador,
                    fkEstacao
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
                -- Dados da estação
                e.idEstacao,
                e.nome AS estacao,

                -- Dados do projeto
                p.codigoProjeto,

                -- Dados do cliente
                c.idCliente,
                c.nomeCliente,

                -- Valores de referência do cliente
                MAX(CASE
                    WHEN pc.fkParametro = 1
                    THEN pc.valorReferencia
                END) AS ph,

                MAX(CASE
                    WHEN pc.fkParametro = 2
                    THEN pc.valorReferencia
                END) AS temperatura,

                MAX(CASE
                    WHEN pc.fkParametro = 3
                    THEN pc.valorReferencia
                END) AS temperaturaAr,

                MAX(CASE
                    WHEN pc.fkParametro = 4
                    THEN pc.valorReferencia
                END) AS oxigenioDissolvido,

                MAX(CASE
                    WHEN pc.fkParametro = 5
                    THEN pc.valorReferencia
                END) AS condutividadeEletrica,

                MAX(CASE
                    WHEN pc.fkParametro = 6
                    THEN pc.valorReferencia
                END) AS turbidez

            FROM dbo.estacaoCliente AS ec

            INNER JOIN dbo.estacao AS e
                ON e.idEstacao = ec.fkEstacao

            INNER JOIN dbo.cliente AS c
                ON c.idCliente = ec.fkCliente

            INNER JOIN dbo.projeto AS p
                ON p.idProjeto = e.fkProjeto

            LEFT JOIN dbo.parametroCliente AS pc
                ON pc.fkCliente = c.idCliente

            WHERE p.codigoProjeto = '2412377'

            GROUP BY
                e.idEstacao,
                e.nome,
                p.codigoProjeto,
                c.idCliente,
                c.nomeCliente

            ORDER BY
                c.nomeCliente;
        """

            # Lê o resultado direto para um DataFrame usando pandas
            df = pd.read_sql(sql, conexao)

            return df

        except Exception as erro:
            print(f"Erro ao buscar clientes: {erro}")
            raise

        finally:
            self.db.fechar(conexao)