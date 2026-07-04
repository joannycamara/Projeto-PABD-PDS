CREATE DATABASE IF NOT EXISTS biblioteca;
USE biblioteca;

CREATE TABLE IF NOT EXISTS usuarios (
    id    INT AUTO_INCREMENT PRIMARY KEY,
    nome  VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    tipo  ENUM('aluno', 'bolsista', 'bibliotecario') NOT NULL
);

-- Um TÍTULO é a ficha bibliográfica (o "livro" em si): título, autor, gênero, ISBN.
-- Um EXEMPLAR é uma cópia física daquele título. Um mesmo título pode ter
-- vários exemplares (cada um com sua própria disponibilidade).
CREATE TABLE IF NOT EXISTS titulos (
    id     INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    autor  VARCHAR(100),
    genero VARCHAR(50),
    isbn   VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS exemplares (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    id_titulo  INT NOT NULL,
    disponivel BOOLEAN DEFAULT TRUE,

    FOREIGN KEY (id_titulo) REFERENCES titulos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS emprestimos (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario       INT NOT NULL,
    id_livro         INT NOT NULL,  -- referencia exemplares.id (uma cópia específica)
    data_emprestimo  DATE NOT NULL,
    data_devolucao   DATE NULL,
    renovado         BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    FOREIGN KEY (id_livro)   REFERENCES exemplares(id)
);

CREATE TABLE IF NOT EXISTS reservas (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario   INT NOT NULL,
    id_livro     INT NOT NULL,  -- referencia exemplares.id (uma cópia específica)
    data_reserva DATE NOT NULL,
    ativa        BOOLEAN DEFAULT TRUE,

    FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    FOREIGN KEY (id_livro)   REFERENCES exemplares(id)
);