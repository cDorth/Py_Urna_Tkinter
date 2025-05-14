import tkinter as tk
from tkinter import messagebox, Toplevel, Text, Scrollbar, filedialog
from tkinter import font as tkFont
import cv2
import os
import shutil # Para copiar arquivos de imagem
from PIL import Image, ImageTk # Para manipulação e exibição de imagens

# --- Constantes ---
IMAGENS_DIR = "imagens_candidatos" 
PLACEHOLDER_IMAGE_PATH = "placeholder.png" 
TAMANHO_PREVIEW_CADASTRO = (100, 100)
TAMANHO_EXIBICAO_PRINCIPAL = (150, 150)

# --- Dados Globais Dinâmicos ---
candidatos = []
votacoes = {}

# --- Janelas e Widgets Globais ---
root = None
status_label = None
voto_var = None
candidatos_frame = None
vote_button = None
label_imagem_candidato_selecionado = None # Label para exibir a imagem na tela principal
imagem_tk_principal = None # Para manter referência da imagem na tela principal

# Janelas Toplevel
resultados_window = None
cadastro_window = None

# Elementos da Janela de Cadastro
entry_nome_candidato_cadastro = None
entry_partido_candidato_cadastro = None
label_preview_imagem_cadastro = None
imagem_path_atual_cadastro = None # Caminho da imagem selecionada/capturada no cadastro
imagem_tk_preview_cadastro = None # Para manter referência da imagem no preview

# Fontes (definidas globalmente)
default_font = None
bold_font = None
title_font = None

# --- Funções Auxiliares ---
def criar_pasta_imagens():
    if not os.path.exists(IMAGENS_DIR):
        try:
            os.makedirs(IMAGENS_DIR)
        except OSError as e:
            messagebox.showerror("Erro", f"Não foi possível criar a pasta de imagens: {e}", parent=root)
            return False
    return True

def criar_placeholder_se_nao_existir():
    if not os.path.exists(PLACEHOLDER_IMAGE_PATH):
        try:
            # Tenta criar um placeholder simples se não existir
            img = Image.new('RGB', (100, 100), color = (200, 200, 200))
            draw = ImageDraw.Draw(img)
            draw.text((10,0), "Sem Imagem", fill=(0,0,0))
            img.save(PLACEHOLDER_IMAGE_PATH)
        except Exception:
            # Se PIL não estiver disponível para criar, pelo menos não falha
            print(f"Aviso: Não foi possível criar {PLACEHOLDER_IMAGE_PATH}. Por favor, crie manualmente.")
            pass


