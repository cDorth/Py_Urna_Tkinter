import tkinter as tk
from tkinter import messagebox, Toplevel, Text, Scrollbar 
from tkinter import font as tkFont
import os 


candidatos = [
    {"candidato": "João Silva", "partido": "Partido do Futuro"},
    {"candidato": "Maria Oliveira", "partido": "União Nacional"},
    {"candidato": "Carlos Souza", "partido": "Movimento Progressista"},
    {"candidato": "Ana Lima", "partido": "Aliança Popular"},
    {"candidato": "Pedro Rocha", "partido": "Democracia Real"}
]
votacoes = {}

def centralizar_janela(janela, largura, altura):
    """Centraliza uma janela (Tk ou Toplevel) na tela."""
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    pos_x = int(largura_tela / 2 - largura / 2)
    pos_y = int(altura_tela / 2 - altura / 2)
    janela.geometry(f'{largura}x{altura}+{pos_x}+{pos_y}')

def determinar_vencedor(votos_dict):
    """Determina o vencedor ou informa empate a partir do dicionário de votos."""
    if not votos_dict:
        return "Nenhum voto registrado.", None # Retorna tupla (mensagem, lista_vencedores)

    votos_max = 0
    try:
      votos_max = max(votos_dict.values())
    except ValueError:
        return "Nenhum voto registrado.", None # Segurança extra

    vencedores = [candidato for candidato, votos in votos_dict.items() if votos == votos_max]

    if len(vencedores) == 1:
        return f"O vencedor da eleição é: {vencedores[0]} com {votos_max} votos!", vencedores
    elif len(vencedores) > 1:
        nomes_empate = ', '.join(vencedores)
        return f"Empate entre: {nomes_empate} com {votos_max} votos cada!", vencedores
    else: # Caso improvável de não haver vencedores apesar de votos
        return "Não foi possível determinar um vencedor.", None

# --- Funções de Interface ---
def registrar_voto():

    try:
        escolha_idx = voto_var.get()
        if escolha_idx == 0:
            messagebox.showwarning("Seleção Inválida", "Por favor, selecione um candidato para votar.", parent=root) 
            return

        indice_lista = escolha_idx - 1
        if 0 <= indice_lista < len(candidatos):
            candidato_selecionado = candidatos[indice_lista]
            nome_candidato = candidato_selecionado["candidato"]
            partido_candidato = candidato_selecionado["partido"]

            confirmar = messagebox.askyesno(
                "Confirmar Voto",
                f"Você confirma o voto em:\n\nCandidato: {nome_candidato}\nPartido: {partido_candidato}?",
                parent=root 
            )

            if confirmar:
                votacoes[nome_candidato] = votacoes.get(nome_candidato, 0) + 1
                status_label.config(text=f"Voto em {nome_candidato} registrado com sucesso!", fg="green")
                voto_var.set(0)
            else:
                status_label.config(text="Votação cancelada pelo usuário.", fg="orange")
        else:
             messagebox.showerror("Erro Inesperado", "Candidato selecionado inválido.", parent=root) 
             status_label.config(text="Erro: Candidato inválido.", fg="red")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}", parent=root) 
        status_label.config(text="Ocorreu um erro ao processar o voto.", fg="red")

def exportar_resultados():
    """Gera o arquivo Candidatos.txt com a lista e o resultado."""
    script_dir = os.path.dirname(os.path.abspath(__file__)) 
    filepath = os.path.join(script_dir, "Candidatos.txt")

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("=== Lista de Candidatos ===\n")
            for idx, cand in enumerate(candidatos, start=1):
                f.write(f"{idx} - {cand['candidato']} ({cand['partido']})\n")

            f.write("\n=== Resultado da Votação ===\n")
            if not votacoes:
                f.write("Nenhum voto foi registrado.\n")
            else:
                # Exibe a contagem de todos que receberam votos
                for candidato, votos in sorted(votacoes.items()):
                     f.write(f"{candidato}: {votos} voto(s)\n")

                # Determina e escreve o vencedor/empate
                mensagem_vencedor, _ = determinar_vencedor(votacoes) 
                f.write(f"\n{mensagem_vencedor}\n")

        messagebox.showinfo("Exportação Concluída", f"Resultados exportados com sucesso para:\n{filepath}", parent=resultados_window) 
    except Exception as e:
        messagebox.showerror("Erro de Exportação", f"Não foi possível salvar o arquivo:\n{e}", parent=resultados_window) 

# Variável global para a janela de resultados, para referência no messagebox da exportação
resultados_window = None

