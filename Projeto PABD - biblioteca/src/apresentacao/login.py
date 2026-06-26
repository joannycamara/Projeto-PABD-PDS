"""
login.py — Tela de Login e Cadastro (US01, US02)

Tela única com duas abas: ENTRAR e CADASTRAR-SE.
Fundo azul-marinho escuro, card central, botão dourado.
"""

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from apresentacao.estilos import (
    COR_FUNDO_ESCURO, COR_FUNDO_CARD_LOGIN, COR_DOURADO, COR_DOURADO_HOVER,
    COR_TEXTO_CLARO, COR_CAMPO_FUNDO, COR_CAMPO_TEXTO, COR_BORDA_CAMPO,
    COR_TEXTO_SECUNDARIO, COR_LINHA_ABA,
    FONTE_TITULO_GRANDE, FONTE_SUBTITULO, FONTE_LABEL, FONTE_CAMPO,
    FONTE_BOTAO, FONTE_ABA,
)


def mostrar_login(root, usuario_service):
    """Renderiza a tela de login/cadastro na janela root."""
    for w in root.winfo_children():
        w.destroy()

    root.configure(bg=COR_FUNDO_ESCURO)
    root.geometry("700x580")
    root.title("Biblioteca Central")

    # --- Logo e título -------------------------------------------------------
    topo = tk.Frame(root, bg=COR_FUNDO_ESCURO)
    topo.pack(pady=(40, 10))

    tk.Label(
        topo, text="📖", font=("Arial", 28), bg=COR_FUNDO_ESCURO,
        fg=COR_DOURADO
    ).pack()

    tk.Label(
        topo, text="Biblioteca Central", font=FONTE_TITULO_GRANDE,
        bg=COR_FUNDO_ESCURO, fg=COR_TEXTO_CLARO
    ).pack()

    tk.Label(
        topo, text="SISTEMA DE GESTÃO ACADÊMICA", font=FONTE_SUBTITULO,
        bg=COR_FUNDO_ESCURO, fg=COR_TEXTO_SECUNDARIO
    ).pack(pady=(2, 0))

    # --- Abas ----------------------------------------------------------------
    frame_abas = tk.Frame(root, bg=COR_FUNDO_ESCURO)
    frame_abas.pack(pady=(20, 0))

    aba_var = tk.StringVar(value="entrar")

    lbl_entrar  = tk.Label(frame_abas, text="ENTRAR",       font=FONTE_ABA, bg=COR_FUNDO_ESCURO, cursor="hand2", padx=20)
    lbl_cadastro = tk.Label(frame_abas, text="CADASTRAR-SE", font=FONTE_ABA, bg=COR_FUNDO_ESCURO, cursor="hand2", padx=20)
    lbl_entrar.grid(row=0, column=0)
    lbl_cadastro.grid(row=0, column=1)

    linha_entrar   = tk.Frame(frame_abas, height=2, width=120, bg=COR_LINHA_ABA)
    linha_cadastro = tk.Frame(frame_abas, height=2, width=120, bg=COR_FUNDO_ESCURO)
    linha_entrar.grid(row=1, column=0, sticky="ew")
    linha_cadastro.grid(row=1, column=1, sticky="ew")

    # --- Card central --------------------------------------------------------
    card = tk.Frame(root, bg=COR_FUNDO_CARD_LOGIN, padx=30, pady=24)
    card.pack(padx=60, pady=10, fill="x")

    conteudo = tk.Frame(card, bg=COR_FUNDO_CARD_LOGIN)
    conteudo.pack(fill="x")

    # =========================================================================
    # ABA: ENTRAR
    # =========================================================================
    def montar_entrar():
        for w in conteudo.winfo_children():
            w.destroy()

        lbl_entrar.configure(fg=COR_DOURADO)
        lbl_cadastro.configure(fg=COR_TEXTO_SECUNDARIO)
        linha_entrar.configure(bg=COR_LINHA_ABA)
        linha_cadastro.configure(bg=COR_FUNDO_ESCURO)

        def campo(rotulo, placeholder, oculto=False):
            tk.Label(conteudo, text=rotulo, font=FONTE_LABEL,
                     bg=COR_FUNDO_CARD_LOGIN, fg=COR_DOURADO).pack(anchor="w", pady=(14, 3))
            e = tk.Entry(conteudo, font=FONTE_CAMPO, bg=COR_CAMPO_FUNDO,
                         fg=COR_CAMPO_TEXTO, insertbackground=COR_TEXTO_CLARO,
                         relief="flat", bd=4, show="•" if oculto else "")
            e.insert(0, placeholder)
            e.configure(fg="#888888")

            def on_focus_in(ev, en=e, ph=placeholder):
                if en.get() == ph:
                    en.delete(0, tk.END)
                    en.configure(fg=COR_CAMPO_TEXTO)

            def on_focus_out(ev, en=e, ph=placeholder):
                if not en.get():
                    en.insert(0, ph)
                    en.configure(fg="#888888")

            e.bind("<FocusIn>",  on_focus_in)
            e.bind("<FocusOut>", on_focus_out)
            e.pack(fill="x", ipady=8)
            return e

        e_email = campo("E-MAIL", "seu.email@gmail.com")
        e_senha = campo("SENHA",  "••••••••", oculto=True)

        def fazer_login():
            email = e_email.get().strip()
            senha = e_senha.get().strip()
            if email == "seu.email@":
                email = ""
            if senha == "••••••••":
                senha = ""
            try:
                usuario = usuario_service.login(email, senha)
                _redirecionar(root, usuario, usuario_service)
            except ValueError as erro:
                messagebox.showerror("Erro de Login", str(erro))

        tk.Button(
            conteudo, text="ENTRAR", command=fazer_login,
            bg=COR_DOURADO, fg=COR_TEXTO_CLARO, font=FONTE_BOTAO,
            relief="flat", cursor="hand2", pady=10
        ).pack(fill="x", pady=(20, 0))

    # =========================================================================
    # ABA: CADASTRAR-SE
    # =========================================================================
    def montar_cadastro():
        for w in conteudo.winfo_children():
            w.destroy()

        lbl_entrar.configure(fg=COR_TEXTO_SECUNDARIO)
        lbl_cadastro.configure(fg=COR_DOURADO)
        linha_entrar.configure(bg=COR_FUNDO_ESCURO)
        linha_cadastro.configure(bg=COR_LINHA_ABA)

        def campo(rotulo, placeholder, oculto=False):
            tk.Label(conteudo, text=rotulo, font=FONTE_LABEL,
                     bg=COR_FUNDO_CARD_LOGIN, fg=COR_DOURADO).pack(anchor="w", pady=(12, 3))
            e = tk.Entry(conteudo, font=FONTE_CAMPO, bg=COR_CAMPO_FUNDO,
                         fg=COR_CAMPO_TEXTO, insertbackground=COR_TEXTO_CLARO,
                         relief="flat", bd=4, show="•" if oculto else "")
            e.insert(0, placeholder)
            e.configure(fg="#888888")

            def on_in(ev, en=e, ph=placeholder):
                if en.get() == ph:
                    en.delete(0, tk.END)
                    en.configure(fg=COR_CAMPO_TEXTO)

            def on_out(ev, en=e, ph=placeholder):
                if not en.get():
                    en.insert(0, ph)
                    en.configure(fg="#888888")

            e.bind("<FocusIn>",  on_in)
            e.bind("<FocusOut>", on_out)
            e.pack(fill="x", ipady=8)
            return e

        e_nome  = campo("NOME COMPLETO *", "Seu nome completo")
        e_email = campo("E-MAIL *",        "seu.email@gmail.com")
        e_senha = campo("SENHA * (mín. 5 caracteres)", "••••••••", oculto=True)
        # ---------------- Tipo de usuário ---------------- #

        tk.Label(
            conteudo,
            text="TIPO DE USUÁRIO *",
            font=FONTE_LABEL,
            bg=COR_FUNDO_CARD_LOGIN,
            fg=COR_DOURADO
        ).pack(anchor="w", pady=(12, 3))

        tipo_var = tk.StringVar()

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Cadastro.TCombobox",
            font=FONTE_CAMPO,
            foreground=COR_CAMPO_TEXTO,
            fieldbackground=COR_CAMPO_FUNDO,
            background=COR_CAMPO_FUNDO,
            bordercolor=COR_BORDA_CAMPO,
            lightcolor=COR_BORDA_CAMPO,
            darkcolor=COR_BORDA_CAMPO,
            arrowcolor=COR_DOURADO,
            relief="flat",
            padding=8
        )

        style.map(
            "Cadastro.TCombobox",
            fieldbackground=[("readonly", COR_CAMPO_FUNDO)],
            foreground=[("readonly", COR_CAMPO_TEXTO)],
            selectbackground=[("readonly", COR_CAMPO_FUNDO)],
            selectforeground=[("readonly", COR_CAMPO_TEXTO)]
        )

        combo_tipo = ttk.Combobox(
            conteudo,
            textvariable=tipo_var,
            values=[
                "aluno",
                "bolsista",
                "bibliotecario"
            ],
            state="readonly",
            style="Cadastro.TCombobox",
            font=FONTE_CAMPO
        )

        combo_tipo.current(0)
        combo_tipo.pack(fill="x", ipady=7)

        def criar_conta():
            nome  = e_nome.get().strip()
            email = e_email.get().strip()
            senha = e_senha.get().strip()
            for ph in ("Seu nome completo", "seu.email@gmail.com", "••••••••"):
                if nome == ph:  nome = ""
                if email == ph: email = ""
                if senha == ph: senha = ""
            try:
                usuario_service.cadastrar_usuario(nome, email, senha, tipo_var.get())
                messagebox.showinfo("Sucesso", "Cadastro realizado! Faça login para continuar.")
                montar_entrar()
            except ValueError as erro:
                messagebox.showerror("Erro no Cadastro", str(erro))

        tk.Button(
            conteudo, text="CRIAR CONTA", command=criar_conta,
            bg=COR_DOURADO, fg=COR_TEXTO_CLARO, font=FONTE_BOTAO,
            relief="flat", cursor="hand2", pady=10
        ).pack(fill="x", pady=(18, 0))

    lbl_entrar.bind("<Button-1>",   lambda e: montar_entrar())
    lbl_cadastro.bind("<Button-1>", lambda e: montar_cadastro())

    montar_entrar()


def _redirecionar(root, usuario, usuario_service):
    """Redireciona para a tela correta após login."""
    from apresentacao.interface_aluno        import mostrar_interface_aluno
    from apresentacao.interface_bolsista     import mostrar_interface_bolsista
    from apresentacao.interface_bibliotecario import mostrar_interface_bibliotecario

    tipo = usuario.tipo.lower()
    if tipo == "aluno":
        mostrar_interface_aluno(root, usuario, usuario_service)
    elif tipo == "bolsista":
        mostrar_interface_bolsista(root, usuario, usuario_service)
    elif tipo == "bibliotecario":
        mostrar_interface_bibliotecario(root, usuario, usuario_service)
    else:
        messagebox.showerror("Erro", f"Tipo de usuário desconhecido: {tipo}")