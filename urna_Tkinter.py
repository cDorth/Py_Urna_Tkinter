import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkFont

# --- Lógica Original (mantida) ---
candidatos = [
    {"candidato": "João Silva", "partido": "Partido do Futuro"},
    {"candidato": "Maria Oliveira", "partido": "União Nacional"},
    {"candidato": "Carlos Souza", "partido": "Movimento Progressista"},
    {"candidato": "Ana Lima", "partido": "Aliança Popular"},
    {"candidato": "Pedro Rocha", "partido": "Democracia Real"}
]
votacoes = {}
# --- Fim da Lógica Original ---

# --- Funções para a Interface Tkinter (sem alterações) ---
# ... (as funções registrar_voto e mostrar_resultados permanecem iguais) ...
def registrar_voto():
    try:
        escolha_idx = voto_var.get()
        if escolha_idx == 0:
            messagebox.showwarning("Seleção Inválida", "Por favor, selecione um candidato para votar.")
            return

        indice_lista = escolha_idx - 1
        if 0 <= indice_lista < len(candidatos):
            candidato_selecionado = candidatos[indice_lista]
            nome_candidato = candidato_selecionado["candidato"]
            partido_candidato = candidato_selecionado["partido"]

            confirmar = messagebox.askyesno(
                "Confirmar Voto",
                f"Você confirma o voto em:\n\nCandidato: {nome_candidato}\nPartido: {partido_candidato}?"
            )

            if confirmar:
                votacoes[nome_candidato] = votacoes.get(nome_candidato, 0) + 1
                status_label.config(text=f"Voto em {nome_candidato} registrado com sucesso!", fg="green")
                voto_var.set(0)
            else:
                status_label.config(text="Votação cancelada pelo usuário.", fg="orange")
        else:
             messagebox.showerror("Erro Inesperado", "Candidato selecionado inválido.")
             status_label.config(text="Erro: Candidato inválido.", fg="red")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        status_label.config(text="Ocorreu um erro ao processar o voto.", fg="red")

def mostrar_resultados():
    if not votacoes:
        messagebox.showinfo("Resultados", "Nenhum voto foi registrado ainda.")
        return

    resultado_texto = "Resultado da Votação:\n\n"
    for candidato, votos in sorted(votacoes.items()):
        resultado_texto += f"{candidato}: {votos} voto(s)\n"

    try:
        vencedor = max(votacoes, key=votacoes.get)
        votos_vencedor = votacoes[vencedor]
        empates = [c for c, v in votacoes.items() if v == votos_vencedor]
        if len(empates) > 1:
             resultado_texto += f"\nEmpate entre: {', '.join(empates)} com {votos_vencedor} votos cada!"
        else:
            resultado_texto += f"\nO vencedor da eleição é: {vencedor} com {votos_vencedor} votos!"
    except ValueError:
        resultado_texto += "\nNenhum voto para determinar um vencedor."

    messagebox.showinfo("Resultado Final da Votação", resultado_texto)
    status_label.config(text="Resultados exibidos.", fg="blue")

# --- Configuração da Interface Gráfica ---
root = tk.Tk()
root.title("Urna Eletrônica Tkinter")
# root.geometry("550x450") # Remova ou comente a definição de geometria antiga
root.configure(bg="#ECECEC")

# --- Centralização da Janela na Tela --- INÍCIO ---
window_width = 550  # Largura desejada da janela
window_height = 450 # Altura desejada da janela

# Obter as dimensões da tela
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calcular a posição x e y para centralizar a janela
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)

# Definir a geometria da janela com tamanho e posição centralizada
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
# --- Centralização da Janela na Tela --- FIM ---

# Configuração das Fontes
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(size=11)
bold_font = tkFont.Font(family=default_font["family"], size=12, weight="bold")
title_font = tkFont.Font(family=default_font["family"], size=14, weight="bold")

# Variável de controle
voto_var = tk.IntVar(value=0)

# --- Layout (mantido centralizado dentro da janela) ---
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
    botoes_frame, text="Ver Resultados", command=mostrar_resultados,
    font=bold_font, bg="#2196F3", fg="white", padx=20, pady=10, relief=tk.RAISED, bd=3
)
results_button.grid(row=0, column=1, padx=10)

status_label = tk.Label(root, text="Selecione um candidato e clique em 'Confirmar Voto'.", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#F5F5F5", padx=5, pady=5)
status_label.pack(fill=tk.X, side=tk.BOTTOM, ipady=5)

root.mainloop()