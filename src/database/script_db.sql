CREATE DATABASE walter;
GO

USE walter;
GO

BEGIN TRANSACTION;


-- TABELA: CLIENTES
CREATE TABLE cliente (
    idCliente INT IDENTITY(1,1) PRIMARY KEY,
    nomeCliente VARCHAR(100) NOT NULL,
);

-- TABELA: PROJETOS
CREATE TABLE projeto (
    idProjeto INT IDENTITY(1,1) PRIMARY KEY,
    codigoProjeto INT NOT NULL,
    nomeProjeto VARCHAR(150) NOT NULL,
    descricao VARCHAR(255),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    createdAd DATETIME DEFAULT GETDATE(),
    updatedAt DATETIME DEFAULT GETDATE(),

    -- FK: relaciona Projeto com Cliente
    fkCliente INT NOT NULL,

    CONSTRAINT fkProjetosClientes
        FOREIGN KEY (fkCliente)
        REFERENCES cliente(idCliente)
);


CREATE TABLE estacao(
    idEstacao INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(45) NOT NULL,
    municipio VARCHAR(45) NOT NULL,
    estado VARCHAR(45) NOT NULL,

    -- FK: se relaciona com Projeto
    fkProjeto INT NOT NULL

    CONSTRAINT fkEstacaoProjeto
        FOREIGN KEY(fkProjeto)
        REFERENCES projeto(idProjeto) 
);


-- TABELA: OPERADORES
CREATE TABLE operador (
    idOperador INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(11) NOT NULL UNIQUE,
    email VARCHAR(245) NOT NULL UNIQUE,
    senha CHAR(8) NOT NULL,
    ativo BIT NOT NULL DEFAULT 1,

    -- FK: se relaciona com Estacao
    fkEstacao INT NOT NULL,

    -- FK: se relaciona com Projeto
    fkProjeto INT NOT NULL,
    
    CONSTRAINT fkOperadorEstacao
        FOREIGN KEY(fkEstacao)
        REFERENCES estacao(idEstacao),

    CONSTRAINT fkOperadorProjeto
        FOREIGN KEY(fkProjeto)
        REFERENCES projeto(idProjeto) 
);


-- TABELA: PARAMETROS
CREATE TABLE parametro (
    idParametro INT IDENTITY(1,1) PRIMARY KEY,
    codigoParametro VARCHAR(30) NOT NULL UNIQUE,
    nomeParametro VARCHAR(100) NOT NULL,
    unidadePadrao VARCHAR(20) NOT NULL,

    -- FK: se relaciona com Estacao
    fkEstacao INT NOT NULL
    CONSTRAINT fkParametroEstacao
        FOREIGN KEY(fkEstacao)
        REFERENCES estacao(idEstacao),
);


-- TABELA: LEITURA
CREATE TABLE leitura (
    entry_ID INT IDENTITY(1,1) PRIMARY KEY,
    entry_id_api INT NOT NULL UNIQUE,
    dataHora DATETIME NOT NULL,

    -- Parametros medidos na leitura
    ph DECIMAL(5,2),
    temperaturaAgua DECIMAL(5,2),
    temperaturaAr DECIMAL(5,2),
    oxigenioDissolvido DECIMAL(10,4),
    condutividadeEletrica DECIMAL(10,4),
    turbidezAgua DECIMAL(10,4),
    
    -- FK: relaciona Leitura com Projeto
    idProjeto INT NOT NULL,

    -- FK: relaciona Leitura com Operador
    idOperador INT NULL,

    -- FK: se relaciona com Estacao
    fkEstacao INT NOT NULL,

    CONSTRAINT fkLeiturasProjetos
        FOREIGN KEY (idProjeto)
        REFERENCES projeto(idProjeto),

    CONSTRAINT fkLeiturasOperadores
        FOREIGN KEY (idOperador)
        REFERENCES operador(idOperador),

    CONSTRAINT fkLeituraEstacao
        FOREIGN KEY(fkEstacao)
        REFERENCES estacao(idEstacao),
);

-- INSERÇÕES: CLIENTES
INSERT INTO cliente (nomeCliente) VALUES
    ('Vila'),
    ('Joana'),
    ('Dalas'),
    ('Fonte Paraíso'),
    ('Fonte Mineralba');


-- INSERÇÕES: PROJETO
INSERT INTO projeto (codigoProjeto, nomeProjeto, descricao, latitude, longitude, createdAd, updatedAt, fkCliente) VALUES
    ('2412377', 'QMStation1', 'Testes de conectividade e usabilidade para estação remota de monitoramento da qualidade da água', '37.424946', '-79.191969', '2024-01-25T14:16:26Z', '2024-03-18T13:07:02Z', 1);

