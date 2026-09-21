CREATE DATABASE walter;
GO

USE walter;
GO

BEGIN TRANSACTION;

CREATE TABLE ph (
    idPh INT IDENTITY(1,1) PRIMARY KEY,
    valor FLOAT NOT NULL,
    data_hora DATETIME NOT NULL
);

CREATE TABLE temperatura (
    idTemperatura INT IDENTITY(1,1) PRIMARY KEY,
    valor FLOAT NOT NULL,
    data_hora DATETIME NOT NULL,
    ph_field_temperatura INT NOT NULL,

    CONSTRAINT FK_temperatura_ph
        FOREIGN KEY (ph_field_temperatura)
        REFERENCES ph(idPh)
);

CREATE TABLE oxigenio (
    idOxigenio INT IDENTITY(1,1) PRIMARY KEY,
    valor FLOAT NOT NULL,
    data_hora DATETIME NOT NULL,
    ph_field_oxigenio INT NOT NULL,

    CONSTRAINT FK_oxigenio_ph
        FOREIGN KEY (ph_field_oxigenio)
        REFERENCES ph(idPh)
);

COMMIT TRANSACTION;
GO

--ROLLBACK TRANSACTION;