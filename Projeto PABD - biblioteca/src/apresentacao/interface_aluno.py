"""
interface_aluno.py — Dashboard do Aluno (US04, US05, US10, US11)

Abas: Catálogo | Meus Empréstimos | Minhas Reservas
Cards de resumo: Empréstimos Ativos | Em Atraso | Reservas Ativas
"""

import tkinter as tk
from tkinter import messagebox
from datetime import date

from apresentacao.estilos import (
    COR_FUNDO_INTERNO, COR_DOURADO, COR_TEXTO_ESCURO, COR_TEXTO_SECUNDARIO,
    COR_VERMELHO, COR_AMARELO, COR_VERDE_STATUS,
    FONTE_LABEL, FONTE_CAMPO, FONTE_BOTAO, FONTE_TABELA,
)
from apresentacao.componentes import (
    montar_header, montar_card_stat, montar_abas,
    botao_principal, separador, treeview_estilizado,
)


def mostrar_interface_aluno(root, usuario, usuario_service,
                             livro_service=None, emprestimo_service=None):
    for w in root.winfo_children():
        w.destroy()

    root.configure(bg=COR_FUNDO_INTERNO)
    root.geometry("980x680")
    root.title("Biblioteca Central — Aluno")

    def sair():
        from apresentacao.login import mostrar_login
        mostrar_login(root, usuario_service)

    montar_header(root, usuario, sair)

    # --- Linha dourada fina abaixo do header ---------------------------------
    tk.Frame(root, height=2, bg=COR_DOURADO).pack(fill="x")

    # --- Área principal com padding ------------------------------------------
    corpo = tk.Frame(root, bg=COR_FUNDO_INTERNO)
    corpo.pack(fill="both", expand=True, padx=30, pady=20)

    # --- Cards de resumo -----------------------------------------------------
    frame_cards = tk.Frame(corpo, bg=COR_FUNDO_INTERNO)
    frame_cards.pack(fill="x", pady=(0, 20))

    def carregar_stats():
        ativos   = len(emprestimo_service.buscar_emprestimos_ativos_por_usuario(usuario.id)) if emprestimo_service else 0
        atrasados = len([e for e in emprestimo_service.listar_emprestimos_atrasados() if e["emprestimo"].id_usuario == usuario.id]) if emprestimo_service else 0
        reservas = 0  # simplificado; pode expandir futuramente
        return ativos, atrasados, reservas

    ativos, atrasados, reservas = carregar_stats()

    montar_card_stat(frame_cards, ativos,    "Empréstimos Ativos", COR_TEXTO_ESCURO)
    montar_card_stat(frame_cards, atrasados, "Em Atraso",          COR_VERMELHO)
    montar_card_stat(frame_cards, reservas,  "Reservas Ativas",    COR_AMARELO)

    # --- Conteúdo das abas ---------------------------------------------------
    area_conteudo = tk.Frame(corpo, bg=COR_FUNDO_INTERNO)
    area_conteudo.pack(fill="both", expand=True)

    def mostrar_catalogo():
        for w in area_conteudo.winfo_children():
            w.destroy()

        # Campo de busca
        frame_busca = tk.Frame(area_conteudo, bg=COR_FUNDO_INTERNO)
        frame_busca.pack(fill="x", pady=(12, 8))

        tk.Label(frame_busca, text="🔍", bg=COR_FUNDO_INTERNO,
                 font=("Arial", 11)).pack(side="left")
        e_busca = tk.Entry(frame_busca, font=FONTE_CAMPO, relief="flat",
                           bg="white", fg="#888888", bd=6)
        e_busca.insert(0, "Buscar por título ou autor... (Enter)")
        e_busca.pack(side="left", fill="x", expand=True, ipady=5)

        # Grid de livros
        frame_grid = tk.Frame(area_conteudo, bg=COR_FUNDO_INTERNO)
        frame_grid.pack(fill="both", expand=True)

        CORES_CARD = ["#7a6a3a", "#3a6a4a", "#2a3a4a", "#8a3a3a",
                      "#4a5a3a", "#6a3a5a", "#3a5a6a", "#5a4a2a"]

        def renderizar_livros(livros):
            for w in frame_grid.winfo_children():
                w.destroy()

            for i, livro in enumerate(livros):
                col = i % 4
                row = i // 4
                cor = CORES_CARD[i % len(CORES_CARD)]

                card = tk.Frame(frame_grid, bg="white",
                                highlightbackground="#e0d8cc", highlightthickness=1)
                card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
                frame_grid.columnconfigure(col, weight=1)

                capa = tk.Frame(card, bg=cor, height=90)
                capa.pack(fill="x")
                tk.Label(capa, text="📖", font=("Arial", 24),
                         bg=cor, fg="#ffffff88").pack(expand=True)

                info = tk.Frame(card, bg="white", padx=10, pady=8)
                info.pack(fill="x")

                tk.Label(info, text=livro.titulo, font=("Arial", 10, "bold"),
                         bg="white", fg=COR_TEXTO_ESCURO, anchor="w",
                         wraplength=160).pack(anchor="w")
                tk.Label(info, text=livro.autor, font=("Arial", 9),
                         bg="white", fg=COR_TEXTO_SECUNDARIO).pack(anchor="w")
                tk.Label(info, text=f"{livro.genero}",
                         font=("Arial", 8), bg="white",
                         fg=COR_TEXTO_SECUNDARIO).pack(anchor="w")

                if livro.disponivel:
                    tk.Label(info, text="disponível", font=("Arial", 8),
                             bg="#d4edda", fg="#2d6a2d",
                             padx=6, pady=2).pack(anchor="w", pady=(4, 0))
                    botao_principal(info, "Solicitar Empréstimo",
                        lambda l=livro: solicitar_emprestimo(l)
                    ).pack(fill="x", pady=(6, 0))
                else:
                    tk.Label(info, text="Indisponível", font=("Arial", 8),
                             bg="#fde8e8", fg=COR_VERMELHO,
                             padx=6, pady=2).pack(anchor="w", pady=(4, 0))
                    tk.Button(info, text="Reservar",
                              font=("Arial", 9), bg="#f0ece4",
                              fg=COR_DOURADO, relief="flat", cursor="hand2",
                              command=lambda l=livro: reservar(l)
                    ).pack(fill="x", pady=(6, 0))

        def buscar(ev=None):
            termo = e_busca.get().strip()
            if termo == "Buscar por título ou autor... (Enter)":
                termo = ""
            if not termo:
                livros = livro_service.listar_livros() if livro_service else []
            else:
                livros = livro_service.buscar_por_titulo_ou_autor(termo) if livro_service else []
                if not livros:
                    messagebox.showinfo("Busca", "Nenhum resultado encontrado.")
            renderizar_livros(livros)

        e_busca.bind("<Return>", buscar)
        e_busca.bind("<FocusIn>", lambda ev: (
            e_busca.delete(0, tk.END) or e_busca.configure(fg="#333333")
        ) if e_busca.get() == "Buscar por título ou autor... (Enter)" else None)

        livros_iniciais = livro_service.listar_livros() if livro_service else []
        renderizar_livros(livros_iniciais)

    def solicitar_emprestimo(livro):
        if not emprestimo_service:
            messagebox.showinfo("Aviso", "Serviço de empréstimo não configurado.")
            return
        try:
            emp = emprestimo_service.realizar_emprestimo(usuario.id, livro.id)
            messagebox.showinfo("Sucesso",
                f"Empréstimo realizado!\nDevolução prevista: {emp.data_devolucao}")
            mostrar_catalogo()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def reservar(livro):
        if not emprestimo_service:
            messagebox.showinfo("Aviso", "Serviço de empréstimo não configurado.")
            return
        try:
            resultado = emprestimo_service.reservar_livro(usuario.id, livro.id)
            messagebox.showinfo("Reserva Confirmada",
                f"Reserva realizada!\nPosição na fila: {resultado['posicao_fila']}")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def mostrar_meus_emprestimos():
        for w in area_conteudo.winfo_children():
            w.destroy()

        frame = tk.Frame(area_conteudo, bg=COR_FUNDO_INTERNO)
        frame.pack(fill="both", expand=True, pady=12)

        colunas = [
            ("titulo",    "Título",    260),
            ("data_emp",  "Emprestado em", 120),
            ("devolucao", "Devolver até",  120),
            ("renovado",  "Renovado",      80),
            ("status",    "Status",        90),
        ]

        tree = treeview_estilizado(frame, colunas, altura=14)

        emprestimos = emprestimo_service.historico_por_usuario(usuario.id) if emprestimo_service else []
        hoje = date.today()

        if not emprestimos:
            messagebox.showinfo("Histórico", "Nenhum empréstimo encontrado no histórico.")
            return

        for emp in emprestimos:
            livro = livro_service.buscar_por_id(emp.id_livro) if livro_service else None
            titulo = livro.titulo if livro else f"Livro #{emp.id_livro}"
            data_dev = date.fromisoformat(emp.data_devolucao)
            status = "Atrasado" if (not livro or not livro.disponivel) and hoje > data_dev else (
                     "Devolvido" if (livro and livro.disponivel) else "Ativo")
            tree.insert("", tk.END, values=(
                titulo,
                emp.data_emprestimo,
                emp.data_devolucao,
                "Sim" if emp.renovado else "Não",
                status,
            ))

    def mostrar_minhas_reservas():
        for w in area_conteudo.winfo_children():
            w.destroy()
        tk.Label(area_conteudo, text="Nenhum empréstimo encontrado no histórico.",
                 font=FONTE_TABELA, bg=COR_FUNDO_INTERNO,
                 fg=COR_TEXTO_SECUNDARIO).pack(pady=40)

    # --- Montagem das abas ---------------------------------------------------
    montar_abas(corpo, [
        ("Catálogo",          mostrar_catalogo),
        ("Meus Empréstimos",  mostrar_meus_emprestimos),
        ("Minhas Reservas",   mostrar_minhas_reservas),
    ], COR_FUNDO_INTERNO)

    separador(corpo)
    mostrar_catalogo()