def mostrar_resultados():
    """Exibe os resultados da votação em uma nova janela Toplevel."""
    global resultados_window # Permite modificar a variável global

    if not votacoes:
        messagebox.showinfo("Resultados", "Nenhum voto foi registrado ainda.", parent=root)
        return

    # Cria a janela Toplevel se ainda não existir ou se foi fechada
    if resultados_window is None or not tk.Toplevel.winfo_exists(resultados_window):
        resultados_window = Toplevel(root)
        resultados_window.title("Resultados da Votação")
        resultados_window.configure(bg="#F0F0F0")
        resultados_window.transient(root) # Mantém a janela de resultados na frente da principal
        resultados_window.grab_set() # Impede interação com a janela principal enquanto esta estiver aberta

        # Definir tamanho e centralizar
        largura_res = 450
        altura_res = 400
        centralizar_janela(resultados_window, largura_res, altura_res)


        frame_res = tk.Frame(resultados_window, bg="#F0F0F0", padx=15, pady=15)
        frame_res.pack(expand=True, fill="both")

        titulo_res = tk.Label(frame_res, text="Resultado Detalhado", font=title_font, bg="#F0F0F0", pady=10)
        titulo_res.pack()

        # Área de texto para resultados com scrollbar
        text_frame = tk.Frame(frame_res)
        text_frame.pack(pady=5, fill="both", expand=True)

        scrollbar = Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        resultado_text_widget = Text(text_frame, wrap="word", font=default_font,
                                     yscrollcommand=scrollbar.set, bd=1, relief=tk.SUNKEN,
                                     padx=5, pady=5, height=10) 
        resultado_text_widget.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.config(command=resultado_text_widget.yview)

        # Preenche a área de texto
        resultado_text_widget.insert(tk.END, "Contagem de Votos:\n\n")
        for candidato, votos in sorted(votacoes.items()):
            resultado_text_widget.insert(tk.END, f"  {candidato}: {votos} voto(s)\n")

        resultado_text_widget.insert(tk.END, "\n" + ("-"*40) + "\n\n") 

        # Adiciona o vencedor
        mensagem_vencedor, _ = determinar_vencedor(votacoes)
        resultado_text_widget.insert(tk.END, mensagem_vencedor + "\n")

        # Desabilita edição no Text widget
        resultado_text_widget.config(state=tk.DISABLED)

        # --- Botões na Janela de Resultados ---
        botoes_res_frame = tk.Frame(frame_res, bg="#F0F0F0", pady=10)
        botoes_res_frame.pack(fill=tk.X)

        export_button = tk.Button(
            botoes_res_frame,
            text="Exportar (.txt)",
            command=exportar_resultados, # Chama a nova função
            font=bold_font, bg="#FF9800", fg="white", padx=15, pady=8, relief=tk.RAISED, bd=2
        )
        # Centralizar botões no frame deles
        export_button.pack(side=tk.LEFT, padx=(0, 5), expand=True)

        close_button = tk.Button(
            botoes_res_frame,
            text="Fechar",
            command=resultados_window.destroy, # Fecha apenas esta janela
            font=bold_font, bg="#F44336", fg="white", padx=15, pady=8, relief=tk.RAISED, bd=2
        )
        close_button.pack(side=tk.RIGHT, padx=(5, 0), expand=True)

        # Ao fechar a janela pelo 'X', liberar o grab_set
        resultados_window.protocol("WM_DELETE_WINDOW", lambda: (resultados_window.grab_release(), resultados_window.destroy()))

    else:
         # Se a janela já existe, apenas traga para frente
         resultados_window.lift()
         resultados_window.grab_set() # Garante que o foco volte


# --- Configuração da Interface Gráfica Principal (root) ---
root = tk.Tk()
root.title("Urna Eletrônica Tkinter")
root.configure(bg="#ECECEC")

# Centralizar Janela Principal
window_width = 550
window_height = 450
centralizar_janela(root, window_width, window_height)

# Configuração das Fontes 
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(size=11)
bold_font = tkFont.Font(family=default_font["family"], size=12, weight="bold")
title_font = tkFont.Font(family=default_font["family"], size=14, weight="bold")

# Variável de controle 
voto_var = tk.IntVar(value=0)


main_content_frame = tk.Frame(root, bg="#ECECEC")
main_content_frame.pack(expand=True, fill="both", padx=20, pady=10)

title_label = tk.Label(main_content_frame, text="Escolha seu Candidato", font=title_font, bg="#ECECEC", pady=15)
title_label.pack()

candidatos_frame = tk.Frame(main_content_frame, bg="#ECECEC", bd=2, relief=tk.GROOVE)
candidatos_frame.pack(pady=10)

for idx, cand in enumerate(candidatos, start=1):
    texto_candidato = f"{idx} - {cand['candidato']} ({cand['partido']})"
    rb = tk.Radiobutton(
        candidatos_frame, text=texto_candidato, variable=voto_var, value=idx,
        anchor="w", font=default_font, bg="#ECECEC", padx=10, pady=5,
        indicatoron=0, selectcolor="#D0D0FF", width=40
    )
    rb.pack(fill=tk.X, padx=5, pady=2)

botoes_frame = tk.Frame(main_content_frame, bg="#ECECEC")
botoes_frame.pack(pady=15)

vote_button = tk.Button(
    botoes_frame, text="Confirmar Voto", command=registrar_voto,
    font=bold_font, bg="#4CAF50", fg="white", padx=20, pady=10, relief=tk.RAISED, bd=3
)
vote_button.grid(row=0, column=0, padx=10)

results_button = tk.Button(
    botoes_frame, text="Ver Resultados", command=mostrar_resultados, # Chama a função modificada
    font=bold_font, bg="#2196F3", fg="white", padx=20, pady=10, relief=tk.RAISED, bd=3
)
results_button.grid(row=0, column=1, padx=10)

status_label = tk.Label(root, text="Selecione um candidato e clique em 'Confirmar Voto'.", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#F5F5F5", padx=5, pady=5)
status_label.pack(fill=tk.X, side=tk.BOTTOM, ipady=5)

root.mainloop()