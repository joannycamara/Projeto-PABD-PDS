CREATE DATABASE IF NOT EXISTS biblioteca;
USE biblioteca;

CREATE TABLE usuarios (
    id    INT AUTO_INCREMENT PRIMARY KEY,
    nome  VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    tipo  ENUM('aluno', 'bolsista', 'bibliotecario') NOT NULL
);

CREATE TABLE livros (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    titulo     VARCHAR(150) NOT NULL,
    autor      VARCHAR(100),
    genero     VARCHAR(50),
    isbn       VARCHAR(20) NOT NULL UNIQUE,
    disponivel BOOLEAN DEFAULT TRUE
);

CREATE TABLE emprestimos (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario       INT NOT NULL,
    id_livro         INT NOT NULL,
    data_emprestimo  DATE NOT NULL,
    data_devolucao   DATE NULL,
    renovado         BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    FOREIGN KEY (id_livro)   REFERENCES livros(id)
);

CREATE TABLE reservas (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario   INT NOT NULL,
    id_livro     INT NOT NULL,
    data_reserva DATE NOT NULL,
    ativa        BOOLEAN DEFAULT TRUE,

    FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    FOREIGN KEY (id_livro)   REFERENCES livros(id)
);