"""
interface_bolsista.py — Dashboard do Bolsista (US06, US07, US08, US09, US11)

Abas: Central de Empréstimos | Histórico do Aluno | Registrar Devolução |
      Livros Indisponíveis | Todos os Empréstimos
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
    root.resizable(True, True)
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

    atrasados_lista = emprestimo_service.listar_emprestimos_atrasados() if emprestimo_service else []
    indisponiveis   = livro_service.listar_indisponiveis() if livro_service else []
    try:
        solicitacoes_pend = emprestimo_service.listar_solicitacoes_pendentes() if emprestimo_service else []
    except Exception:
        solicitacoes_pend = []

    montar_card_stat(frame_cards, len(solicitacoes_pend),   "Solicitações Pendentes", COR_DOURADO)
    montar_card_stat(frame_cards, len(indisponiveis),       "Empréstimos Ativos",     "#2a4a8a")
    montar_card_stat(frame_cards, len(atrasados_lista),     "Em Atraso",              COR_VERMELHO)
    montar_card_stat(frame_cards, len(indisponiveis),       "Livros Indisponíveis",   COR_AMARELO)

    # --- Área de conteúdo das abas -------------------------------------------
    area = tk.Frame(corpo, bg=COR_FUNDO_INTERNO)
    # (empacotado só depois do menu de abas, ao final da função —
    #  assim o menu nunca fica escondido atrás do conteúdo)

    def limpar():
        for w in area.winfo_children():
            w.destroy()

    def _linha_status_emprestimo(painel, emp):
        """Monta o bloco 'Empréstimo Atual' dentro de um painel, com botão de renovar."""
        livro = livro_service.buscar_por_id(emp.id_livro) if livro_service else None
        titulo = livro.titulo if livro else f"Livro #{emp.id_livro}"
        hoje = date.today()
        prazo = date.fromisoformat(emp.data_devolucao)
        atrasado = hoje > prazo

        tk.Label(painel, text="Empréstimo Atual", font=("Arial", 10, "bold"),
                 bg="white", fg=COR_TEXTO_ESCURO).pack(anchor="w", padx=14)
        tk.Label(painel, text=titulo, font=("Arial", 11), bg="white",
                 fg=COR_TEXTO_ESCURO).pack(anchor="w", padx=14)
        tk.Label(
            painel,
            text=f"Devolver até {emp.data_devolucao}" + ("   •   ATRASADO" if atrasado else ""),
            font=("Arial", 9), bg="white",
            fg=(COR_VERMELHO if atrasado else COR_TEXTO_SECUNDARIO),
        ).pack(anchor="w", padx=14, pady=(0, 8))

    # ------------------------------------------------------------------
    # ABA: Solicitações Pendentes (US05, US06)
    # ------------------------------------------------------------------
    def aba_solicitacoes():
        limpar()
        frame = tk.Frame(area, bg=COR_FUNDO_INTERNO)
        frame.pack(fill="both", expand=True, pady=12)

        try:
            solicitacoes = emprestimo_service.listar_solicitacoes_pendentes() if emprestimo_service else []
        except Exception as e:
            tk.Label(frame, text=f"Não foi possível carregar as solicitações.\n{e}",
                     font=FONTE_TABELA, bg=COR_FUNDO_INTERNO, fg=COR_VERMELHO,
                     justify="left").pack(pady=20)
            return

        if not solicitacoes:
            tk.Label(frame, text="Nenhuma solicitação pendente no momento.",
                     font=FONTE_TABELA, bg=COR_FUNDO_INTERNO,
                     fg=COR_TEXTO_SECUNDARIO).pack(pady=40)
            return

        def aprovar(id_solicitacao):
            try:
                emp = emprestimo_service.aprovar_solicitacao(id_solicitacao)
                messagebox.showinfo("Sucesso",
                    f"Solicitação aprovada! Empréstimo registrado.\nDevolução prevista: {emp.data_devolucao}")
                aba_solicitacoes()
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

        def rejeitar(id_solicitacao):
            if not messagebox.askyesno("Confirmar", "Rejeitar esta solicitação de empréstimo?"):
                return
            try:
                emprestimo_service.rejeitar_solicitacao(id_solicitacao)
                messagebox.showinfo("Solicitação Rejeitada", "A solicitação foi rejeitada.")
                aba_solicitacoes()
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

        for s in solicitacoes:
            linha = tk.Frame(frame, bg="white", highlightbackground="#e0d8cc", highlightthickness=1)
            linha.pack(fill="x", pady=6, ipady=8, ipadx=10)

            aluno = usuario_service.buscar_por_id(s.id_usuario) if usuario_service else None
            livro = livro_service.buscar_por_id(s.id_livro) if livro_service else None

            info = tk.Frame(linha, bg="white")
            info.pack(side="left", fill="x", expand=True, padx=10)
            tk.Label(info, text=(livro.titulo if livro else f"Livro #{s.id_livro}"),
                     font=("Arial", 11, "bold"), bg="white", fg=COR_TEXTO_ESCURO).pack(anchor="w")
            tk.Label(
                info,
                text=(f"Solicitado por {aluno.nome if aluno else f'#{s.id_usuario}'}   •   "
                      f"em {s.data_solicitacao}"),
                font=("Arial", 9), bg="white", fg=COR_TEXTO_SECUNDARIO,
            ).pack(anchor="w")

            botoes = tk.Frame(linha, bg="white")
            botoes.pack(side="right", padx=10)
            botao_secundario(botoes, "Rejeitar",
                              lambda sid=s.id: rejeitar(sid)).pack(side="left", padx=(0, 8), ipady=2)
            botao_principal(botoes, "Aprovar",
                             lambda sid=s.id: aprovar(sid)).pack(side="left", ipady=2)

    # ------------------------------------------------------------------
    # ABA: Central de Empréstimos (US06, US07)
    # ------------------------------------------------------------------
    def aba_central_emprestimos():
        limpar()
        frame = tk.Frame(area, bg=COR_FUNDO_INTERNO)
        frame.pack(fill="both", expand=True, pady=12)

        tk.Label(frame, text="BUSCAR ALUNO POR NOME", font=FONTE_LABEL,
                 bg=COR_FUNDO_INTERNO, fg="#555555").pack(anchor="w")
        linha_busca = tk.Frame(frame, bg=COR_FUNDO_INTERNO)
        linha_busca.pack(fill="x", pady=(4, 10))
        e_busca_aluno = tk.Entry(linha_busca, font=FONTE_CAMPO, relief="solid", bd=1, bg="white")
        e_busca_aluno.pack(side="left", fill="x", expand=True, ipady=6)
        e_busca_aluno.bind("<Return>", lambda ev: buscar_aluno())
        botao_secundario(linha_busca, "Buscar", lambda: buscar_aluno()).pack(side="left", padx=(8, 0))

        lista_resultados = tk.Listbox(frame, height=4, font=FONTE_CAMPO)
        lista_resultados.pack(fill="x", pady=(0, 10))
        resultados_cache = []

        painel_aluno = tk.Frame(frame, bg="white", highlightbackground=COR_DOURADO, highlightthickness=1)
        painel_aluno.pack(fill="both", expand=True, pady=(0, 10))

        aluno_selecionado = {"usuario": None}

        def buscar_aluno():
            termo = e_busca_aluno.get().strip()
            lista_resultados.delete(0, tk.END)
            resultados_cache.clear()
            if not termo:
                return
            try:
                resultados = [u for u in usuario_service.buscar_por_nome(termo) if u.tipo == "aluno"]
            except ValueError as e:
                messagebox.showerror("Erro", str(e))
                return
            if not resultados:
                lista_resultados.insert(tk.END, "Nenhum aluno encontrado.")
                return
            for u in resultados:
                resultados_cache.append(u)
                lista_resultados.insert(tk.END, f"{u.nome}   ({u.email})   — ID {u.id}")

        def selecionar_aluno(ev=None):
            sel = lista_resultados.curselection()
            if not sel or not resultados_cache or sel[0] >= len(resultados_cache):
                return
            aluno_selecionado["usuario"] = resultados_cache[sel[0]]
            renderizar_painel_aluno()

        lista_resultados.bind("<<ListboxSelect>>", selecionar_aluno)

        def renovar(id_emprestimo):
            try:
                emp = emprestimo_service.renovar_emprestimo(id_emprestimo)
                messagebox.showinfo("Sucesso", f"Empréstimo renovado!\nNova data de devolução: {emp.data_devolucao}")
                renderizar_painel_aluno()
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

        def renderizar_painel_aluno():
            for w in painel_aluno.winfo_children():
                w.destroy()

            aluno = aluno_selecionado["usuario"]
            if not aluno:
                tk.Label(painel_aluno, text="Busque e selecione um aluno acima.",
                         bg="white", fg=COR_TEXTO_SECUNDARIO).pack(pady=30)
                return

            tk.Label(painel_aluno, text=aluno.nome, font=("Arial", 13, "bold"),
                     bg="white", fg=COR_TEXTO_ESCURO).pack(anchor="w", padx=14, pady=(12, 0))
            tk.Label(painel_aluno, text=aluno.email, font=("Arial", 9),
                     bg="white", fg=COR_TEXTO_SECUNDARIO).pack(anchor="w", padx=14)

            tk.Frame(painel_aluno, height=1, bg="#e0d8cc").pack(fill="x", padx=14, pady=10)

            atual = emprestimo_service.emprestimo_atual_do_usuario(aluno.id) if emprestimo_service else None
            if atual:
                _linha_status_emprestimo(painel_aluno, atual)
                botao_secundario(painel_aluno, "🔄  Renovar Empréstimo",
                                  lambda: renovar(atual.id)).pack(anchor="w", padx=14, pady=(0, 14))
            else:
                tk.Label(painel_aluno, text="Nenhum empréstimo ativo no momento.",
                         bg="white", fg=COR_TEXTO_SECUNDARIO).pack(anchor="w", padx=14, pady=(0, 14))

            tk.Frame(painel_aluno, height=1, bg="#e0d8cc").pack(fill="x", padx=14, pady=(0, 10))

            tk.Label(painel_aluno, text="Novo Empréstimo — buscar livro (título ou autor)",
                     font=("Arial", 10, "bold"), bg="white", fg=COR_TEXTO_ESCURO).pack(anchor="w", padx=14)

            linha_busca_livro = tk.Frame(painel_aluno, bg="white")
            linha_busca_livro.pack(fill="x", padx=14, pady=(4, 4))
            e_busca_livro = tk.Entry(linha_busca_livro, font=FONTE_CAMPO, relief="solid", bd=1)
            e_busca_livro.pack(side="left", fill="x", expand=True, ipady=6)
            botao_secundario(linha_busca_livro, "Buscar",
                              lambda: buscar_livro()).pack(side="left", padx=(8, 0))

            lista_livros = tk.Listbox(painel_aluno, height=4, font=FONTE_CAMPO)
            lista_livros.pack(fill="x", padx=14, pady=(4, 6))
            livros_cache = []

            def buscar_livro():
                termo = e_busca_livro.get().strip()
                lista_livros.delete(0, tk.END)
                livros_cache.clear()
                if not termo or not livro_service:
                    return
                try:
                    resultados = [l for l in livro_service.buscar_por_titulo_ou_autor(termo) if l.disponivel]
                except ValueError as e:
                    messagebox.showerror("Erro", str(e))
                    return
                if not resultados:
                    lista_livros.insert(tk.END, "Nenhum exemplar disponível encontrado.")
                    return
                for l in resultados:
                    livros_cache.append(l)
                    lista_livros.insert(tk.END, f"{l.titulo} — {l.autor}   (exemplar #{l.id})")

            e_busca_livro.bind("<Return>", lambda ev: buscar_livro())

            def registrar_selecionado():
                sel = lista_livros.curselection()
                if not sel or not livros_cache or sel[0] >= len(livros_cache):
                    messagebox.showwarning("Aviso", "Busque e selecione um livro disponível na lista.")
                    return
                livro = livros_cache[sel[0]]
                try:
                    emp = emprestimo_service.realizar_emprestimo(aluno.id, livro.id)
                    messagebox.showinfo("Sucesso",
                        f"Empréstimo registrado!\nDevolução prevista: {emp.data_devolucao}")
                    renderizar_painel_aluno()
                except ValueError as e:
                    messagebox.showerror("Erro", str(e))

            botao_principal(painel_aluno, "Registrar Empréstimo do Livro Selecionado",
                             registrar_selecionado).pack(fill="x", padx=14, pady=(0, 14), ipady=4)

        renderizar_painel_aluno()

    # ------------------------------------------------------------------
    # ABA: Histórico do Aluno (US11)
    # ------------------------------------------------------------------
    def aba_historico_aluno():
        limpar()
        frame = tk.Frame(area, bg=COR_FUNDO_INTERNO)
        frame.pack(fill="both", expand=True, pady=12)

        tk.Label(frame, text="BUSCAR ALUNO POR NOME", font=FONTE_LABEL,
                 bg=COR_FUNDO_INTERNO, fg="#555555").pack(anchor="w")
        linha_busca = tk.Frame(frame, bg=COR_FUNDO_INTERNO)
        linha_busca.pack(fill="x", pady=(4, 10))
        e_busca = tk.Entry(linha_busca, font=FONTE_CAMPO, relief="solid", bd=1, bg="white")
        e_busca.pack(side="left", fill="x", expand=True, ipady=6)
        e_busca.bind("<Return>", lambda ev: buscar())
        botao_secundario(linha_busca, "Buscar", lambda: buscar()).pack(side="left", padx=(8, 0))

        lista_resultados = tk.Listbox(frame, height=4, font=FONTE_CAMPO)
        lista_resultados.pack(fill="x", pady=(0, 10))
        resultados_cache = []

        painel_resultado = tk.Frame(frame, bg=COR_FUNDO_INTERNO)
        painel_resultado.pack(fill="both", expand=True)

        def buscar():
            termo = e_busca.get().strip()
            lista_resultados.delete(0, tk.END)
            resultados_cache.clear()
            if not termo:
                return
            try:
                resultados = [u for u in usuario_service.buscar_por_nome(termo) if u.tipo == "aluno"]
            except ValueError as e:
                messagebox.showerror("Erro", str(e))
                return
            if not resultados:
                lista_resultados.insert(tk.END, "Nenhum aluno encontrado.")
                return
            for u in resultados:
                resultados_cache.append(u)
                lista_resultados.insert(tk.END, f"{u.nome}   ({u.email})   — ID {u.id}")

        def selecionar(ev=None):
            sel = lista_resultados.curselection()
            if not sel or not resultados_cache or sel[0] >= len(resultados_cache):
                return
            mostrar_historico(resultados_cache[sel[0]])

        lista_resultados.bind("<<ListboxSelect>>", selecionar)

        def mostrar_historico(aluno):
            for w in painel_resultado.winfo_children():
                w.destroy()

            tk.Label(painel_resultado, text=f"Histórico de {aluno.nome}", font=("Arial", 12, "bold"),
                     bg=COR_FUNDO_INTERNO, fg=COR_TEXTO_ESCURO).pack(anchor="w", pady=(4, 8))

            colunas = [
                ("titulo",    "Título",        260),
                ("data_emp",  "Emprestado em", 120),
                ("devolucao", "Devolver até",  120),
                ("renovado",  "Renovado",      80),
                ("status",    "Status",        90),
            ]
            tree = treeview_estilizado(painel_resultado, colunas, altura=10)

            emprestimos = emprestimo_service.historico_por_usuario(aluno.id) if emprestimo_service else []
            hoje = date.today()

            if not emprestimos:
                tk.Label(painel_resultado, text="Nenhum empréstimo encontrado no histórico.",
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
                    titulo, emp.data_emprestimo, emp.data_devolucao,
                    "Sim" if emp.renovado else "Não", status,
                ))

        tk.Label(painel_resultado, text="Busque e selecione um aluno acima para ver o histórico.",
                 bg=COR_FUNDO_INTERNO, fg=COR_TEXTO_SECUNDARIO).pack(pady=30)

    # ------------------------------------------------------------------
    # ABA: Reservas Pendentes (US10)
    # ------------------------------------------------------------------
    def aba_reservas():
        limpar()
        frame = tk.Frame(area, bg=COR_FUNDO_INTERNO)
        frame.pack(fill="both", expand=True, pady=12)

        try:
            reservas = emprestimo_service.listar_reservas_ativas() if emprestimo_service else []
        except Exception as e:
            tk.Label(frame, text=f"Não foi possível carregar as reservas.\n{e}",
                     font=FONTE_TABELA, bg=COR_FUNDO_INTERNO, fg=COR_VERMELHO,
                     justify="left").pack(pady=20)
            return

        if not reservas:
            tk.Label(frame, text="Nenhuma reserva pendente no momento.",
                     font=FONTE_TABELA, bg=COR_FUNDO_INTERNO,
                     fg=COR_TEXTO_SECUNDARIO).pack(pady=40)
            return

        def criar_emprestimo(id_reserva):
            try:
                emp = emprestimo_service.criar_emprestimo_a_partir_da_reserva(id_reserva)
                messagebox.showinfo("Sucesso",
                    f"Empréstimo criado a partir da reserva!\nDevolução prevista: {emp.data_devolucao}")
                aba_reservas()
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

        for r in reservas:
            linha = tk.Frame(frame, bg="white", highlightbackground="#e0d8cc", highlightthickness=1)
            linha.pack(fill="x", pady=6, ipady=8, ipadx=10)

            aluno = usuario_service.buscar_por_id(r.id_usuario) if usuario_service else None
            livro = livro_service.buscar_por_id(r.id_livro) if livro_service else None
            posicao = emprestimo_service.posicao_na_fila(r.id_livro, r.id) if emprestimo_service else "-"

            info = tk.Frame(linha, bg="white")
            info.pack(side="left", fill="x", expand=True, padx=10)
            tk.Label(info, text=(livro.titulo if livro else f"Livro #{r.id_livro}"),
                     font=("Arial", 11, "bold"), bg="white", fg=COR_TEXTO_ESCURO).pack(anchor="w")
            tk.Label(
                info,
                text=(f"Reservado por {aluno.nome if aluno else f'#{r.id_usuario}'}   •   "
                      f"em {r.data_reserva}   •   Posição na fila: {posicao}"),
                font=("Arial", 9), bg="white", fg=COR_TEXTO_SECUNDARIO,
            ).pack(anchor="w")

            disponivel = livro.disponivel if livro else False
            if disponivel:
                botao_principal(linha, "Criar Empréstimo",
                                 lambda rid=r.id: criar_emprestimo(rid)
                ).pack(side="right", padx=10, ipady=2)
            else:
                tk.Label(linha, text="Aguardando devolução", font=("Arial", 9, "bold"),
                         bg="white", fg=COR_AMARELO).pack(side="right", padx=10)

    # ------------------------------------------------------------------
    # ABA: Registrar Devolução (US08)
    # ------------------------------------------------------------------
    def aba_devolucao():
        limpar()
        frame = tk.Frame(area, bg=COR_FUNDO_INTERNO)
        frame.pack(fill="both", expand=True, pady=12)

        tk.Label(frame, text="BUSCAR ALUNO POR NOME", font=FONTE_LABEL,
                 bg=COR_FUNDO_INTERNO, fg="#555555").pack(anchor="w")
        linha_busca = tk.Frame(frame, bg=COR_FUNDO_INTERNO)
        linha_busca.pack(fill="x", pady=(4, 10))
        e_busca = tk.Entry(linha_busca, font=FONTE_CAMPO, relief="solid", bd=1, bg="white")
        e_busca.pack(side="left", fill="x", expand=True, ipady=6)
        e_busca.bind("<Return>", lambda ev: buscar())
        botao_secundario(linha_busca, "Buscar", lambda: buscar()).pack(side="left", padx=(8, 0))

        lista_resultados = tk.Listbox(frame, height=4, font=FONTE_CAMPO)
        lista_resultados.pack(fill="x", pady=(0, 10))
        resultados_cache = []

        painel = tk.Frame(frame, bg="white", highlightbackground=COR_DOURADO, highlightthickness=1)
        painel.pack(fill="both", expand=True, pady=(0, 10))

        def buscar():
            termo = e_busca.get().strip()
            lista_resultados.delete(0, tk.END)
            resultados_cache.clear()
            if not termo:
                return
            try:
                resultados = [u for u in usuario_service.buscar_por_nome(termo) if u.tipo == "aluno"]
            except ValueError as e:
                messagebox.showerror("Erro", str(e))
                return
            if not resultados:
                lista_resultados.insert(tk.END, "Nenhum aluno encontrado.")
                return
            for u in resultados:
                resultados_cache.append(u)
                lista_resultados.insert(tk.END, f"{u.nome}   ({u.email})   — ID {u.id}")

        def selecionar(ev=None):
            sel = lista_resultados.curselection()
            if not sel or not resultados_cache or sel[0] >= len(resultados_cache):
                return
            mostrar_emprestimos_ativos(resultados_cache[sel[0]])

        lista_resultados.bind("<<ListboxSelect>>", selecionar)

        def devolver(id_emprestimo, aluno):
            try:
                resultado = emprestimo_service.registrar_devolucao(id_emprestimo)
                if resultado["atrasado"]:
                    messagebox.showwarning("Devolução com Atraso",
                        f"Devolução realizada com atraso de {resultado['dias_atraso']} dia(s).")
                else:
                    messagebox.showinfo("Sucesso", "Devolução registrada com sucesso!")
                mostrar_emprestimos_ativos(aluno)
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

        def mostrar_emprestimos_ativos(aluno):
            for w in painel.winfo_children():
                w.destroy()

            tk.Label(painel, text=aluno.nome, font=("Arial", 13, "bold"),
                     bg="white", fg=COR_TEXTO_ESCURO).pack(anchor="w", padx=14, pady=(12, 0))
            tk.Label(painel, text=aluno.email, font=("Arial", 9),
                     bg="white", fg=COR_TEXTO_SECUNDARIO).pack(anchor="w", padx=14)
            tk.Frame(painel, height=1, bg="#e0d8cc").pack(fill="x", padx=14, pady=10)

            ativos = emprestimo_service.buscar_emprestimos_ativos_por_usuario(aluno.id) if emprestimo_service else []
            if not ativos:
                tk.Label(painel, text="Nenhum empréstimo ativo no momento.",
                         bg="white", fg=COR_TEXTO_SECUNDARIO).pack(anchor="w", padx=14, pady=(0, 14))
                return

            for emp in ativos:
                linha = tk.Frame(painel, bg="white")
                linha.pack(fill="x", padx=14, pady=(0, 10))

                livro = livro_service.buscar_por_id(emp.id_livro) if livro_service else None
                titulo = livro.titulo if livro else f"Livro #{emp.id_livro}"
                hoje = date.today()
                prazo = date.fromisoformat(emp.data_devolucao)
                atrasado = hoje > prazo

                info = tk.Frame(linha, bg="white")
                info.pack(side="left", fill="x", expand=True)
                tk.Label(info, text=titulo, font=("Arial", 11, "bold"),
                         bg="white", fg=COR_TEXTO_ESCURO).pack(anchor="w")
                tk.Label(
                    info,
                    text=f"Devolver até {emp.data_devolucao}" + ("   •   ATRASADO" if atrasado else ""),
                    font=("Arial", 9), bg="white",
                    fg=(COR_VERMELHO if atrasado else COR_TEXTO_SECUNDARIO),
                ).pack(anchor="w")

                botao_principal(linha, "Registrar Devolução",
                                 lambda eid=emp.id, al=aluno: devolver(eid, al)
                ).pack(side="right", ipady=2)

        tk.Label(painel, text="Busque e selecione um aluno acima para ver os empréstimos ativos.",
                 bg="white", fg=COR_TEXTO_SECUNDARIO).pack(pady=30)

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
            tk.Label(frame, text="Todos os livros estão disponíveis no momento.",
                     font=FONTE_TABELA, bg=COR_FUNDO_INTERNO,
                     fg=COR_TEXTO_SECUNDARIO).pack(pady=40)
            return

        for l in livros:
            tree.insert("", tk.END, values=(l.id, l.titulo, l.autor, l.genero))

    # ------------------------------------------------------------------
    # ABA: Todos os Empréstimos (ativo / atrasado / devolvido)
    # ------------------------------------------------------------------
    def aba_meus_registros():
        limpar()
        frame = tk.Frame(area, bg=COR_FUNDO_INTERNO)
        frame.pack(fill="both", expand=True, pady=12)

        colunas = [
            ("id",        "ID Emp.", 55),
            ("aluno",     "Aluno",   170),
            ("livro",     "Livro",   210),
            ("emprestado","Emprestado em", 100),
            ("devolucao", "Devolver até",  100),
            ("status",    "Status",   90),
        ]
        tree = treeview_estilizado(frame, colunas, altura=14)

        todos = emprestimo_service.listar_todos() if emprestimo_service else []
        if not todos:
            tk.Label(frame, text="Nenhum empréstimo registrado no sistema.",
                     font=FONTE_TABELA, bg=COR_FUNDO_INTERNO,
                     fg=COR_TEXTO_SECUNDARIO).pack(pady=40)
            return

        hoje = date.today()
        # Mais recentes primeiro
        for emp in sorted(todos, key=lambda e: e.data_emprestimo, reverse=True):
            usuario_emp = usuario_service.buscar_por_id(emp.id_usuario) if usuario_service else None
            livro = livro_service.buscar_por_id(emp.id_livro) if livro_service else None
            data_prazo = date.fromisoformat(emp.data_devolucao)

            if not emp.ativo:
                status = "Devolvido"
            elif hoje > data_prazo:
                status = "Atrasado"
            else:
                status = "Ativo"

            tree.insert("", tk.END, values=(
                emp.id,
                usuario_emp.nome if usuario_emp else f"#{emp.id_usuario}",
                livro.titulo if livro else f"#{emp.id_livro}",
                emp.data_emprestimo,
                emp.data_devolucao,
                status,
            ))

    # --- Montar abas ---------------------------------------------------------
    montar_abas(corpo, [
        ("Solicitações Pendentes", aba_solicitacoes),
        ("Central de Empréstimos", aba_central_emprestimos),
        ("Histórico do Aluno",     aba_historico_aluno),
        ("Reservas Pendentes",     aba_reservas),
        ("Registrar Devolução",    aba_devolucao),
        ("Livros Indisponíveis",   aba_indisponiveis),
        ("Todos os Empréstimos",   aba_meus_registros),
    ], COR_FUNDO_INTERNO)

    separador(corpo)
    area.pack(fill="both", expand=True)
    aba_solicitacoes()