-- INSERÇÕES: ESTAÇÕES
INSERT INTO estacao (nome, municipio, estado, fkProjeto) VALUES
    ('Vila', 'Joinville', 'Santa Catarina', 1),
    ('Joana', 'A confirmar', 'A confirmar', 1),
    ('Dalas', 'Parnaguá', 'Piauí', 1),
    ('Fonte Paraiso', 'Pilar do Sul', 'São Paulo', 1),
    ('Fonte Mineralba', 'Bauru', 'São Paulo', 1);

-- INSERÇÕES: OPERADORES
INSERT INTO operador (nome, cpf, email, senha, ativo, fkEstacao, fkProjeto) VALUES
    ('Operador Vila', '00000000001', 'operador.vila@exemplo.com', 'Vila1234', 1, 1, 1),
    ('Operador Joana', '00000000002', 'operador.joana@exemplo.com', 'Joana123', 1, 2, 1),
    ('Operador Dalas', '00000000003', 'operador.dalas@exemplo.com', 'Dalas123', 1, 3, 1),
    ('Operador Fonte Paraiso', '00000000004', 'operador.paraiso@exemplo.com', 'Fonte123', 1, 4, 1),
    ('Operador Mineralba', '00000000005', 'operador.mineralba@exemplo.com', 'Miner123', 1, 5, 1);


-- INSERÇÕES: PARAMETROS
INSERT INTO parametro (codigoParametro, nomeParametro, unidadePadrao, fkEstacao) VALUES
    -- Estação 1: Vila
    ('PH_VILA', 'pH', 'adimensional', 1),
    ('TEMP_AGUA_VILA', 'Temperatura da agua', '°C', 1),
    ('TEMP_AR_VILA', 'Temperatura do ar', '°C', 1),
    ('OD_VILA', 'Oxigenio dissolvido', 'mg/L', 1),
    ('CE_VILA', 'Condutividade eletrica', 'µS/cm', 1),
    ('TURB_VILA', 'Turbidez da agua', 'NTU', 1),

    -- Estação 2: Joana
    ('PH_JOANA', 'pH', 'adimensional', 2),
    ('TEMP_AGUA_JOANA', 'Temperatura da agua', '°C', 2),
    ('TEMP_AR_JOANA', 'Temperatura do ar', '°C', 2),
    ('OD_JOANA', 'Oxigenio dissolvido', 'mg/L', 2),
    ('CE_JOANA', 'Condutividade eletrica', 'µS/cm', 2),
    ('TURB_JOANA', 'Turbidez da agua', 'NTU', 2),

    -- Estação 3: Dalas
    ('PH_DALAS', 'pH', 'adimensional', 3),
    ('TEMP_AGUA_DALAS', 'Temperatura da agua', '°C', 3),
    ('TEMP_AR_DALAS', 'Temperatura do ar', '°C', 3),
    ('OD_DALAS', 'Oxigenio dissolvido', 'mg/L', 3),
    ('CE_DALAS', 'Condutividade eletrica', 'µS/cm', 3),
    ('TURB_DALAS', 'Turbidez da agua', 'NTU', 3),

    -- Estação 4: Fonte Paraiso
    ('PH_PARAISO', 'pH', 'adimensional', 4),
    ('TEMP_AGUA_PARAISO', 'Temperatura da agua', '°C', 4),
    ('TEMP_AR_PARAISO', 'Temperatura do ar', '°C', 4),
    ('OD_PARAISO', 'Oxigenio dissolvido', 'mg/L', 4),
    ('CE_PARAISO', 'Condutividade eletrica', 'µS/cm', 4),
    ('TURB_PARAISO', 'Turbidez da agua', 'NTU', 4),

    -- Estação 5: Fonte Mineralba
    ('PH_MINERALBA', 'pH', 'adimensional', 5),
    ('TEMP_AGUA_MINERALBA', 'Temperatura da agua', '°C', 5),
    ('TEMP_AR_MINERALBA', 'Temperatura do ar', '°C', 5),
    ('OD_MINERALBA', 'Oxigenio dissolvido', 'mg/L', 5),
    ('CE_MINERALBA', 'Condutividade eletrica', 'µS/cm', 5),
    ('TURB_MINERALBA', 'Turbidez da agua', 'NTU', 5);


COMMIT TRANSACTION;
GO


-- ROLLBACK TRANSACTION;

-- SELECT * FROM cliente;
-- SELECT * FROM leitura;
-- SELECT * FROM projeto;
-- SELECT * FROM operador;
SELECT * FROM parametro;