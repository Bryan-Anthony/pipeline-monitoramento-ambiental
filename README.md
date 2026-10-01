<div align="center">

# 🌊 Pipeline de Monitoramento Ambiental

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL%20Server-CC2927?logo=microsoftsqlserver&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?logo=pytest&logoColor=white)

</div>

Pipeline de dados desenvolvido em **Python** para ingestão, tratamento, validação, transformação, persistência e análise de dados ambientais.

O projeto utiliza dados obtidos através da **ThingSpeak API**, realiza o processamento das informações e armazena os dados em um banco de dados **SQL Server**. Após a persistência, os dados são utilizados para análises estatísticas, identificação de outliers e geração de gráficos e relatórios.

---

## 📦 O Produto

O resultado final é um **relatório de monitoramento ambiental** gerado automaticamente a partir das leituras da estação `QMStation1`.

O projeto trabalha com dados de monitoramento ambiental, incluindo informações de **temperatura e pH**.

---

## 🔄 Fluxo do Pipeline

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

| Etapa | Descrição |
|---|---|
| 1️⃣ **Coleta** | Consulta a API ThingSpeak, canal `2412377`, e recebe as últimas leituras da estação. |
| 2️⃣ **Tratamento** | Converte temperatura e pH para números, transforma valores inválidos em nulos e ajusta data e hora. |
| 3️⃣ **Validação** | Verifica se existem dados, se a coluna de data está presente e se há datas válidas. |
| 4️⃣ **Persistência** | Grava as leituras no SQL Server. |
| 5️⃣ **Análise** | Calcula estatísticas descritivas e identifica outliers pelo método IQR. |
| 6️⃣ **Entrega** | Gera gráficos PNG e um diagnóstico textual. |

---

## 🛠️ Tecnologias

| Tecnologia | Aplicação no projeto |
|---|---|
| **Python** | Linguagem principal do pipeline |
| **Requests** | Consumo da API ThingSpeak |
| **Pandas** e **NumPy** | Tratamento, transformação e análise dos dados |
| **Matplotlib** | Geração dos gráficos |
| **SQL Server** | Armazenamento das leituras e dados de referência |
| **PyODBC** | Conexão do Python com o SQL Server |
| **Pytest** | Testes automatizados |
| **Git** e **GitHub** | Versionamento e colaboração |

---

## 📁 Estrutura de pastas

```text
pipeline-monitoramento-ambiental/
├── main.py                          # Executa o pipeline completo
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

## 🗄️ Banco de Dados

O projeto utiliza **Microsoft SQL Server** para persistência dos dados.

O banco possui tabelas relacionadas ao monitoramento ambiental e às águas utilizadas como referência para comparação.

### Script de criação do banco

```text
src/database/script_db.sql
```

A comunicação com o banco é realizada através do **PyODBC**.

---

## 📊 Análise e Resultados

Após o processamento e persistência dos dados, o projeto realiza análises estatísticas de:

- Temperatura
- pH

São calculadas medidas como:

- Média
- Mediana
- Desvio padrão
- Quartis
- Mínimo e máximo
- Intervalo interquartil (IQR)

Também é realizada a identificação de possíveis outliers utilizando o método IQR.

---

## 📄 Arquivos Gerados

Os resultados das análises são armazenados na pasta `reports/`.

Entre os resultados estão:

- Histogramas
- Boxplots
- Gráficos comparativos
- Relatório de diagnóstico em `.txt`

---

## 🧪 Testes

O projeto utiliza **Pytest** para testes automatizados. Os testes estão organizados por responsabilidade:

| Arquivo | Responsabilidade |
|---|---|
| `test_api_client.py` | Testes da comunicação com a API |
| `test_statistics.py` | Testes das análises estatísticas |
| `test_transformacao.py` | Testes das transformações |
| `test_tratamento.py` | Testes do tratamento dos dados |
| `test_validacao.py` | Testes das validações |

Para executar os testes:

```bash
# Executa todos os testes
python -m pytest

# Executa mostrando os prints no terminal
python -m pytest -s

# Executa apenas os testes de estatística
python -m pytest tests/test_statistics.py -v

# Executa apenas os testes de transformação
python -m pytest tests/test_transformacao.py

# Executa apenas os testes de tratamento
python -m pytest tests/test_tratamento.py

# Executa apenas os testes de validação
python -m pytest tests/test_validacao.py
```

---

## 🚀 Como Executar

**1. Clone o repositório:**

```bash
git clone https://github.com/Bryan-Anthony/pipeline-monitoramento-ambiental.git
```

**2. Acesse a pasta:**

```bash
cd pipeline-monitoramento-ambiental
```

**3. Crie um ambiente virtual:**

```bash
python -m venv .venv
```

**4. Ative o ambiente virtual:**

```bash
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

**5. Instale as dependências:**

```bash
pip install -r requirements.txt
```

**6. Configure o banco de dados:**

Execute o script `src/database/script_db.sql` e configure a conexão com o SQL Server conforme o ambiente local.

**7. Execute o pipeline:**

```bash
python main.py
```

---

## 🎓 Conceitos aplicados

O projeto permite aplicar conceitos de:

- ETL (Extract, Transform, Load)
- Consumo de APIs
- JSON
- Manipulação de DataFrames
- Tratamento e validação de dados
- Banco de dados relacional
- SQL
- Análise estatística
- Detecção de outliers
- Visualização de dados
- Testes automatizados
- Git e GitHub
- Organização modular de projetos Python

---

## 🔮 Possíveis evoluções

- Criar alertas quando temperatura ou pH saírem de faixas definidas
- Agendar execuções automáticas do pipeline
- Criar dashboard para visualização dos relatórios
- Expor os resultados com uma API em FastAPI
- Mover credenciais e configurações do banco para variáveis de ambiente