def carregar_e_redimensionar_imagem(path, tamanho):
    try:
        if not path or not os.path.exists(path):
            # Tenta usar o placeholder se o caminho for inválido
            if os.path.exists(PLACEHOLDER_IMAGE_PATH):
                path = PLACEHOLDER_IMAGE_PATH
            else: # Último recurso, retorna None se nem o placeholder existir
                print(f"Aviso: Imagem {path} não encontrada e placeholder também não.")
                return None

        img = Image.open(path)
        img.thumbnail(tamanho, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Erro ao carregar/redimensionar imagem {path}: {e}")
        # Tenta carregar placeholder em caso de erro com a imagem original
        try:
            if os.path.exists(PLACEHOLDER_IMAGE_PATH):
                img = Image.open(PLACEHOLDER_IMAGE_PATH)
                img.thumbnail(tamanho, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
        except Exception as e2:
            print(f"Erro ao carregar placeholder: {e2}")
            return None


def centralizar_janela(janela, largura, altura):
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    pos_x = int(largura_tela / 2 - largura / 2)
    pos_y = int(altura_tela / 2 - altura / 2)
    janela.geometry(f'{largura}x{altura}+{pos_x}+{pos_y}')

def determinar_vencedor(votos_dict):
    if not votos_dict: return "Nenhum voto registrado.", None
    try: votos_max = max(votos_dict.values())
    except ValueError: return "Nenhum voto registrado.", None
    vencedores = [c for c, v in votos_dict.items() if v == votos_max]
    if len(vencedores) == 1: return f"O vencedor da eleição é: {vencedores[0]} com {votos_max} votos!", vencedores
    elif len(vencedores) > 1: return f"Empate entre: {', '.join(vencedores)} com {votos_max} votos cada!", vencedores
    return "Não foi possível determinar um vencedor.", None

# --- Funções de Cadastro de Candidatos ---
def selecionar_imagem_arquivo_para_cadastro():
    global imagem_path_atual_cadastro, label_preview_imagem_cadastro, imagem_tk_preview_cadastro

    filepath = filedialog.askopenfilename(
        title="Selecionar Imagem do Candidato",
        filetypes=[("Arquivos de Imagem", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos os arquivos", "*.*")],
        parent=cadastro_window
    )
    if not filepath:
        return

    # Copiar imagem para a pasta do projeto e usar um nome padronizado/único
    filename = os.path.basename(filepath)
    novo_path = os.path.join(IMAGENS_DIR, filename)

    try:
        shutil.copy(filepath, novo_path)
        imagem_path_atual_cadastro = novo_path # Armazena o caminho da imagem COPIADA

        # Atualizar preview
        imagem_tk_preview_cadastro = carregar_e_redimensionar_imagem(imagem_path_atual_cadastro, TAMANHO_PREVIEW_CADASTRO)
        if imagem_tk_preview_cadastro:
            label_preview_imagem_cadastro.config(image=imagem_tk_preview_cadastro)
        else:
            label_preview_imagem_cadastro.config(image='') # Limpa se falhar
            messagebox.showwarning("Imagem", "Não foi possível carregar o preview da imagem.", parent=cadastro_window)

    except Exception as e:
        messagebox.showerror("Erro ao Copiar Imagem", f"Não foi possível processar a imagem: {e}", parent=cadastro_window)
        imagem_path_atual_cadastro = None
        label_preview_imagem_cadastro.config(image='')

def abrir_janela_webcam_para_cadastro():
    global imagem_path_atual_cadastro, label_preview_imagem_cadastro, imagem_tk_preview_cadastro

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Erro", "Não foi possível acessar a webcam.", parent=cadastro_window)
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Captura - Pressione Espaço para salvar", frame)

        key = cv2.waitKey(1)
        if key == 27:  # ESC para cancelar
            break
        elif key == 32:  # Espaço para capturar
            nome_arquivo = os.path.join(IMAGENS_DIR, f"webcam_{len(os.listdir(IMAGENS_DIR)) + 1}.jpg")
            cv2.imwrite(nome_arquivo, frame)
            imagem_path_atual_cadastro = nome_arquivo
            break

    cap.release()
    cv2.destroyAllWindows()

    # Atualizar preview
    imagem_tk_preview_cadastro = carregar_e_redimensionar_imagem(imagem_path_atual_cadastro, TAMANHO_PREVIEW_CADASTRO)
    if imagem_tk_preview_cadastro:
        label_preview_imagem_cadastro.config(image=imagem_tk_preview_cadastro)
    else:
        label_preview_imagem_cadastro.config(image='')
        messagebox.showwarning("Imagem", "Erro ao carregar a imagem capturada.", parent=cadastro_window)


def abrir_janela_cadastro():
    global cadastro_window, entry_nome_candidato_cadastro, entry_partido_candidato_cadastro
    global label_preview_imagem_cadastro, imagem_path_atual_cadastro, imagem_tk_preview_cadastro

    imagem_path_atual_cadastro = None # Reseta para cada novo cadastro
    imagem_tk_preview_cadastro = None

    if cadastro_window is None or not tk.Toplevel.winfo_exists(cadastro_window):
        cadastro_window = Toplevel(root)
        cadastro_window.title("Cadastrar Novo Candidato")
        cadastro_window.configure(bg="#F5F5F5")
        cadastro_window.transient(root)
        cadastro_window.grab_set()

        largura_cad = 450
        altura_cad = 380 # Aumentar altura para preview e botões de imagem
        centralizar_janela(cadastro_window, largura_cad, altura_cad)

        frame_cad = tk.Frame(cadastro_window, bg="#F5F5F5", padx=20, pady=20)
        frame_cad.pack(expand=True, fill="both")

        # Campos de Texto
        tk.Label(frame_cad, text="Nome Candidato:", font=default_font, bg="#F5F5F5").grid(row=0, column=0, sticky="w", pady=3)
        entry_nome_candidato_cadastro = tk.Entry(frame_cad, font=default_font, width=35, bd=2)
        entry_nome_candidato_cadastro.grid(row=0, column=1, columnspan=2, pady=3, padx=5, sticky="ew")

        tk.Label(frame_cad, text="Partido:", font=default_font, bg="#F5F5F5").grid(row=1, column=0, sticky="w", pady=3)
        entry_partido_candidato_cadastro = tk.Entry(frame_cad, font=default_font, width=35, bd=2)
        entry_partido_candidato_cadastro.grid(row=1, column=1, columnspan=2, pady=3, padx=5, sticky="ew")

        # Preview da Imagem
        tk.Label(frame_cad, text="Imagem:", font=default_font, bg="#F5F5F5").grid(row=2, column=0, sticky="nw", pady=10)
        label_preview_imagem_cadastro = tk.Label(frame_cad, relief=tk.SUNKEN, bg="white", bd=1) # Ajuste de tamanho
        label_preview_imagem_cadastro.grid(row=2, column=1, columnspan=2, pady=5, sticky="w")
        imagem_tk_preview_cadastro = carregar_e_redimensionar_imagem(None, TAMANHO_PREVIEW_CADASTRO) # Carrega placeholder inicial
        if imagem_tk_preview_cadastro:
            label_preview_imagem_cadastro.config(image=imagem_tk_preview_cadastro)


        # Botões de Imagem
        btn_selecionar_img = tk.Button(frame_cad, text="Selecionar Imagem", command=selecionar_imagem_arquivo_para_cadastro,
                                       font=default_font, bg="#5bc0de", fg="white")
        btn_selecionar_img.grid(row=3, column=1, pady=5, sticky="ew")

        btn_webcam_img = tk.Button(frame_cad, text="Usar Webcam", command=abrir_janela_webcam_para_cadastro,
                                   font=default_font, bg="#f0ad4e", fg="white")
        btn_webcam_img.grid(row=3, column=2, pady=5, padx=5, sticky="ew")


        # Botões de Ação
        botoes_acao_cad_frame = tk.Frame(frame_cad, bg="#F5F5F5", pady=15)
        botoes_acao_cad_frame.grid(row=4, column=0, columnspan=3, pady=10)

        btn_salvar = tk.Button(botoes_acao_cad_frame, text="Salvar Candidato", command=salvar_novo_candidato,
                               font=bold_font, bg="#007bff", fg="white", padx=10, pady=5)
        btn_salvar.pack(side=tk.LEFT, padx=10)

        btn_cancelar = tk.Button(botoes_acao_cad_frame, text="Cancelar",
                                 command=lambda: (cadastro_window.grab_release(), cadastro_window.destroy()),
                                 font=bold_font, bg="#6c757d", fg="white", padx=10, pady=5)
        btn_cancelar.pack(side=tk.LEFT, padx=10)

        frame_cad.columnconfigure(1, weight=1)
        frame_cad.columnconfigure(2, weight=1)
        entry_nome_candidato_cadastro.focus_set()
        cadastro_window.protocol("WM_DELETE_WINDOW", lambda: (cadastro_window.grab_release(), cadastro_window.destroy()))
    else:
        cadastro_window.lift()
        cadastro_window.grab_set()

def salvar_novo_candidato():
    global candidatos, imagem_path_atual_cadastro
    nome = entry_nome_candidato_cadastro.get().strip()
    partido = entry_partido_candidato_cadastro.get().strip()

    if not nome or not partido:
        messagebox.showerror("Erro de Cadastro", "Nome e partido são obrigatórios!", parent=cadastro_window)
        return
    for cand in candidatos:
        if cand["candidato"].lower() == nome.lower():
            messagebox.showwarning("Cadastro Duplicado", f"Candidato '{nome}' já cadastrado.", parent=cadastro_window)
            return

    # Se imagem_path_atual_cadastro for None, significa que nenhuma imagem foi selecionada
    # Você pode optar por atribuir um placeholder padrão aqui ou deixar como None
    caminho_final_imagem = imagem_path_atual_cadastro # Já é o caminho na pasta IMAGENS_DIR

    novo_candidato = {"candidato": nome, "partido": partido, "imagem_path": caminho_final_imagem}
    candidatos.append(novo_candidato)
    messagebox.showinfo("Cadastro Realizado", f"Candidato '{nome}' cadastrado!", parent=cadastro_window)

    if cadastro_window:
        cadastro_window.grab_release()
        cadastro_window.destroy()
    atualizar_lista_candidatos_ui()
    _atualizar_imagem_exibida() # Limpa/atualiza imagem na tela principal


def atualizar_lista_candidatos_ui():
    global candidatos_frame, voto_var, vote_button, default_font

    for widget in candidatos_frame.winfo_children():
        widget.destroy()
    voto_var.set(0)

    if not candidatos:
        tk.Label(candidatos_frame, text="Nenhum candidato cadastrado.", font=default_font, bg="#ECECEC", pady=20, fg="#555").pack(pady=10)
        if vote_button: vote_button.config(state=tk.DISABLED)
        _atualizar_imagem_exibida() # Limpa imagem principal
        return
    else:
        if vote_button: vote_button.config(state=tk.NORMAL)

    # Scrollable Frame para os Radiobuttons
    canvas = tk.Canvas(candidatos_frame, bg="#ECECEC", highlightthickness=0)
    scrollbar_cand = tk.Scrollbar(candidatos_frame, orient="vertical", command=canvas.yview)
    scrollable_frame_cand = tk.Frame(canvas, bg="#ECECEC")

    scrollable_frame_cand.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame_cand, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar_cand.set)

    for idx, cand_info in enumerate(candidatos, start=1):
        texto_candidato = f"{idx} - {cand_info['candidato']} ({cand_info['partido']})"
        rb = tk.Radiobutton(
            scrollable_frame_cand, text=texto_candidato, variable=voto_var, value=idx,
            anchor="w", font=default_font, bg="#ECECEC", padx=10, pady=5,
            indicatoron=0, selectcolor="#D0D0FF", width=40, relief=tk.FLAT, overrelief=tk.GROOVE,
            command=_atualizar_imagem_exibida # Chama ao selecionar
        )
        rb.pack(fill=tk.X, padx=5, pady=2)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar_cand.pack(side="right", fill="y")


def _atualizar_imagem_exibida():
    global label_imagem_candidato_selecionado, imagem_tk_principal
    path_imagem_selecionada = None
    try:
        escolha_idx = voto_var.get()
        if escolha_idx > 0 and (escolha_idx -1) < len(candidatos):
            path_imagem_selecionada = candidatos[escolha_idx-1].get("imagem_path")
    except:
        pass # Se não houver seleção ou erro, path_imagem_selecionada permanece None

    imagem_tk_principal = carregar_e_redimensionar_imagem(path_imagem_selecionada, TAMANHO_EXIBICAO_PRINCIPAL)
    if imagem_tk_principal:
        label_imagem_candidato_selecionado.config(image=imagem_tk_principal)
    else:
        # Se falhar ao carregar ou não tiver imagem, limpa ou usa placeholder padrão (já tratado em carregar_e_redimensionar)
        placeholder_img = carregar_e_redimensionar_imagem(None, TAMANHO_EXIBICAO_PRINCIPAL)
        label_imagem_candidato_selecionado.config(image=placeholder_img if placeholder_img else '')
        if not placeholder_img : label_imagem_candidato_selecionado.config(text="Sem Imagem")


# --- Funções de Votação e Resultados (com pequenas adaptações) ---
def registrar_voto():
    try:
        escolha_idx = voto_var.get()
        if escolha_idx == 0:
            messagebox.showwarning("Seleção Inválida", "Selecione um candidato.", parent=root)
            return
        indice_lista = escolha_idx - 1
        if 0 <= indice_lista < len(candidatos):
            nome_candidato = candidatos[indice_lista]["candidato"]
            confirmar = messagebox.askyesno("Confirmar Voto", f"Confirma voto em {nome_candidato}?", parent=root)
            if confirmar:
                votacoes[nome_candidato] = votacoes.get(nome_candidato, 0) + 1
                status_label.config(text=f"Voto em {nome_candidato} registrado!", fg="green")
                voto_var.set(0)
                _atualizar_imagem_exibida() # Limpa imagem após voto
            else:
                status_label.config(text="Votação cancelada.", fg="orange")
        else:
             messagebox.showerror("Erro", "Candidato inválido.", parent=root)
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}", parent=root)

def exportar_resultados():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, "Candidatos_e_Resultados.txt")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("=== Lista de Candidatos Cadastrados ===\n")
            if not candidatos: f.write("Nenhum candidato cadastrado.\n")
            else:
                for idx, cand in enumerate(candidatos, start=1):
                    f.write(f"{idx} - {cand['candidato']} ({cand['partido']}) - Imagem: {cand.get('imagem_path', 'Nenhuma')}\n")
            f.write("\n=== Resultado da Votação ===\n")
            if not votacoes: f.write("Nenhum voto foi registrado.\n")
            else:
                for c, v in sorted(votacoes.items()): f.write(f"{c}: {v} voto(s)\n")
                msg_vencedor, _ = determinar_vencedor(votacoes)
                f.write(f"\n{msg_vencedor}\n")
        messagebox.showinfo("Exportação", f"Resultados exportados para:\n{filepath}", parent=resultados_window)
    except Exception as e:
        messagebox.showerror("Erro Exportação", f"Falha ao salvar:\n{e}", parent=resultados_window)

def mostrar_resultados():
    global resultados_window, default_font, title_font
    if not votacoes and not candidatos : # Verifica se há algo para mostrar
        messagebox.showinfo("Resultados", "Nenhum candidato cadastrado ou voto registrado.", parent=root)
        return
    if not votacoes :
        messagebox.showinfo("Resultados", "Nenhum voto foi registrado ainda (mas há candidatos).", parent=root)
        # Poderia mostrar só a lista de candidatos se quisesse

    if resultados_window is None or not tk.Toplevel.winfo_exists(resultados_window):
        resultados_window = Toplevel(root)
        resultados_window.title("Resultados da Votação")

        resultados_window.configure(bg="#F0F0F0")
        resultados_window.transient(root)
        resultados_window.grab_set()
        largura_res, altura_res = 450, 400
        centralizar_janela(resultados_window, largura_res, altura_res)
        frame_res = tk.Frame(resultados_window, bg="#F0F0F0", padx=15, pady=15)
        frame_res.pack(expand=True, fill="both")
        tk.Label(frame_res, text="Resultado Detalhado", font=title_font, bg="#F0F0F0", pady=10).pack()
        text_frame = tk.Frame(frame_res)
        text_frame.pack(pady=5, fill="both", expand=True)
        scrollbar = Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        resultado_text_widget = Text(text_frame, wrap="word", font=default_font,
                                     yscrollcommand=scrollbar.set, bd=1, relief=tk.SUNKEN,
                                     padx=5, pady=5, height=10)
        resultado_text_widget.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.config(command=resultado_text_widget.yview)

        resultado_text_widget.insert(tk.END, "Candidatos Cadastrados:\n")
        if not candidatos: resultado_text_widget.insert(tk.END, "Nenhum.\n")
        for cand_info in candidatos:
             resultado_text_widget.insert(tk.END, f" - {cand_info['candidato']} ({cand_info['partido']})\n")

        resultado_text_widget.insert(tk.END, "\nContagem de Votos:\n")
        if not votacoes: resultado_text_widget.insert(tk.END, "Nenhum voto.\n")
        for cand_nome, votos_count in sorted(votacoes.items()):
            resultado_text_widget.insert(tk.END, f"  {cand_nome}: {votos_count} voto(s)\n")

        resultado_text_widget.insert(tk.END, "\n" + ("-"*40) + "\n\n")
        mensagem_vencedor, _ = determinar_vencedor(votacoes)
        resultado_text_widget.insert(tk.END, mensagem_vencedor + "\n")
        resultado_text_widget.config(state=tk.DISABLED)

        botoes_res_frame = tk.Frame(frame_res, bg="#F0F0F0", pady=10)
        botoes_res_frame.pack(fill=tk.X)
        tk.Button(botoes_res_frame, text="Exportar (.txt)", command=exportar_resultados,
                                  font=bold_font, bg="#FF9800", fg="white", padx=15, pady=8).pack(side=tk.LEFT, padx=(0, 5), expand=True)
        tk.Button(botoes_res_frame, text="Fechar", command=lambda: (resultados_window.grab_release(), resultados_window.destroy()),
                                 font=bold_font, bg="#F44336", fg="white", padx=15, pady=8).pack(side=tk.RIGHT, padx=(5, 0), expand=True)

        resultados_window.protocol("WM_DELETE_WINDOW", lambda: (resultados_window.grab_release(), resultados_window.destroy()))
    else:
         resultados_window.lift()
         resultados_window.grab_set()

# --- Configuração da Interface Gráfica Principal (root) ---
def criar_interface_principal():
    global root, status_label, voto_var, candidatos_frame, vote_button
    global default_font, bold_font, title_font, label_imagem_candidato_selecionado

    if not criar_pasta_imagens():

        pass


    root = tk.Tk()
    root.title("Urna Eletrônica com Imagens")
    root.configure(bg="#ECECEC")
    window_width, window_height = 750, 550 # Aumentar para caber imagem
    centralizar_janela(root, window_width, window_height)

    default_font = tkFont.nametofont("TkDefaultFont"); default_font.configure(size=10, family="Segoe UI")
    bold_font = tkFont.Font(family=default_font["family"], size=11, weight="bold")
    title_font = tkFont.Font(family=default_font["family"], size=14, weight="bold")

    voto_var = tk.IntVar(value=0)

    # Frame principal para layout
    main_app_frame = tk.Frame(root, bg="#ECECEC")
    main_app_frame.pack(expand=True, fill="both", padx=10, pady=10)

    # Coluna da Esquerda (Cadastro, Lista de Candidatos)
    left_column_frame = tk.Frame(main_app_frame, bg="#ECECEC", padx=10)
    left_column_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    title_label = tk.Label(left_column_frame, text="Sistema de Votação", font=title_font, bg="#ECECEC", pady=10)
    title_label.pack()
    tk.Button(left_column_frame, text="Cadastrar Candidato", command=abrir_janela_cadastro,
              font=bold_font, bg="#17a2b8", fg="white", padx=10, pady=6).pack(pady=8, fill=tk.X)
    tk.Label(left_column_frame, text="Escolha seu Candidato:", font=tkFont.Font(family=default_font["family"], size=12), bg="#ECECEC", pady=5).pack(anchor="w")
    
    # Frame para os Radiobuttons com borda
    candidatos_outer_frame = tk.Frame(left_column_frame, bg="#ECECEC", bd=1, relief=tk.GROOVE)
    candidatos_outer_frame.pack(pady=5, fill=tk.BOTH, expand=True)
    candidatos_frame = tk.Frame(candidatos_outer_frame, bg="#ECECEC") # Frame interno para o scroll
    candidatos_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


    # Coluna da Direita (Imagem do Candidato, Botões de Ação)
    right_column_frame = tk.Frame(main_app_frame, bg="#ECECEC", padx=10, width=TAMANHO_EXIBICAO_PRINCIPAL[0] + 40)
    right_column_frame.pack(side=tk.RIGHT, fill=tk.Y)
    right_column_frame.pack_propagate(False) # Impede que o frame encolha para o tamanho dos filhos

    tk.Label(right_column_frame, text="Candidato", font=tkFont.Font(family=default_font["family"], size=12), bg="#ECECEC", pady=10).pack()
    label_imagem_candidato_selecionado = tk.Label(right_column_frame, relief=tk.RIDGE, bg="white", bd=1)
    label_imagem_candidato_selecionado.pack(pady=5)
    _atualizar_imagem_exibida() # Carrega placeholder inicial na imagem principal

    botoes_acao_frame = tk.Frame(right_column_frame, bg="#ECECEC", pady=20)
    botoes_acao_frame.pack(side=tk.BOTTOM, fill=tk.X) # Coloca os botões no final da coluna direita

    vote_button = tk.Button(botoes_acao_frame, text="Confirmar Voto", command=registrar_voto,
                            font=bold_font, bg="#4CAF50", fg="white", padx=15, pady=8)
    vote_button.pack(pady=5, fill=tk.X)
    results_button = tk.Button(botoes_acao_frame, text="Ver Resultados", command=mostrar_resultados,
                               font=bold_font, bg="#2196F3", fg="white", padx=15, pady=8)
    results_button.pack(pady=5, fill=tk.X)

    # Status Bar
    status_label = tk.Label(root, text="Pronto.", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#F5F5F5", padx=5, pady=3, font=default_font)
    status_label.pack(fill=tk.X, side=tk.BOTTOM)

    atualizar_lista_candidatos_ui()
    root.mainloop()

if __name__ == "__main__":
    # Para ImageDraw (se for usado no placeholder)
    try: from PIL import ImageDraw
    except ImportError: ImageDraw = None

    criar_interface_principal()
def limpar_imagens_ao_sair():
    if os.path.exists(IMAGENS_DIR):
        for file in os.listdir(IMAGENS_DIR):
            caminho = os.path.join(IMAGENS_DIR, file)
            try:
                os.remove(caminho)
            except Exception as e:
                print(f"Erro ao remover imagem: {caminho} -> {e}")
try:
    root.mainloop()
finally:
    limpar_imagens_ao_sair()