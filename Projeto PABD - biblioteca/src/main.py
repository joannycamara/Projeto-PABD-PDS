"""
main.py — Ponto de entrada da aplicação Biblioteca Central.
"""

import tkinter as tk

from dados.conexao_singleton       import ConexaoSingleton
from dados.usuarios_repository     import UsuariosRepository
from dados.livro_repository        import LivrosRepository
from dados.emprestimo_repository   import EmprestimosRepository

from negocio.usuario_service       import UsuarioService
from negocio.livro_service         import LivroService
from negocio.emprestimo_service    import EmprestimoService

from apresentacao.login            import mostrar_login


def principal() -> None:
    conexao = ConexaoSingleton.obter_conexao(
        tipo_banco="mysql",
        host="127.0.0.1",
        porta=3306,
        usuario="root",
        senha="S@mu3l#1306",      # ← ajuste para sua senha
        banco="biblioteca",
    )

    # --- Repositórios --------------------------------------------------------
    repo_usuario    = UsuariosRepository(conexao)
    repo_livro      = LivrosRepository(conexao)
    repo_emprestimo = EmprestimosRepository(conexao)

    # --- Services ------------------------------------------------------------
    usuario_service    = UsuarioService(repo_usuario)
    livro_service      = LivroService(repo_livro)
    emprestimo_service = EmprestimoService(repo_emprestimo, repo_livro, repo_usuario)

    # --- Injeta services nas telas -------------------------------------------
    import apresentacao.interface_aluno          as _ia
    import apresentacao.interface_bolsista       as _ib
    import apresentacao.interface_bibliotecario  as _ibi

    _orig_aluno = _ia.mostrar_interface_aluno
    def _aluno_injetado(root, usuario, us):
        _orig_aluno(root, usuario, us, livro_service, emprestimo_service)
    _ia.mostrar_interface_aluno = _aluno_injetado

    _orig_bolsista = _ib.mostrar_interface_bolsista
    def _bolsista_injetado(root, usuario, us):
        _orig_bolsista(root, usuario, us, livro_service, emprestimo_service)
    _ib.mostrar_interface_bolsista = _bolsista_injetado

    _orig_biblio = _ibi.mostrar_interface_bibliotecario
    def _biblio_injetado(root, usuario, us):
        _orig_biblio(root, usuario, us, livro_service, emprestimo_service)
    _ibi.mostrar_interface_bibliotecario = _biblio_injetado

    # --- Janela principal ----------------------------------------------------
    root = tk.Tk()
    root.title("Biblioteca Central")
    root.resizable(True, True)

    mostrar_login(root, usuario_service)

    try:
        root.mainloop()
    finally:
        ConexaoSingleton.fechar_conexao()


if __name__ == "__main__":
    principal()