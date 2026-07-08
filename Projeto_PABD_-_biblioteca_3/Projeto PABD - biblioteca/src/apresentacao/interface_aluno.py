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
        try:
            ativos = len(emprestimo_service.buscar_emprestimos_ativos_por_usuario(usuario.id)) if emprestimo_service else 0
            atrasados = len([e for e in emprestimo_service.listar_emprestimos_atrasados() if e["emprestimo"].id_usuario == usuario.id]) if emprestimo_service else 0
            reservas = len([r for r in emprestimo_service.listar_reservas_do_usuario(usuario.id) if r.ativa]) if emprestimo_service else 0
            return ativos, atrasados, reservas
        except Exception as e:
            messagebox.showerror("Erro ao carregar dados", f"Não foi possível carregar seus dados:\n{e}")
            return 0, 0, 0

    ativos, atrasados, reservas = carregar_stats()

    montar_card_stat(frame_cards, ativos,    "Empréstimos Ativos", COR_TEXTO_ESCURO)
    montar_card_stat(frame_cards, atrasados, "Em Atraso",          COR_VERMELHO)
    montar_card_stat(frame_cards, reservas,  "Reservas Ativas",    COR_AMARELO)

    # --- Conteúdo das abas ---------------------------------------------------
    area_conteudo = tk.Frame(corpo, bg=COR_FUNDO_INTERNO)
    # (empacotado só depois do menu de abas, ao final da função)

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

        # Verifica se o aluno já tem empréstimo ativo ou solicitação pendente
        # (nesse caso, não pode solicitar outro)
        try:
            ja_tem_ativo = bool(emprestimo_service.emprestimo_atual_do_usuario(usuario.id)) if emprestimo_service else False
            ja_tem_pendente = any(
                s.pendente for s in emprestimo_service.listar_solicitacoes_do_usuario(usuario.id)
            ) if emprestimo_service else False
        except Exception:
            ja_tem_ativo, ja_tem_pendente = False, False
        bloqueado = ja_tem_ativo or ja_tem_pendente

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
                         bg=cor, fg="white").pack(expand=True)

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
                    if bloqueado:
                        tk.Button(info, text="Você já tem um pedido em aberto",
                                  font=("Arial", 8), bg="#e8e0d4", fg=COR_TEXTO_SECUNDARIO,
                                  relief="flat", state="disabled"
                        ).pack(fill="x", pady=(6, 0))
                    else:
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
            try:
                if not termo:
                    livros = livro_service.listar_livros() if livro_service else []
                else:
                    livros = livro_service.buscar_por_titulo_ou_autor(termo) if livro_service else []
                    if not livros:
                        messagebox.showinfo("Busca", "Nenhum resultado encontrado.")
            except Exception as e:
                messagebox.showerror("Erro ao buscar", f"Não foi possível buscar os livros:\n{e}")
                return
            renderizar_livros(livros)

        e_busca.bind("<Return>", buscar)
        e_busca.bind("<FocusIn>", lambda ev: (
            e_busca.delete(0, tk.END) or e_busca.configure(fg="#333333")
        ) if e_busca.get() == "Buscar por título ou autor... (Enter)" else None)

        try:
            livros_iniciais = livro_service.listar_livros() if livro_service else []
        except Exception as e:
            tk.Label(area_conteudo, text=f"Não foi possível carregar o acervo.\n{e}",
                     font=FONTE_TABELA, bg=COR_FUNDO_INTERNO, fg=COR_VERMELHO,
                     justify="left").pack(pady=20)
            return
        renderizar_livros(livros_iniciais)

    def solicitar_emprestimo(livro):
        if not emprestimo_service:
            messagebox.showinfo("Aviso", "Serviço de empréstimo não configurado.")
            return
        try:
            emprestimo_service.solicitar_emprestimo(usuario.id, livro.id)
            messagebox.showinfo("Solicitação Enviada",
                "Sua solicitação de empréstimo foi enviada!\n"
                "Aguarde a aprovação do bolsista.")
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

        wrapper = tk.Frame(area_conteudo, bg=COR_FUNDO_INTERNO)
        wrapper.pack(fill="both", expand=True, pady=12)

        # --- Empréstimo atual (destaque) --------------------------------
        atual = emprestimo_service.emprestimo_atual_do_usuario(usuario.id) if emprestimo_service else None

        painel = tk.Frame(wrapper, bg="white", highlightbackground=COR_DOURADO, highlightthickness=1)
        painel.pack(fill="x", pady=(0, 16), ipady=10, ipadx=12)

        if atual:
            livro = livro_service.buscar_por_id(atual.id_livro) if livro_service else None
            titulo = livro.titulo if livro else f"Livro #{atual.id_livro}"
            hoje = date.today()
            prazo = date.fromisoformat(atual.data_devolucao)
            atrasado = hoje > prazo

            tk.Label(painel, text="📖 Empréstimo Atual", font=("Arial", 11, "bold"),
                     bg="white", fg=COR_TEXTO_ESCURO).pack(anchor="w", padx=6)
            tk.Label(painel, text=titulo, font=("Arial", 13, "bold"),
                     bg="white", fg=COR_TEXTO_ESCURO).pack(anchor="w", padx=6, pady=(4, 0))
            tk.Label(
                painel,
                text=f"Emprestado em {atual.data_emprestimo}   •   Devolver até {atual.data_devolucao}"
                     + ("   •   ATRASADO" if atrasado else ""),
                font=("Arial", 9), bg="white",
                fg=(COR_VERMELHO if atrasado else COR_TEXTO_SECUNDARIO),
            ).pack(anchor="w", padx=6, pady=(2, 0))
        else:
            tk.Label(painel, text="Você não tem nenhum empréstimo ativo no momento.",
                     font=("Arial", 10), bg="white",
                     fg=COR_TEXTO_SECUNDARIO).pack(anchor="w", padx=6)

        # --- Solicitações pendentes ---------------------------------------
        try:
            solicitacoes = emprestimo_service.listar_solicitacoes_do_usuario(usuario.id) if emprestimo_service else []
        except Exception:
            solicitacoes = []
        pendentes = [s for s in solicitacoes if s.pendente]

        if pendentes:
            painel_solic = tk.Frame(wrapper, bg="#fff9ec", highlightbackground=COR_AMARELO, highlightthickness=1)
            painel_solic.pack(fill="x", pady=(0, 16), ipady=8, ipadx=12)
            tk.Label(painel_solic, text="⏳ Solicitações Aguardando Aprovação", font=("Arial", 10, "bold"),
                     bg="#fff9ec", fg=COR_TEXTO_ESCURO).pack(anchor="w", padx=6)
            for s in pendentes:
                livro = livro_service.buscar_por_id(s.id_livro) if livro_service else None
                titulo = livro.titulo if livro else f"Livro #{s.id_livro}"
                tk.Label(painel_solic, text=f"{titulo}  —  solicitado em {s.data_solicitacao}",
                         font=("Arial", 9), bg="#fff9ec",
                         fg=COR_TEXTO_SECUNDARIO).pack(anchor="w", padx=6)

        # --- Histórico completo ------------------------------------------
        tk.Label(wrapper, text="Histórico Completo", font=("Arial", 11, "bold"),
                 bg=COR_FUNDO_INTERNO, fg=COR_TEXTO_ESCURO).pack(anchor="w", pady=(4, 6))

        colunas = [
            ("titulo",    "Título",    260),
            ("data_emp",  "Emprestado em", 120),
            ("devolucao", "Devolver até",  120),
            ("renovado",  "Renovado",      80),
            ("status",    "Status",        90),
        ]

        tree = treeview_estilizado(wrapper, colunas, altura=10)

        emprestimos = emprestimo_service.historico_por_usuario(usuario.id) if emprestimo_service else []
        hoje = date.today()

        if not emprestimos:
            tk.Label(wrapper, text="Nenhum empréstimo encontrado no histórico.",
                     font=FONTE_TABELA, bg=COR_FUNDO_INTERNO,
                     fg=COR_TEXTO_SECUNDARIO).pack(pady=20)
            return

        for emp in emprestimos:
            livro = livro_service.buscar_por_id(emp.id_livro) if livro_service else None
            titulo = livro.titulo if livro else f"Livro #{emp.id_livro}"
            data_prazo = date.fromisoformat(emp.data_devolucao)

            if not emp.ativo:
                status = "Devolvido"
            elif hoje > data_prazo:
                status = "Atrasado"
            else:
                status = "Ativo"

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

        wrapper = tk.Frame(area_conteudo, bg=COR_FUNDO_INTERNO)
        wrapper.pack(fill="both", expand=True, pady=12)

        try:
            reservas = emprestimo_service.listar_reservas_do_usuario(usuario.id) if emprestimo_service else []
        except Exception as e:
            tk.Label(wrapper, text=f"Não foi possível carregar suas reservas.\n{e}",
                     font=FONTE_TABELA, bg=COR_FUNDO_INTERNO, fg=COR_VERMELHO,
                     justify="left").pack(pady=20)
            return

        ativas = [r for r in reservas if r.ativa]

        if not ativas:
            tk.Label(wrapper, text="Você não tem nenhuma reserva ativa no momento.",
                     font=FONTE_TABELA, bg=COR_FUNDO_INTERNO,
                     fg=COR_TEXTO_SECUNDARIO).pack(pady=40)
            return

        for r in ativas:
            linha = tk.Frame(wrapper, bg="white", highlightbackground="#e0d8cc", highlightthickness=1)
            linha.pack(fill="x", pady=6, ipady=8, ipadx=10)

            livro = livro_service.buscar_por_id(r.id_livro) if livro_service else None
            titulo = livro.titulo if livro else f"Livro #{r.id_livro}"
            posicao = emprestimo_service.posicao_na_fila(r.id_livro, r.id) if emprestimo_service else "-"

            tk.Label(linha, text=titulo, font=("Arial", 11, "bold"),
                     bg="white", fg=COR_TEXTO_ESCURO).pack(anchor="w", padx=10)
            tk.Label(
                linha,
                text=f"Reservado em {r.data_reserva}   •   Posição na fila: {posicao}",
                font=("Arial", 9), bg="white", fg=COR_TEXTO_SECUNDARIO,
            ).pack(anchor="w", padx=10, pady=(0, 6))

    # --- Montagem das abas ---------------------------------------------------
    montar_abas(corpo, [
        ("Catálogo",          mostrar_catalogo),
        ("Meus Empréstimos",  mostrar_meus_emprestimos),
        ("Minhas Reservas",   mostrar_minhas_reservas),
    ], COR_FUNDO_INTERNO)

    separador(corpo)
    area_conteudo.pack(fill="both", expand=True)
    mostrar_catalogo()