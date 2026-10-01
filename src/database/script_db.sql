CREATE DATABASE walter;
GO

USE walter;
GO

BEGIN TRANSACTION;

-- TABELA: CLIENTES
CREATE TABLE cliente (
    idCliente INT IDENTITY(1,1) PRIMARY KEY,
    nomeCliente VARCHAR(100) NOT NULL,
    phCliente VARCHAR(100) NOT NULL,
    temperaturaCliente VARCHAR(100) NOT NULL,
);


-- TABELA: PROJETOS
CREATE TABLE projeto (
    idProjeto INT IDENTITY(1,1) PRIMARY KEY,
    codigoProjeto VARCHAR(50) NOT NULL,
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


-- TABELA: LEITURA
CREATE TABLE leitura (
    entry_ID INT IDENTITY(1,1) PRIMARY KEY,
    dataHora DATETIME NOT NULL,
    temperatura DECIMAL(5,2),
    ph DECIMAL(5,2),

    -- FK: relaciona Leitura com Projeto
    idProjeto INT NOT NULL,

    CONSTRAINT fkLeiturasProjetos
        FOREIGN KEY (idProjeto)
        REFERENCES projeto(idProjeto)
);


INSERT INTO cliente (nomeCliente, phCliente, temperaturaCliente) VALUES
    ('Vila', 5.87, 28.3),
    ('Joana', 5.10, 26.9),
    ('Dalas', 4.48, 27.9),
    ('Fonte Paraíso', 5.30, 19.8),
    ('Fonte Mineralba', 8.26, 23.8);


INSERT INTO projeto (codigoProjeto, nomeProjeto, descricao, latitude, longitude, createdAd, updatedAt, fkCliente) VALUES
    ('2412377', 'QMStation1', 'Testes de conectividade e usabilidade para estação remota de monitoramento da qualidade da água', '37.424946', '-79.191969', '2024-01-25T14:16:26Z', '2024-03-18T13:07:02Z', 1);


COMMIT TRANSACTION;
GO

-- ROLLBACK TRANSACTION;

-- SELECT * FROM cliente; 
-- SELECT * FROM leitura; 
-- SELECT * FROM projeto; 