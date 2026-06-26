"""
interface_bibliotecario.py — Dashboard do Bibliotecário (US12, US13, US14, US15, US11)

Cards: Títulos no Acervo | Exemplares Disponíveis | Empréstimos Ativos | Em Atraso
Abas:  Acervo | Empréstimos | Atrasos | Histórico
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date

from apresentacao.estilos import (
    COR_FUNDO_INTERNO, COR_DOURADO, COR_TEXTO_ESCURO, COR_TEXTO_SECUNDARIO,
    COR_VERMELHO, COR_AMARELO, FONTE_LABEL, FONTE_CAMPO, FONTE_BOTAO, FONTE_TABELA,
)
from apresentacao.componentes import (
    montar_header, montar_card_stat, montar_abas,
    botao_principal, botao_secundario, separador, treeview_estilizado,
)


def mostrar_interface_bibliotecario(root, usuario, usuario_service,
                                     livro_service=None, emprestimo_service=None):
    for w in root.winfo_children():
        w.destroy()

    root.configure(bg=COR_FUNDO_INTERNO)
    root.geometry("1100x720")
    root.title("Biblioteca Central — Bibliotecário")

    def sair():
        from apresentacao.login import mostrar_login
        mostrar_login(root, usuario_service)

    # Header com badge ADMINISTRAÇÃO
    header = montar_header(root, usuario, sair)
    tk.Label(header, text="ADMINISTRAÇÃO", font=("Arial", 8, "bold"),
             bg=COR_DOURADO, fg="white", padx=6, pady=2).place(x=230, rely=0.5, anchor="w")

    tk.Frame(root, height=2, bg=COR_DOURADO).pack(fill="x")

    corpo = tk.Frame(root, bg=COR_FUNDO_INTERNO)
    corpo.pack(fill="both", expand=True, padx=30, pady=20)

    # --- Cards ---------------------------------------------------------------
    frame_cards = tk.Frame(corpo, bg=COR_FUNDO_INTERNO)
    frame_cards.pack(fill="x", pady=(0, 16))

    todos_livros  = livro_service.listar_livros() if livro_service else []
    indisponiveis = livro_service.listar_indisponiveis() if livro_service else []
    atrasados     = emprestimo_service.listar_emprestimos_atrasados() if emprestimo_service else []
    disponiveis   = [l for l in todos_livros if l.disponivel]

    montar_card_stat(frame_cards, len(todos_livros),    "Títulos no Acervo",       COR_TEXTO_ESCURO)
    montar_card_stat(frame_cards, len(disponiveis),     "Exemplares Disponíveis",  "#2a6a4a")
    montar_card_stat(frame_cards, len(indisponiveis),   "Empréstimos Ativos",      "#2a4a8a")
    montar_card_stat(frame_cards, len(atrasados),       "Em Atraso",               COR_VERMELHO)

    # --- Área de conteúdo ----------------------------------------------------
    area = tk.Frame(corpo, bg=COR_FUNDO_INTERNO)
    area.pack(fill="both", expand=True)

    def limpar():
        for w in area.winfo_children():
            w.destroy()

    # ------------------------------------------------------------------
    # ABA: Acervo (US12, US13, US14)
    # ------------------------------------------------------------------
    def aba_acervo():
        limpar()

        topo = tk.Frame(area, bg=COR_FUNDO_INTERNO)
        topo.pack(fill="x", pady=(12, 6))

        # Busca
        e_busca = tk.Entry(topo, font=FONTE_CAMPO, relief="flat",
                           bg="white", fg="#888888", bd=6, width=40)
        e_busca.insert(0, "Buscar por título, autor ou ISBN...")
        e_busca.pack(side="left", ipady=5)

        botao_principal(topo, "+ Adicionar Livro",
                        lambda: popup_adicionar_livro(area, atualizar_tabela)
        ).pack(side="right")

        # Tabela
        frame_tree = tk.Frame(area, bg=COR_FUNDO_INTERNO)
        frame_tree.pack(fill="both", expand=True, pady=8)

        colunas = [
            ("titulo",  "TÍTULO",  200),
            ("autor",   "AUTOR",   160),
            ("isbn",    "ISBN",    140),
            ("genero",  "GÊNERO",   80),
            ("id",      "ID",       40),
        ]
        tree = treeview_estilizado(frame_tree, colunas, altura=14)

        def atualizar_tabela(termo=""):
            tree.delete(*tree.get_children())
            livros = livro_service.listar_livros() if livro_service else []
            if termo and termo != "Buscar por título, autor ou ISBN...":
                livros = [l for l in livros if
                          termo.lower() in l.titulo.lower() or
                          termo.lower() in l.autor.lower() or
                          termo.lower() in l.isbn.lower()]
            for l in livros:
                tree.insert("", tk.END, iid=str(l.id), values=(
                    l.titulo, l.autor, l.isbn, l.genero, l.id
                ))

        e_busca.bind("<Return>", lambda ev: atualizar_tabela(e_busca.get()))
        e_busca.bind("<FocusIn>", lambda ev: (
            e_busca.delete(0, tk.END) or e_busca.configure(fg="#333333")
        ) if e_busca.get() == "Buscar por título, autor ou ISBN..." else None)

        # Rodapé com ações
        rodape = tk.Frame(area, bg=COR_FUNDO_INTERNO)
        rodape.pack(fill="x", pady=6)

        def remover():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione um livro.")
                return
            if not messagebox.askyesno("Confirmar", "Remover este livro do acervo?"):
                return
            try:
                id_livro = int(sel[0])
                tem_emp  = emprestimo_service.livro_tem_emprestimo_ativo(id_livro) if emprestimo_service else False
                tem_res  = emprestimo_service.livro_tem_reserva_ativa(id_livro)    if emprestimo_service else False
                livro_service.remover_livro(id_livro, tem_emp, tem_res)
                messagebox.showinfo("Sucesso", "Livro removido do acervo com sucesso.")
                atualizar_tabela()
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

        def editar():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione um livro para editar.")
                return
            id_livro = int(sel[0])
            livro    = livro_service.buscar_por_id(id_livro) if livro_service else None
            if livro:
                popup_editar_livro(area, livro, atualizar_tabela)

        botao_secundario(rodape, "✏  Editar Selecionado", editar).pack(side="left", padx=(0, 8))
        botao_secundario(rodape, "🗑  Remover Selecionado", remover).pack(side="left")

        atualizar_tabela()

    # ------------------------------------------------------------------
    # ABA: Empréstimos ativos
    # ------------------------------------------------------------------
    def aba_emprestimos():
        limpar()
        frame = tk.Frame(area, bg=COR_FUNDO_INTERNO)
        frame.pack(fill="both", expand=True, pady=12)

        colunas = [
            ("id",       "ID",         50),
            ("aluno",    "Aluno",      200),
            ("livro",    "Título",     240),
            ("data_emp", "Emprestado", 110),
            ("devolucao","Devolver",   110),
            ("renovado", "Renovado",    70),
        ]
        tree = treeview_estilizado(frame, colunas)

        indisponiveis = livro_service.listar_indisponiveis() if livro_service else []
        if not indisponiveis:
            tk.Label(frame, text="Nenhum empréstimo ativo no momento.",
                     font=FONTE_TABELA, bg=COR_FUNDO_INTERNO,
                     fg=COR_TEXTO_SECUNDARIO).pack(pady=40)
            return

        todos_emp = emprestimo_service.repositorio_emprestimo.listar_todos() if emprestimo_service else []
        ids_indisp = {l.id for l in indisponiveis}
        ativos = [e for e in todos_emp if e.id_livro in ids_indisp]

        for emp in ativos:
            u = usuario_service.buscar_por_id(emp.id_usuario)
            l = livro_service.buscar_por_id(emp.id_livro) if livro_service else None
            tree.insert("", tk.END, values=(
                emp.id,
                u.nome if u else f"#{emp.id_usuario}",
                l.titulo if l else f"#{emp.id_livro}",
                emp.data_emprestimo,
                emp.data_devolucao,
                "Sim" if emp.renovado else "Não",
            ))

    # ------------------------------------------------------------------
    # ABA: Atrasos (US15)
    # ------------------------------------------------------------------
    def aba_atrasos():
        limpar()
        frame = tk.Frame(area, bg=COR_FUNDO_INTERNO)
        frame.pack(fill="both", expand=True, pady=12)

        colunas = [
            ("id",       "ID Emp.",    60),
            ("aluno",    "Aluno",     200),
            ("livro",    "Título",    220),
            ("devolucao","Devolver",  110),
            ("atraso",   "Dias Atraso", 80),
        ]
        tree = treeview_estilizado(frame, colunas)

        atrasados = emprestimo_service.listar_emprestimos_atrasados() if emprestimo_service else []
        if not atrasados:
            tk.Label(frame, text="Nenhum livro atrasado no momento.",
                     font=FONTE_TABELA, bg=COR_FUNDO_INTERNO,
                     fg=COR_TEXTO_SECUNDARIO).pack(pady=40)
            return

        for item in atrasados:
            emp = item["emprestimo"]
            u   = item["usuario"]
            l   = livro_service.buscar_por_id(emp.id_livro) if livro_service else None
            tree.insert("", tk.END, values=(
                emp.id,
                u.nome if u else f"#{emp.id_usuario}",
                l.titulo if l else f"#{emp.id_livro}",
                emp.data_devolucao,
                item["dias_atraso"],
            ))

    # ------------------------------------------------------------------
    # ABA: Histórico (US11)
    # ------------------------------------------------------------------
    def aba_historico():
        limpar()
        frame = tk.Frame(area, bg=COR_FUNDO_INTERNO)
        frame.pack(fill="both", expand=True, pady=12)

        busca_frame = tk.Frame(frame, bg=COR_FUNDO_INTERNO)
        busca_frame.pack(fill="x", pady=(0, 10))

        tk.Label(busca_frame, text="Buscar aluno (nome):", font=FONTE_LABEL,
                 bg=COR_FUNDO_INTERNO).pack(side="left", padx=(0, 8))
        e_aluno = tk.Entry(busca_frame, font=FONTE_CAMPO, relief="solid", bd=1, width=30)
        e_aluno.pack(side="left")

        colunas = [
            ("aluno",    "Aluno",       180),
            ("livro",    "Título",      220),
            ("data_emp", "Emprestado",  110),
            ("devolucao","Devolvido",   110),
            ("renovado", "Renovado",     70),
        ]
        tree = treeview_estilizado(frame, colunas, altura=13)

        def buscar():
            tree.delete(*tree.get_children())
            nome = e_aluno.get().strip()
            if not nome:
                messagebox.showwarning("Aviso", "Informe um nome para buscar.")
                return
            usuarios_enc = usuario_service.buscar_por_nome(nome)
            if not usuarios_enc:
                messagebox.showinfo("Busca", "Nenhum aluno encontrado.")
                return
            for u in usuarios_enc:
                emprestimos = emprestimo_service.historico_por_usuario(u.id) if emprestimo_service else []
                for emp in emprestimos:
                    l = livro_service.buscar_por_id(emp.id_livro) if livro_service else None
                    tree.insert("", tk.END, values=(
                        u.nome,
                        l.titulo if l else f"#{emp.id_livro}",
                        emp.data_emprestimo,
                        emp.data_devolucao,
                        "Sim" if emp.renovado else "Não",
                    ))

        botao_secundario(busca_frame, "Buscar", buscar).pack(side="left", padx=8)

    # --- Abas ----------------------------------------------------------------
    montar_abas(corpo, [
        ("Acervo",      aba_acervo),
        ("Empréstimos", aba_emprestimos),
        (f"Atrasos {len(atrasados) if atrasados else ''}", aba_atrasos),
        ("Histórico",   aba_historico),
    ], COR_FUNDO_INTERNO)

    separador(corpo)
    aba_acervo()


# =============================================================================
# Popup: Adicionar Livro
# =============================================================================
def popup_adicionar_livro(pai, ao_salvar, livro_service=None):
    popup = tk.Toplevel(pai)
    popup.title("Adicionar Novo Livro")
    popup.configure(bg="white")
    popup.resizable(False, False)
    popup.geometry("440x540")
    popup.grab_set()

    tk.Label(popup, text="Adicionar Novo Livro", font=("Georgia", 15, "bold"),
             bg="white").pack(anchor="w", padx=24, pady=(20, 4))

    corpo = tk.Frame(popup, bg="white")
    corpo.pack(fill="both", expand=True, padx=24)

    campos = {}
    definicoes = [
        ("titulo",      "TÍTULO *",      "Título do livro"),
        ("autor",       "AUTOR *",       "Nome do autor"),
        ("isbn",        "ISBN *",        "ex: 978-85-359-0277-5"),
        ("genero",      "GÊNERO",        "ex: Romance"),
    ]
    for chave, rotulo, placeholder in definicoes:
        tk.Label(corpo, text=rotulo, font=("Arial", 9, "bold"),
                 bg="white", fg="#333333").pack(anchor="w", pady=(12, 2))
        e = tk.Entry(corpo, font=("Arial", 11), relief="solid", bd=1)
        e.insert(0, placeholder)
        e.configure(fg="grey")
        e.bind("<FocusIn>",  lambda ev, en=e, ph=placeholder: (en.delete(0, tk.END) or en.configure(fg="black")) if en.get() == ph else None)
        e.bind("<FocusOut>", lambda ev, en=e, ph=placeholder: (en.insert(0, ph) or en.configure(fg="grey")) if not en.get() else None)
        e.pack(fill="x", ipady=6)
        campos[chave] = e

    rodape = tk.Frame(popup, bg="white")
    rodape.pack(fill="x", padx=24, pady=20)

    def salvar():
        vals = {k: v.get().strip() for k, v in campos.items()}
        placeholders = {"Título do livro", "Nome do autor", "ex: 978-85-359-0277-5", "ex: Romance"}
        for k, v in vals.items():
            if v in placeholders:
                vals[k] = ""
        try:
            if livro_service:
                livro_service.cadastrar_livro(vals["titulo"], vals["autor"], vals["genero"], vals["isbn"])
            messagebox.showinfo("Sucesso", "Livro adicionado ao acervo com sucesso!")
            if ao_salvar:
                ao_salvar()
            popup.destroy()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    tk.Button(rodape, text="Adicionar", command=salvar,
              bg=COR_DOURADO, fg="white", font=("Arial", 11, "bold"),
              relief="flat", cursor="hand2", padx=20, pady=8).pack(side="left")
    tk.Button(rodape, text="Cancelar", command=popup.destroy,
              bg="white", fg="#444444", font=("Arial", 11),
              relief="flat", cursor="hand2").pack(side="left", padx=12)


# =============================================================================
# Popup: Editar Livro
# =============================================================================
def popup_editar_livro(pai, livro, ao_salvar, livro_service=None):
    popup = tk.Toplevel(pai)
    popup.title("Editar Livro")
    popup.configure(bg="white")
    popup.resizable(False, False)
    popup.geometry("440x480")
    popup.grab_set()

    tk.Label(popup, text="Editar Livro", font=("Georgia", 15, "bold"),
             bg="white").pack(anchor="w", padx=24, pady=(20, 4))

    corpo = tk.Frame(popup, bg="white")
    corpo.pack(fill="both", expand=True, padx=24)

    campos = {}
    definicoes = [
        ("titulo", "TÍTULO *",  livro.titulo),
        ("autor",  "AUTOR *",   livro.autor),
        ("isbn",   "ISBN *",    livro.isbn),
        ("genero", "GÊNERO",    livro.genero),
    ]
    for chave, rotulo, valor in definicoes:
        tk.Label(corpo, text=rotulo, font=("Arial", 9, "bold"),
                 bg="white", fg="#333333").pack(anchor="w", pady=(12, 2))
        e = tk.Entry(corpo, font=("Arial", 11), relief="solid", bd=1)
        e.insert(0, valor)
        e.pack(fill="x", ipady=6)
        campos[chave] = e

    rodape = tk.Frame(popup, bg="white")
    rodape.pack(fill="x", padx=24, pady=20)

    def salvar():
        try:
            if livro_service:
                livro_service.atualizar_livro(
                    livro.id,
                    campos["titulo"].get().strip(),
                    campos["autor"].get().strip(),
                    campos["genero"].get().strip(),
                    campos["isbn"].get().strip(),
                )
            messagebox.showinfo("Sucesso", "Dados do livro atualizados com sucesso.")
            if ao_salvar:
                ao_salvar()
            popup.destroy()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    tk.Button(rodape, text="Salvar", command=salvar,
              bg=COR_DOURADO, fg="white", font=("Arial", 11, "bold"),
              relief="flat", cursor="hand2", padx=20, pady=8).pack(side="left")
    tk.Button(rodape, text="Cancelar", command=popup.destroy,
              bg="white", fg="#444444", font=("Arial", 11),
              relief="flat", cursor="hand2").pack(side="left", padx=12)