# Projeto exemplo: aplicação em 3 camadas com Factory e Singleton

Este projeto mostra uma aplicação simples em Python organizada em três camadas, usando Factory e Singleton para a conexão com o banco.

## O que o exemplo faz

- cadastrar produtos;
- listar produtos;
- buscar produto por ID;
- atualizar produto;
- remover produto.

## Estrutura de pastas

```text
projeto_exemplo_3_camadas_portugues/
├── banco_de_dados/
│   └── init.sql
├── docker-compose.yml
├── README.md
├── requirements.txt
└── src/
    ├── apresentacao/
    │   └── interface_terminal.py
    ├── dados/
    │   ├── conexao_factory.py
    │   ├── conexao_singleton.py
    │   └── produto_repository.py
    ├── dominio/
    │   └── produto.py
    ├── negocio/
    │   └── produto_service.py
    └── main.py
```

## Pré-requisitos

- Python 3.10 ou superior;
- Docker e Docker Compose;
- opcionalmente o DBeaver para acessar o MySQL.

## Subir o MySQL

```bash
docker compose up -d
```

O container sobe com:

- host: `127.0.0.1`
- porta: `3306`
- usuário: `root`
- senha: `labinfo`
- banco: `aplicacao`

## Instalar dependências e executar o projeto

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/main.py
```

### Windows Prompt de Comando

```bat
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python src/main.py
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

## Conexão no DBeaver

Use estes dados:

- host: `localhost`
- porta: `3306`
- database: `aplicacao`
- username: `root`
- password: `labinfo`

## Como o projeto se organiza

### `src/apresentacao`
Camada de interface com o usuário. Lê entradas e mostra saídas no terminal.

### `src/negocio`
Camada de regras de negócio. Valida nome, preço e IDs.

### `src/dados`
Camada de acesso a dados. Cria a conexão, executa SQL e persiste produtos.

### `src/dominio`
Entidades do domínio da aplicação.

## Factory e Singleton

### Factory

Arquivo: `src/dados/conexao_factory.py`

Centraliza a criação da conexão com o MySQL.

### Singleton

Arquivo: `src/dados/conexao_singleton.py`

Garante que a aplicação reutilize uma única conexão durante a execução.

## Observações

- A tabela `produtos` é criada pelo `init.sql` do container e também é garantida pelo repositório ao iniciar a aplicação.
- O exemplo mantém SQL cru para facilitar o uso em aula e a comparação entre as camadas.
