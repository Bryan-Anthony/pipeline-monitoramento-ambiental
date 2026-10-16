
-- =========================================================
-- BANCO DE DADOS: WALTER
-- SQL Server
-- Criar estrutura nova
-- =========================================================

IF DB_ID(N'walter') IS NULL
BEGIN
    EXEC(N'CREATE DATABASE walter');
END;
GO

USE walter;
GO

SET XACT_ABORT ON;
GO

BEGIN TRY
    BEGIN TRANSACTION;

    -- =====================================================
    -- 1. CLIENTE
    -- =====================================================
    CREATE TABLE cliente (
        idCliente INT IDENTITY(1,1) PRIMARY KEY,
        nomeCliente VARCHAR(100) NOT NULL UNIQUE
    );

    -- =====================================================
    -- 2. PARAMETRO
    -- =====================================================
    CREATE TABLE parametro (
        idParametro INT IDENTITY(1,1) PRIMARY KEY,
        codigoParametro VARCHAR(30) NOT NULL UNIQUE,
        nomeParametro VARCHAR(100) NOT NULL,
        unidadePadrao VARCHAR(30) NOT NULL
    );

    -- =====================================================
    -- 3. PARAMETRO CLIENTE
    -- Um valor de referência por cliente e parâmetro.
    -- =====================================================
    CREATE TABLE parametroCliente (
        idParametroCliente INT IDENTITY(1,1) PRIMARY KEY,
        fkCliente INT NOT NULL,
        fkParametro INT NOT NULL,
        valorReferencia DECIMAL(10,2) NOT NULL,

        CONSTRAINT fkParametroClienteCliente
            FOREIGN KEY (fkCliente)
            REFERENCES cliente(idCliente),

        CONSTRAINT fkParametroClienteParametro
            FOREIGN KEY (fkParametro)
            REFERENCES parametro(idParametro),

        CONSTRAINT uqParametroCliente
            UNIQUE (fkCliente, fkParametro)
    );

    -- =====================================================
    -- 4. PROJETO
    -- Um projeto pode possuir várias estações.
    -- Os clientes são associados às estações.
    -- =====================================================
    CREATE TABLE projeto (
        idProjeto INT IDENTITY(1,1) PRIMARY KEY,
        codigoProjeto VARCHAR(50) NOT NULL UNIQUE,
        nomeProjeto VARCHAR(150) NOT NULL,
        descricao VARCHAR(255),

        createdAt DATETIME2(0) NOT NULL
            CONSTRAINT dfProjetoCreatedAt
            DEFAULT SYSUTCDATETIME(),

        updatedAt DATETIME2(0) NOT NULL
            CONSTRAINT dfProjetoUpdatedAt
            DEFAULT SYSUTCDATETIME()
    );

    -- =====================================================
    -- 5. ESTACAO
    -- Cada estação pertence a um projeto.
    -- As coordenadas identificam a localização da estação.
    -- =====================================================
    CREATE TABLE estacao (
        idEstacao INT IDENTITY(1,1) PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        municipio VARCHAR(100) NOT NULL,
        estado VARCHAR(100) NOT NULL,
        pais VARCHAR(100) NOT NULL,

        latitude DECIMAL(9,6),
        longitude DECIMAL(9,6),

        fkProjeto INT NOT NULL,

        CONSTRAINT fkEstacaoProjeto
            FOREIGN KEY (fkProjeto)
            REFERENCES projeto(idProjeto),

        CONSTRAINT ckEstacaoLatitude
            CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),

        CONSTRAINT ckEstacaoLongitude
            CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180)
    );

    -- =====================================================
    -- 6. ESTACAO CLIENTE
    -- Relacionamento muitos para muitos entre estação
    -- e cliente.
    -- =====================================================
    CREATE TABLE estacaoCliente (
        idEstacaoCliente INT IDENTITY(1,1) PRIMARY KEY,
        fkEstacao INT NOT NULL,
        fkCliente INT NOT NULL,

        CONSTRAINT fkEstacaoClienteEstacao
            FOREIGN KEY (fkEstacao)
            REFERENCES estacao(idEstacao),

        CONSTRAINT fkEstacaoClienteCliente
            FOREIGN KEY (fkCliente)
            REFERENCES cliente(idCliente),

        CONSTRAINT uqEstacaoCliente
            UNIQUE (fkEstacao, fkCliente)
    );

    -- =====================================================
    -- 7. OPERADOR
    -- A senha deve ser armazenada como hash seguro.
    -- O operador está associado a uma estação.
    -- =====================================================
    CREATE TABLE operador (
        idOperador INT IDENTITY(1,1) PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        cpf VARCHAR(11) NOT NULL UNIQUE,
        email VARCHAR(245) NOT NULL UNIQUE,
        hashSenha VARCHAR(255) NOT NULL,

        ativo BIT NOT NULL
            CONSTRAINT dfOperadorAtivo DEFAULT 1,

        fkEstacao INT NOT NULL,

        CONSTRAINT fkOperadorEstacao
            FOREIGN KEY (fkEstacao)
            REFERENCES estacao(idEstacao),

        CONSTRAINT ckOperadorCpf
            CHECK (
                LEN(cpf) = 11
                AND cpf NOT LIKE '%[^0-9]%'
            )
    );

    -- =====================================================
    -- 8. LEITURA
    -- Cada leitura pertence a uma estação.
    -- entry_id_api identifica o registro da API dentro
    -- da respectiva estação.
    -- =====================================================
    CREATE TABLE leitura (
        entry_ID INT IDENTITY(1,1) PRIMARY KEY,
        entry_id_api INT NOT NULL,
        dataHora DATETIME2(0) NOT NULL,

        ph DECIMAL(5,2),
        temperaturaAgua DECIMAL(5,2),
        temperaturaAr DECIMAL(5,2),
        oxigenioDissolvido DECIMAL(10,2),
        condutividadeEletrica DECIMAL(10,2),
        turbidezAgua DECIMAL(10,2),

        idOperador INT NULL,
        fkEstacao INT NOT NULL,

        CONSTRAINT fkLeituraOperador
            FOREIGN KEY (idOperador)
            REFERENCES operador(idOperador),

        CONSTRAINT fkLeituraEstacao
            FOREIGN KEY (fkEstacao)
            REFERENCES estacao(idEstacao),

        CONSTRAINT uqLeituraEstacaoEntry
            UNIQUE (fkEstacao, entry_id_api)
    );

    -- Índices para consultas frequentes
    CREATE INDEX ixLeituraDataHora
        ON leitura(dataHora);

    CREATE INDEX ixLeituraEstacaoData
        ON leitura(fkEstacao, dataHora);

    -- =====================================================
    -- 9. INSERÇÃO DE CLIENTES
    -- =====================================================
    INSERT INTO cliente (nomeCliente)
    VALUES
        ('Vila'),
        ('Santa Joana'),
        ('Dias Dávilas'),
        ('Fonte Paraíso'),
        ('Fonte Mineralba');

    -- =====================================================
    -- 10. INSERÇÃO DE PARÂMETROS
    -- =====================================================
    INSERT INTO parametro
        (codigoParametro, nomeParametro, unidadePadrao)
    VALUES
        ('PH',   'pH',                     'adimensional'),
        ('TA',   'Temperatura da água',    '°C'),
        ('TAR',  'Temperatura do ar',      '°C'),
        ('OD',   'Oxigênio dissolvido',     'mg/L'),
        ('CE',   'Condutividade elétrica',  'µS/cm'),
        ('TURB', 'Turbidez da água',        'NTU');

    -- =====================================================
    -- 11. VALORES DE REFERÊNCIA POR CLIENTE
    -- =====================================================
    INSERT INTO parametroCliente
        (fkCliente, fkParametro, valorReferencia)
    SELECT
        c.idCliente,
        p.idParametro,
        v.valorReferencia
    FROM (
        VALUES
            ('Vila',            'PH',    5.87),
            ('Vila',            'TA',   28.30),
            ('Vila',            'TAR',  25.00),
            ('Vila',            'OD',  111.16),
            ('Vila',            'CE',  121.30),
            ('Vila',            'TURB',  0.50),

            ('Santa Joana',     'PH',    5.10),
            ('Santa Joana',     'TA',   28.50),
            ('Santa Joana',     'TAR',  25.00),
            ('Santa Joana',     'OD',  111.16),
            ('Santa Joana',     'CE',  121.30),
            ('Santa Joana',     'TURB',  0.50),

            ('Dias Dávilas',    'PH',    4.48),
            ('Dias Dávilas',    'TA',   27.90),
            ('Dias Dávilas',    'TAR',  25.00),
            ('Dias Dávilas',    'OD',   87.88),
            ('Dias Dávilas',    'CE',  122.40),
            ('Dias Dávilas',    'TURB',  0.30),

            ('Fonte Paraíso',   'PH',    7.00),
            ('Fonte Paraíso',   'TA',   24.60),
            ('Fonte Paraíso',   'TAR',  25.00),
            ('Fonte Paraíso',   'OD',  112.16),
            ('Fonte Paraíso',   'CE',  134.30),
            ('Fonte Paraíso',   'TURB',  0.50),

            ('Fonte Mineralba', 'PH',    7.00),
            ('Fonte Mineralba', 'TA',   26.20),
            ('Fonte Mineralba', 'TAR',  28.00),
            ('Fonte Mineralba', 'OD',  115.16),
            ('Fonte Mineralba', 'CE',  131.30),
            ('Fonte Mineralba', 'TURB',  0.50)
    ) AS v(nomeCliente, codigoParametro, valorReferencia)
    INNER JOIN cliente AS c
        ON c.nomeCliente = v.nomeCliente
    INNER JOIN parametro AS p
        ON p.codigoParametro = v.codigoParametro;

    -- =====================================================
    -- 12. INSERÇÃO DO PROJETO
    -- Datas de origem fornecidas em UTC.
    -- =====================================================
    INSERT INTO projeto (
        codigoProjeto,
        nomeProjeto,
        descricao,
        createdAt,
        updatedAt
    )
    VALUES (
        '2412377',
        'WQMStation1',
        'Testes de conectividade e usabilidade para estação remota de monitoramento da qualidade da água',
        '2024-01-25T14:16:26',
        '2024-03-18T13:07:02'
    );

    -- =====================================================
    -- 13. INSERÇÃO DA ESTAÇÃO
    -- Coordenadas da estação informada pela API.
    -- =====================================================
    INSERT INTO estacao (
        nome,
        municipio,
        estado,
        pais,
        latitude,
        longitude,
        fkProjeto
    )
    VALUES (
        'Oakwood',
        'Lynchburg',
        'Virgínia (Virginia)',
        'Estados Unidos',
        37.424946,
        -79.191969,
        (
            SELECT idProjeto
            FROM projeto
            WHERE codigoProjeto = '2412377'
        )
    );

    -- =====================================================
    -- 14. ASSOCIAR A ESTAÇÃO AOS CINCO CLIENTES
    -- =====================================================
    INSERT INTO estacaoCliente (
        fkEstacao,
        fkCliente
    )
    SELECT
        e.idEstacao,
        c.idCliente
    FROM estacao AS e
    CROSS JOIN cliente AS c
    WHERE e.nome = 'Oakwood'
      AND e.fkProjeto = (
          SELECT p.idProjeto
          FROM projeto AS p
          WHERE p.codigoProjeto = '2412377'
      )
      AND c.nomeCliente IN (
          'Vila',
          'Santa Joana',
          'Dias Dávilas',
          'Fonte Paraíso',
          'Fonte Mineralba'
      );

    -- =====================================================
    -- 15. OPERADOR
    -- A inserção fica a cargo da aplicação após gerar
    -- o hash da senha.
    --
    -- Exemplo de estrutura:
    --
    -- INSERT INTO operador
    --     (nome, cpf, email, hashSenha, fkEstacao)
    -- VALUES
    --     ('José da Silva', '37362584024',
    --      '<HASH_SEGURO_GERADO_NA_APLICACAO>',
    --      (SELECT idEstacao
    --       FROM estacao
    --       WHERE nome = 'Oakwood'
    --         AND fkProjeto = (
    --             SELECT idProjeto
    --             FROM projeto
    --             WHERE codigoProjeto = '2412377'
    --         )));
    --
    -- Não armazene a senha original em hashSenha.
    -- =====================================================

    COMMIT TRANSACTION;

    PRINT 'Banco e dados iniciais criados com sucesso.';

END TRY
BEGIN CATCH
    IF XACT_STATE() <> 0
        ROLLBACK TRANSACTION;

    THROW;
END CATCH;
GO


-- =========================================================
-- 16. CONSULTAS PARA CONFERIR A ESTRUTURA E OS DADOS
-- =========================================================
SELECT * FROM cliente;
SELECT * FROM parametro;
SELECT * FROM parametroCliente;
SELECT * FROM projeto;
SELECT * FROM estacao;
SELECT * FROM estacaoCliente;
SELECT * FROM operador;
SELECT * FROM leitura;
GO

-- Conferir os cinco clientes associados à estação

SELECT
    e.idEstacao,
    e.nome AS estacao,
    p.codigoProjeto,
    c.idCliente,
    c.nomeCliente
FROM estacaoCliente AS ec
INNER JOIN estacao AS e
    ON e.idEstacao = ec.fkEstacao
INNER JOIN cliente AS c
    ON c.idCliente = ec.fkCliente
INNER JOIN projeto AS p
    ON p.idProjeto = e.fkProjeto
WHERE p.codigoProjeto = '2412377'
ORDER BY c.nomeCliente;
GO
