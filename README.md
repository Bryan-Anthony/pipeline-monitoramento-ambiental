# 💧 Monitoramento da Qualidade da Água

Pipeline em Python para transformar leituras de uma estação de monitoramento ambiental em análises claras sobre **temperatura** e **pH da água**.

O projeto busca dados de sensores na API ThingSpeak, trata e valida as leituras, salva o histórico no SQL Server e entrega gráficos e um relatório textual para apoiar a análise da qualidade da água.

---

## O produto

O produto final é um **relatório de monitoramento ambiental** gerado automaticamente a partir das leituras da estação `QMStation1`.

Ao executar o pipeline, o projeto gera na pasta `reports/`:

- Histogramas de temperatura e pH
- Boxplots para identificar dispersão e valores fora do padrão
- Gráficos de comparação entre a água monitorada e águas engarrafadas de referência
- Arquivo `diagnostico.txt` com estatísticas, quantidade de leituras e detecção de outliers

### Perguntas respondidas

- Qual é a média, mediana, mínimo e máximo de temperatura e pH?
- Existem valores anômalos nas leituras?
- Como os dados da água monitorada se comparam com referências cadastradas?
- Como a temperatura e o pH estão distribuídos nos dados coletados?

---

## Fluxo do pipeline

```text
ThingSpeak API
     |
     v
Coleta dos dados JSON
     |
     v
Tratamento e validação com Pandas
     |
     v
Persistência no SQL Server
     |
     v
Estatísticas, identificação de outliers e gráficos
     |
     v
Relatórios na pasta reports/
```

1. **Coleta:** consulta a API ThingSpeak, canal `2412377`, e recebe as últimas leituras da estação.
2. **Tratamento:** converte temperatura e pH para números, transforma valores inválidos em nulos e ajusta data e hora.
3. **Validação:** verifica se existem dados, se a coluna de data está presente e se há datas válidas.
4. **Persistência:** grava as leituras no SQL Server.
5. **Análise:** calcula estatísticas descritivas e identifica outliers pelo método IQR.
6. **Entrega:** gera gráficos PNG e um diagnóstico textual.

---

## Dados monitorados

| Dado | Origem | Uso |
|---|---|---|
| `data_hora` | `created_at` da API | Organização temporal das leituras |
| `temperatura` | `field1` da API | Monitoramento da temperatura da água |
| `ph` | `field8` da API | Monitoramento da acidez ou alcalinidade |

A estação cadastrada no banco é a **QMStation1**, associada ao canal ThingSpeak `2412377`.

---

## Análises entregues

### Estatísticas descritivas

Para temperatura e pH, o pipeline calcula:

- Média
- Mediana
- Desvio padrão
- Mínimo e máximo
- Primeiro quartil (Q1)
- Terceiro quartil (Q3)
- Intervalo interquartil (IQR)

### Identificação de outliers

O projeto utiliza a regra do IQR para sinalizar valores fora do comportamento esperado:

```text
Limite inferior = Q1 - 1,5 × IQR
Limite superior = Q3 + 1,5 × IQR
```

Leituras abaixo ou acima desses limites são incluídas no diagnóstico como possíveis anomalias.

### Comparação de referências

Além das leituras da estação, o banco possui valores de pH e temperatura de águas engarrafadas cadastradas como referência. Os gráficos comparativos ajudam a visualizar a posição da água monitorada em relação a essas referências.

---

## Tecnologias utilizadas

| Tecnologia | Aplicação no projeto |
|---|---|
| Python | Linguagem principal do pipeline |
| Requests | Consumo da API ThingSpeak |
| Pandas e NumPy | Tratamento, transformação e análise dos dados |
| Matplotlib | Geração dos gráficos |
| SQL Server | Armazenamento das leituras e dados de referência |
| PyODBC | Conexão do Python com o SQL Server |
| Pytest | Testes automatizados |
| Git e GitHub | Versionamento e colaboração |

---

## Estrutura do projeto

```text
pipeline-monitoramento-ambiental/
├── main.py                         # Executa o pipeline completo
├── requirements.txt                 # Dependências do projeto
├── conftest.py                      # Configuração do pytest
├── src/
│   ├── config.py                    # URL da API e pasta de saída
│   ├── ingestion/
│   │   ├── api_client.py            # Consumo da API
│   │   └── service.py               # Organização da ingestão
│   ├── processing/
│   │   ├── tratamento.py            # Limpeza e conversão dos dados
│   │   ├── validacao.py             # Regras de validação
│   │   └── transformacao.py         # Padronização dos campos
│   ├── database/
│   │   ├── db_manager.py            # Conexão com SQL Server
│   │   ├── repository.py            # Operações de banco
│   │   ├── script_db.sql            # Criação do banco e tabelas
│   │   └── queries.sql              # Consultas auxiliares
│   └── analytics/
│       └── statistics.py            # Estatísticas e gráficos
├── tests/                           # Testes automatizados
└── reports/                         # Saídas geradas pelo pipeline
```

---

## Banco de dados

O banco SQL Server organiza os dados em três tabelas:

| Tabela | Finalidade |
|---|---|
| `cliente` | Armazena águas engarrafadas usadas como referência |
| `projeto` | Armazena os dados da estação de monitoramento |
| `leitura` | Armazena cada leitura de temperatura e pH |

O relacionamento é:

```text
cliente -> projeto -> leitura
```

---

## Como executar

### Pré-requisitos

- Python 3
- SQL Server em execução
- Driver ODBC para SQL Server

### 1. Instale as dependências

```bash
pip install -r requirements.txt
```

### 2. Crie o banco de dados

Execute o arquivo abaixo no SQL Server:

```text
src/database/script_db.sql
```

### 3. Configure a conexão

Revise as configurações de conexão em:

```text
src/database/db_manager.py
```

### 4. Execute o pipeline

```bash
python main.py
```

Após a execução, os gráficos e o arquivo de diagnóstico estarão disponíveis em `reports/`.

---

## Testes

O projeto possui testes para ingestão, tratamento, validação, transformação e estatísticas.

```bash
# Executa todos os testes
python -m pytest

# Executa mostrando os prints no terminal
python -m pytest -s

# Executa apenas os testes de estatística
python -m pytest tests/test_statistics.py -v
```

Os testes de estatística cobrem conversão de dados, cálculo das métricas, tratamento de valores nulos, detecção de outliers e geração dos arquivos de gráfico.

---

## Possíveis evoluções

- Criar alertas quando temperatura ou pH saírem de faixas definidas
- Agendar execuções automáticas do pipeline
- Criar dashboard para visualização dos relatórios
- Expor os resultados com uma API em FastAPI
- Mover credenciais e configurações do banco para variáveis de ambiente
