"""
interface_bolsista.py — Dashboard do Bolsista (US06, US07, US08, US09)

Cards: Solicitações Pendentes | Empréstimos Ativos | Em Atraso | Indisponíveis | Reservas Ativas
Abas:  Solicitações Pendentes | Registrar Empréstimo | Renovar Empréstimo |
       Registrar Devolução | Livros Indisponíveis | Meus Registros
"""

import tkinter as tk
from tkinter import messagebox
from datetime import date

from apresentacao.estilos import (
    COR_FUNDO_INTERNO, COR_DOURADO, COR_TEXTO_ESCURO, COR_TEXTO_SECUNDARIO,
    COR_VERMELHO, COR_AMARELO, FONTE_LABEL, FONTE_CAMPO, FONTE_TABELA,
)
from apresentacao.componentes import (
    montar_header, montar_card_stat, montar_abas,
    botao_principal, botao_secundario, separador, treeview_estilizado,
)


def mostrar_interface_bolsista(root, usuario, usuario_service,
                                livro_service=None, emprestimo_service=None):
    for w in root.winfo_children():
        w.destroy()

    root.configure(bg=COR_FUNDO_INTERNO)
    root.geometry("1080x700")
    root.title("Biblioteca Central — Bolsista")

    def sair():
        from apresentacao.login import mostrar_login
        mostrar_login(root, usuario_service)

    montar_header(root, usuario, sair)
    tk.Frame(root, height=2, bg=COR_DOURADO).pack(fill="x")

    corpo = tk.Frame(root, bg=COR_FUNDO_INTERNO)
    corpo.pack(fill="both", expand=True, padx=30, pady=20)

    # --- Cards de resumo -----------------------------------------------------
    frame_cards = tk.Frame(corpo, bg=COR_FUNDO_INTERNO)
    frame_cards.pack(fill="x", pady=(0, 20))

    hoje_str = str(date.today())
    atrasados_lista = emprestimo_service.listar_emprestimos_atrasados() if emprestimo_service else []
    indisponiveis   = livro_service.listar_indisponiveis() if livro_service else []

    montar_card_stat(frame_cards, 0,                        "Solicitações Pendentes", COR_TEXTO_ESCURO)
    montar_card_stat(frame_cards, len(indisponiveis),       "Empréstimos Ativos",     "#2a4a8a")
    montar_card_stat(frame_cards, len(atrasados_lista),     "Em Atraso",              COR_VERMELHO)
    montar_card_stat(frame_cards, len(indisponiveis),       "Livros Indisponíveis",   COR_AMARELO)
    montar_card_stat(frame_cards, 0,                        "Reservas Ativas",        "#3a7a5a")

    # --- Área de conteúdo das abas -------------------------------------------
    area = tk.Frame(corpo, bg=COR_FUNDO_INTERNO)
    area.pack(fill="both", expand=True)

    def limpar():
        for w in area.winfo_children():
            w.destroy()

    # ------------------------------------------------------------------
    # ABA: Solicitações Pendentes
    # ------------------------------------------------------------------
    def aba_solicitacoes():
        limpar()
        tk.Label(area, text="Nenhuma solicitação pendente no momento.",
                 font=FONTE_TABELA, bg=COR_FUNDO_INTERNO,
                 fg=COR_TEXTO_SECUNDARIO).pack(pady=40)

    # ------------------------------------------------------------------
    # ABA: Registrar Empréstimo (US06)
    # ------------------------------------------------------------------
    def aba_registrar_emprestimo():
        limpar()
        frame = tk.Frame(area, bg=COR_FUNDO_INTERNO)
        frame.pack(fill="x", pady=20)

        def campo(rotulo, placeholder):
            tk.Label(frame, text=rotulo, font=FONTE_LABEL,
                     bg=COR_FUNDO_INTERNO, fg="#555555").pack(anchor="w", pady=(12, 3))
            e = tk.Entry(frame, font=FONTE_CAMPO, relief="solid", bd=1, bg="white")
            e.insert(0, placeholder)
            e.configure(fg="#aaaaaa")
            e.bind("<FocusIn>",  lambda ev, en=e, ph=placeholder: (en.delete(0, tk.END) or en.configure(fg="#333333")) if en.get() == ph else None)
            e.bind("<FocusOut>", lambda ev, en=e, ph=placeholder: (en.insert(0, ph) or en.configure(fg="#aaaaaa")) if not en.get() else None)
            e.pack(fill="x", ipady=7)
            return e

        e_usuario = campo("ID DO ALUNO", "Digite o ID do aluno")
        e_livro   = campo("ID DO LIVRO", "Digite o ID do livro")

        def registrar():
            try:
                id_u = int(e_usuario.get())
                id_l = int(e_livro.get())
                emp  = emprestimo_service.realizar_emprestimo(id_u, id_l)
                messagebox.showinfo("Sucesso",
                    f"Empréstimo registrado!\nDevolução prevista: {emp.data_devolucao}")
                aba_registrar_emprestimo()
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

        botao_principal(frame, "Registrar Empréstimo", registrar).pack(pady=16)

    # ------------------------------------------------------------------
    # ABA: Renovar Empréstimo (US07)
    # ------------------------------------------------------------------
    def aba_renovar():
        limpar()
        frame = tk.Frame(area, bg=COR_FUNDO_INTERNO)
        frame.pack(fill="x", pady=20)

        tk.Label(frame, text="ID DO EMPRÉSTIMO", font=FONTE_LABEL,
                 bg=COR_FUNDO_INTERNO, fg="#555555").pack(anchor="w", pady=(12, 3))
        e_id = tk.Entry(frame, font=FONTE_CAMPO, relief="solid", bd=1, bg="white")
        e_id.pack(fill="x", ipady=7)

        def renovar():
            try:
                emp = emprestimo_service.renovar_emprestimo(int(e_id.get()))
                messagebox.showinfo("Sucesso",
                    f"Empréstimo renovado!\nNova data de devolução: {emp.data_devolucao}")
                aba_renovar()
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

        botao_principal(frame, "Renovar Empréstimo", renovar).pack(pady=16)

    # ------------------------------------------------------------------
    # ABA: Registrar Devolução (US08)
    # ------------------------------------------------------------------
    def aba_devolucao():
        limpar()
        frame = tk.Frame(area, bg=COR_FUNDO_INTERNO)
        frame.pack(fill="x", pady=20)

        tk.Label(frame, text="ID DO EMPRÉSTIMO", font=FONTE_LABEL,
                 bg=COR_FUNDO_INTERNO, fg="#555555").pack(anchor="w", pady=(12, 3))
        e_id = tk.Entry(frame, font=FONTE_CAMPO, relief="solid", bd=1, bg="white")
        e_id.pack(fill="x", ipady=7)

        def devolver():
            try:
                resultado = emprestimo_service.registrar_devolucao(int(e_id.get()))
                if resultado["atrasado"]:
                    messagebox.showwarning("Devolução com Atraso",
                        f"Devolução realizada com atraso de {resultado['dias_atraso']} dia(s).")
                else:
                    messagebox.showinfo("Sucesso", "Devolução registrada com sucesso!")
                aba_devolucao()
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

        botao_principal(frame, "Registrar Devolução", devolver).pack(pady=16)

    # ------------------------------------------------------------------
    # ABA: Livros Indisponíveis (US09)
    # ------------------------------------------------------------------
    def aba_indisponiveis():
        limpar()
        frame = tk.Frame(area, bg=COR_FUNDO_INTERNO)
        frame.pack(fill="both", expand=True, pady=12)

        colunas = [
            ("id",      "ID",     50),
            ("titulo",  "Título", 280),
            ("autor",   "Autor",  180),
            ("genero",  "Gênero", 100),
        ]
        tree = treeview_estilizado(frame, colunas, altura=14)

        livros = livro_service.listar_indisponiveis() if livro_service else []
        if not livros:
            messagebox.showinfo("Livros Indisponíveis", "Todos os livros estão disponíveis no momento.")
            return

        for l in livros:
            tree.insert("", tk.END, values=(l.id, l.titulo, l.autor, l.genero))

    # ------------------------------------------------------------------
    # ABA: Meus Registros (atrasados — US15 simplificado)
    # ------------------------------------------------------------------
    def aba_meus_registros():
        limpar()
        frame = tk.Frame(area, bg=COR_FUNDO_INTERNO)
        frame.pack(fill="both", expand=True, pady=12)

        colunas = [
            ("id",       "ID Emp.", 60),
            ("aluno",    "Aluno",   180),
            ("livro",    "Livro",   220),
            ("devolucao","Devolver até", 110),
            ("atraso",   "Dias Atraso",  80),
        ]
        tree = treeview_estilizado(frame, colunas, altura=14)

        atrasados = emprestimo_service.listar_emprestimos_atrasados() if emprestimo_service else []
        if not atrasados:
            tk.Label(frame, text="Nenhum livro atrasado no momento.",
                     font=FONTE_TABELA, bg=COR_FUNDO_INTERNO,
                     fg=COR_TEXTO_SECUNDARIO).pack(pady=40)
            return

        for item in atrasados:
            emp     = item["emprestimo"]
            usuario_emp = item["usuario"]
            livro   = livro_service.buscar_por_id(emp.id_livro) if livro_service else None
            tree.insert("", tk.END, values=(
                emp.id,
                usuario_emp.nome if usuario_emp else f"#{emp.id_usuario}",
                livro.titulo if livro else f"#{emp.id_livro}",
                emp.data_devolucao,
                item["dias_atraso"],
            ))

    # --- Montar abas ---------------------------------------------------------
    montar_abas(corpo, [
        ("Solicitações Pendentes", aba_solicitacoes),
        ("Registrar Empréstimo",   aba_registrar_emprestimo),
        ("Renovar Empréstimo",     aba_renovar),
        ("Registrar Devolução",    aba_devolucao),
        ("Livros Indisponíveis",   aba_indisponiveis),
        ("Meus Registros",         aba_meus_registros),
    ], COR_FUNDO_INTERNO)

    separador(corpo)
    aba_solicitacoes()