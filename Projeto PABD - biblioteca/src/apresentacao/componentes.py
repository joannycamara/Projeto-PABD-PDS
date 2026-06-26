"""
componentes.py — Widgets reutilizáveis entre as telas.

- montar_header()   : barra superior verde com logo, perfil e botão sair
- montar_card()     : card de estatística (número grande + label)
- montar_abas()     : navegação por abas com sublinhado dourado
- botao_principal() : botão dourado padrão
- botao_secundario(): botão transparente/cinza
"""

import tkinter as tk
from tkinter import ttk
from apresentacao.estilos import (
    COR_HEADER, COR_FUNDO_INTERNO, COR_DOURADO, COR_TEXTO_CLARO,
    COR_TEXTO_SECUNDARIO, COR_LINHA_ABA, COR_VERDE_STATUS,
    FONTE_HEADER, FONTE_CARD_NUMERO, FONTE_CARD_LABEL,
    FONTE_ABA, FONTE_BOTAO, FONTE_BOTAO_PEQUENO,
)


def montar_header(root, usuario, ao_sair):
    """Barra superior verde-escuro com logo, badge de perfil e botão sair."""
    header = tk.Frame(root, bg=COR_HEADER, height=52)
    header.pack(fill="x")
    header.pack_propagate(False)

    # Logo
    tk.Label(
        header, text="📖  Biblioteca Central",
        font=FONTE_HEADER, bg=COR_HEADER, fg=COR_TEXTO_CLARO
    ).pack(side="left", padx=20)

    # Lado direito: badge perfil + sair
    direita = tk.Frame(header, bg=COR_HEADER)
    direita.pack(side="right", padx=16)

    badge = tk.Frame(direita, bg="#2d4a2d", padx=10, pady=4)
    badge.pack(side="left")

    tk.Label(badge, text="●", font=("Arial", 8), bg="#2d4a2d",
             fg=COR_VERDE_STATUS).pack(side="left")
    tk.Label(badge, text=f"  {usuario.tipo.capitalize()}  ",
             font=("Arial", 9), bg="#2d4a2d", fg=COR_TEXTO_SECUNDARIO).pack(side="left")
    tk.Label(badge, text=usuario.nome.split()[0],
             font=("Arial", 9, "bold"), bg="#2d4a2d", fg=COR_DOURADO).pack(side="left")

    tk.Button(
        direita, text="→ Sair", command=ao_sair,
        bg=COR_HEADER, fg=COR_TEXTO_SECUNDARIO, font=("Arial", 9),
        relief="flat", cursor="hand2", padx=10
    ).pack(side="left", padx=(10, 0))

    return header


def montar_card_stat(pai, numero, label, cor_numero):
    """Card branco com número grande e label pequeno abaixo."""
    card = tk.Frame(pai, bg="white", padx=20, pady=16,
                    highlightbackground="#e0d8cc", highlightthickness=1)
    card.pack(side="left", padx=8, expand=True, fill="x")

    tk.Label(card, text=str(numero), font=FONTE_CARD_NUMERO,
             bg="white", fg=cor_numero).pack(anchor="w")
    tk.Label(card, text=label, font=FONTE_CARD_LABEL,
             bg="white", fg=COR_TEXTO_SECUNDARIO).pack(anchor="w")
    return card


def montar_abas(pai, abas: list[tuple[str, callable]], cor_fundo):
    """
    Cria uma barra de abas com sublinhado dourado.
    abas = [("Rótulo", funcao_ao_clicar), ...]
    Retorna dict com os labels para controle externo.
    """
    frame = tk.Frame(pai, bg=cor_fundo)
    frame.pack(fill="x", padx=0, pady=(16, 0))

    labels = {}
    linhas = {}

    def selecionar(nome):
        for k, lbl in labels.items():
            lbl.configure(fg=COR_TEXTO_SECUNDARIO, font=FONTE_ABA)
            linhas[k].configure(bg=cor_fundo)
        labels[nome].configure(fg=COR_TEXTO_CLARO if cor_fundo == COR_HEADER else "#1a1a1a",
                               font=(*FONTE_ABA[:2], "bold"))
        linhas[nome].configure(bg=COR_DOURADO)

    for i, (rotulo, callback) in enumerate(abas):
        col = tk.Frame(frame, bg=cor_fundo)
        col.grid(row=0, column=i, padx=4)

        lbl = tk.Label(col, text=rotulo, font=FONTE_ABA,
                       bg=cor_fundo, fg=COR_TEXTO_SECUNDARIO,
                       padx=14, cursor="hand2")
        lbl.pack()

        linha = tk.Frame(col, height=2, bg=cor_fundo)
        linha.pack(fill="x")

        labels[rotulo] = lbl
        linhas[rotulo] = linha

        def on_click(ev, nome=rotulo, cb=callback):
            selecionar(nome)
            cb()

        lbl.bind("<Button-1>", on_click)

    # Seleciona a primeira aba por padrão
    primeiro = abas[0][0]
    labels[primeiro].configure(fg="#1a1a1a", font=(*FONTE_ABA[:2], "bold"))
    linhas[primeiro].configure(bg=COR_DOURADO)

    return labels


def botao_principal(pai, texto, comando, largura=None):
    kwargs = dict(
        text=texto, command=comando,
        bg=COR_DOURADO, fg=COR_TEXTO_CLARO, font=FONTE_BOTAO,
        relief="flat", cursor="hand2", pady=8,
    )
    if largura:
        kwargs["width"] = largura
    return tk.Button(pai, **kwargs)


def botao_secundario(pai, texto, comando):
    return tk.Button(
        pai, text=texto, command=comando,
        bg="#e8e0d4", fg="#444444", font=FONTE_BOTAO_PEQUENO,
        relief="flat", cursor="hand2", pady=6, padx=12,
    )


def separador(pai, cor="#e0d8cc"):
    tk.Frame(pai, height=1, bg=cor).pack(fill="x")


def treeview_estilizado(pai, colunas: list[tuple[str, str, int]], altura=12):
    """
    Cria um Treeview com estilo limpo.
    colunas = [("id_coluna", "Título", largura), ...]
    """
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Biblioteca.Treeview",
                    background="white", fieldbackground="white",
                    rowheight=28, font=("Arial", 10))
    style.configure("Biblioteca.Treeview.Heading",
                    background="#f0ece4", font=("Arial", 8, "bold"),
                    foreground="#555555")
    style.map("Biblioteca.Treeview", background=[("selected", "#e8d9b8")])

    ids = [c[0] for c in colunas]
    tree = ttk.Treeview(pai, columns=ids, show="headings",
                        height=altura, style="Biblioteca.Treeview")

    for col_id, titulo, largura in colunas:
        tree.heading(col_id, text=titulo)
        tree.column(col_id, width=largura, anchor="w")

    scroll = ttk.Scrollbar(pai, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    return tree