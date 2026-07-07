"""
interface_bolsista.py — Dashboard do Bolsista (US06, US07, US08, US09)

Cards: Solicitações Pendentes | Empréstimos Ativos | Em Atraso | Indisponíveis | Reservas Ativas
Abas:  Solicitações Pendentes | Central de Empréstimos | Registrar Devolução |
       Livros Indisponíveis | Meus Registros
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
    # ABA: Central de Empréstimos
    # Busca qualquer aluno (nome ou ID), mostra o empréstimo em andamento
    # dele (com opção de renovar) ou permite criar um novo, e exibe o
    # histórico completo (empréstimos antigos + atual).
    # ------------------------------------------------------------------
    def aba_central_emprestimos():
        limpar()

        # --- Bloco de busca ---------------------------------------------
        frame_busca = tk.Frame(area, bg=COR_FUNDO_INTERNO)
        frame_busca.pack(fill="x", pady=(16, 8))

        tk.Label(frame_busca, text="BUSCAR ALUNO (nome ou ID)", font=FONTE_LABEL,
                 bg=COR_FUNDO_INTERNO, fg="#555555").pack(anchor="w")

        linha_busca = tk.Frame(frame_busca, bg=COR_FUNDO_INTERNO)
        linha_busca.pack(fill="x", pady=(4, 0))

        e_busca = tk.Entry(linha_busca, font=FONTE_CAMPO, relief="solid", bd=1, bg="white")
        e_busca.pack(side="left", fill="x", expand=True, ipady=7)

        frame_resultados = tk.Frame(area, bg=COR_FUNDO_INTERNO)
        frame_resultados.pack(fill="x", pady=(4, 12))

        frame_painel = tk.Frame(area, bg=COR_FUNDO_INTERNO)
        frame_painel.pack(fill="both", expand=True)

        def limpar_resultados():
            for w in frame_resultados.winfo_children():
                w.destroy()

        def limpar_painel():
            for w in frame_painel.winfo_children():
                w.destroy()

        def selecionar_aluno(aluno):
            limpar_resultados()
            montar_painel_aluno(aluno)

        def buscar(ev=None):
            termo = e_busca.get().strip()
            if not termo:
                messagebox.showinfo("Busca", "Digite um nome ou ID para buscar.")
                return

            limpar_resultados()
            limpar_painel()

            if termo.isdigit():
                aluno = usuario_service.buscar_por_id(int(termo))
                resultados = [aluno] if aluno else []
            else:
                resultados = usuario_service.buscar_por_nome(termo)

            # A central gerencia empréstimos de alunos
            resultados = [u for u in resultados if u and u.tipo == "aluno"]

            if not resultados:
                messagebox.showinfo("Busca", "Nenhum aluno encontrado.")
                return

            if len(resultados) == 1:
                selecionar_aluno(resultados[0])
                return

            # Múltiplos resultados: lista para o bolsista escolher
            tk.Label(frame_resultados, text="Selecione o aluno:", font=FONTE_LABEL,
                     bg=COR_FUNDO_INTERNO, fg="#555555").pack(anchor="w", pady=(4, 4))

            for aluno in resultados:
                linha = tk.Frame(frame_resultados, bg="white",
                                  highlightbackground="#e0d8cc", highlightthickness=1)
                linha.pack(fill="x", pady=2)
                tk.Label(linha, text=f"#{aluno.id}  {aluno.nome}  ({aluno.email})",
                         font=FONTE_TABELA, bg="white", fg=COR_TEXTO_ESCURO,
                         anchor="w", padx=10, pady=6).pack(side="left", fill="x", expand=True)
                botao_secundario(linha, "Selecionar",
                                  lambda a=aluno: selecionar_aluno(a)).pack(side="right", padx=8, pady=4)

        e_busca.bind("<Return>", buscar)
        botao_principal(linha_busca, "Buscar", buscar).pack(side="left", padx=(8, 0))

        def montar_painel_aluno(aluno):
            limpar_painel()

            tk.Label(frame_painel, text=f"{aluno.nome}  (ID #{aluno.id})",
                     font=("Arial", 13, "bold"), bg=COR_FUNDO_INTERNO,
                     fg=COR_TEXTO_ESCURO).pack(anchor="w", pady=(4, 12))

            # --- Bloco: Empréstimo Atual ----------------------------------
            emp_atual = emprestimo_service.emprestimo_atual_por_usuario(aluno.id)

            bloco_atual = tk.Frame(frame_painel, bg="white",
                                    highlightbackground="#e0d8cc", highlightthickness=1)
            bloco_atual.pack(fill="x", pady=(0, 16))

            conteudo = tk.Frame(bloco_atual, bg="white", padx=14, pady=12)
            conteudo.pack(fill="x")

            if emp_atual:
                livro = livro_service.buscar_por_id(emp_atual.id_livro)
                titulo_livro = livro.titulo if livro else f"Livro #{emp_atual.id_livro}"

                tk.Label(conteudo, text="EMPRÉSTIMO ATUAL", font=FONTE_LABEL,
                         bg="white", fg="#888888").pack(anchor="w")
                tk.Label(conteudo, text=titulo_livro, font=("Arial", 11, "bold"),
                         bg="white", fg=COR_TEXTO_ESCURO).pack(anchor="w", pady=(2, 0))
                tk.Label(conteudo,
                         text=f"Emprestado em {emp_atual.data_emprestimo}  •  "
                              f"Devolver até {emp_atual.data_devolucao}"
                              + ("  •  já renovado" if emp_atual.renovado else ""),
                         font=("Arial", 9), bg="white",
                         fg=COR_TEXTO_SECUNDARIO).pack(anchor="w", pady=(2, 8))

                def renovar():
                    try:
                        novo = emprestimo_service.renovar_emprestimo(emp_atual.id)
                        messagebox.showinfo("Sucesso",
                            f"Empréstimo renovado!\nNova data de devolução: {novo.data_devolucao}")
                        montar_painel_aluno(aluno)
                    except ValueError as e:
                        messagebox.showerror("Erro", str(e))

                botao_principal(conteudo, "Renovar Empréstimo", renovar).pack(anchor="w")
            else:
                tk.Label(conteudo, text="Nenhum empréstimo em andamento.",
                         font=("Arial", 10), bg="white",
                         fg=COR_TEXTO_SECUNDARIO).pack(anchor="w", pady=(0, 10))

                tk.Label(conteudo, text="ID DO LIVRO PARA NOVO EMPRÉSTIMO",
                         font=FONTE_LABEL, bg="white", fg="#555555").pack(anchor="w")

                linha_novo = tk.Frame(conteudo, bg="white")
                linha_novo.pack(fill="x", pady=(4, 0))

                e_livro = tk.Entry(linha_novo, font=FONTE_CAMPO, relief="solid",
                                    bd=1, bg="white", width=10)
                e_livro.pack(side="left", ipady=6)

                def novo_emprestimo():
                    try:
                        id_l = int(e_livro.get())
                        emp = emprestimo_service.realizar_emprestimo(aluno.id, id_l)
                        messagebox.showinfo("Sucesso",
                            f"Empréstimo registrado!\nDevolução prevista: {emp.data_devolucao}")
                        montar_painel_aluno(aluno)
                    except ValueError as e:
                        messagebox.showerror("Erro", str(e))

                botao_principal(linha_novo, "Registrar Empréstimo",
                                 novo_emprestimo).pack(side="left", padx=(8, 0))

            # --- Bloco: Histórico completo ---------------------------------
            tk.Label(frame_painel, text="HISTÓRICO COMPLETO", font=FONTE_LABEL,
                     bg=COR_FUNDO_INTERNO, fg="#555555").pack(anchor="w", pady=(4, 6))

            colunas = [
                ("livro",     "Título",        260),
                ("data_emp",  "Emprestado em", 110),
                ("devolucao", "Devolver até",  110),
                ("renovado",  "Renovado",       80),
                ("status",    "Status",         90),
            ]
            tree = treeview_estilizado(frame_painel, colunas, altura=8)

            historico = emprestimo_service.historico_por_usuario(aluno.id)
            if not historico:
                tk.Label(frame_painel, text="Nenhum empréstimo no histórico.",
                         font=("Arial", 9), bg=COR_FUNDO_INTERNO,
                         fg=COR_TEXTO_SECUNDARIO).pack(anchor="w", pady=8)
                return

            hoje = date.today()
            for emp in historico:
                livro = livro_service.buscar_por_id(emp.id_livro)
                titulo_livro = livro.titulo if livro else f"Livro #{emp.id_livro}"

                if emp_atual and emp.id == emp_atual.id:
                    status = "Atrasado" if hoje > date.fromisoformat(emp.data_devolucao) else "Atual"
                else:
                    status = "Devolvido"

                tree.insert("", tk.END, values=(
                    titulo_livro, emp.data_emprestimo, emp.data_devolucao,
                    "Sim" if emp.renovado else "Não", status,
                ))

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
        ("Central de Empréstimos", aba_central_emprestimos),
        ("Registrar Devolução",    aba_devolucao),
        ("Livros Indisponíveis",   aba_indisponiveis),
        ("Meus Registros",         aba_meus_registros),
    ], COR_FUNDO_INTERNO)

    separador(corpo)
    aba_solicitacoes()