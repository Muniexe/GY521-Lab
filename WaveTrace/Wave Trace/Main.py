import customtkinter as ctk
from tkinter import filedialog
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# ==========================
# Configuração
# ==========================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("1200x700")
app.title("WaveTrace")
canvas = None
df_global = None
# ==========================
# Função CSV
# ==========================

def abrir_csv():
    global canvas

    caminho = filedialog.askopenfilename(
        title="Escolha um CSV",
        filetypes=[("CSV", "*.csv")]
    )

    if not caminho:
        return

    try:
        global df_global
        df_global = pd.read_csv(caminho)
        df = df_global

        duracao = (
            df["tempo_ms"].iloc[-1] -
            df["tempo_ms"].iloc[0]
        ) / 1000

        pitch_max = df["pitch"].max()
        pitch_min = df["pitch"].min()

        roll_max = df["roll"].max()
        roll_min = df["roll"].min()

        lbl_arquivo.configure(
            text=f"Arquivo: {caminho.split('/')[-1]}"
        )

        lbl_amostras.configure(
            text=f"Amostras: {len(df)}"
        )

        lbl_duracao.configure(
            text=f"Duração: {duracao:.1f} s"
        )

        lbl_pitch.configure(
            text=f"Pitch: {pitch_min:.2f}° / {pitch_max:.2f}°"
        )

        lbl_roll.configure(
            text=f"Roll: {roll_min:.2f}° / {roll_max:.2f}°"
        )
        atualizar_grafico(variavel.get())

        global canvas

    except Exception as erro:
        lbl_arquivo.configure(
            text=f"Erro: {erro}"
        )


def atualizar_grafico(escolha):

    global canvas

    if df_global is None:
        return

    if canvas is not None:
        canvas.get_tk_widget().destroy()

    fig = Figure(figsize=(7,5), dpi=100)

    ax = fig.add_subplot(111)

    tempo = df_global["tempo_ms"] / 1000

    ax.plot(
        tempo,
        df_global[escolha],
        linewidth=2,
        label=escolha.upper()
    )

    ax.set_title(escolha.upper())
    ax.set_xlabel("Tempo (s)")
    ax.grid(True)
    ax.legend()

    canvas = FigureCanvasTkAgg(
        fig,
        master=grafico_frame
    )

    canvas.draw()
    canvas.get_tk_widget().pack(
        fill="both",
        expand=True
    )

def exportar_png():

    global df_global

    if df_global is None:
        return

    coluna = variavel.get()

    caminho = filedialog.asksaveasfilename(
        title="Salvar gráfico",
        defaultextension=".png",
        initialfile=f"WaveTrace_{coluna}.png",
        filetypes=[
            ("Imagem PNG", "*.png"),
            ("Todos os arquivos", "*.*")
        ]
    )

    if not caminho:
        return

    fig = Figure(figsize=(10, 5), dpi=300)
    ax = fig.add_subplot(111)

    tempo = df_global["tempo_ms"] / 1000

    ax.plot(
        tempo,
        df_global[coluna],
        linewidth=2,
        label=coluna.upper()
    )

    ax.set_title(f"WaveTrace - {coluna.upper()}")
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel(coluna.upper())
    ax.grid(True)
    ax.legend()

    fig.savefig(
        caminho,
        bbox_inches="tight"
    )

    print(f"Exportado para: {caminho}")
# ==========================
# Layout
# ==========================

titulo = ctk.CTkLabel(
    app,
    text="🌊 WaveTrace",
    font=("Arial", 32, "bold")
)

titulo.pack(pady=15)

# Container principal

main_frame = ctk.CTkFrame(app)
main_frame.pack(fill="both", expand=True, padx=20, pady=10)

# ==========================
# Painel esquerdo
# ==========================

info_frame = ctk.CTkFrame(main_frame, width=300)

info_frame.pack(
    side="left",
    fill="y",
    padx=(0, 10),
    pady=10
)

ctk.CTkLabel(
    info_frame,
    text="Informações",
    font=("Arial", 20, "bold")
).pack(pady=15)

lbl_arquivo = ctk.CTkLabel(
    info_frame,
    text="Nenhum arquivo carregado"
)
lbl_arquivo.pack(pady=5)

lbl_amostras = ctk.CTkLabel(
    info_frame,
    text="Amostras: --"
)
lbl_amostras.pack(pady=5)

lbl_duracao = ctk.CTkLabel(
    info_frame,
    text="Duração: --"
)
lbl_duracao.pack(pady=5)

lbl_pitch = ctk.CTkLabel(
    info_frame,
    text="Pitch: --"
)
lbl_pitch.pack(pady=5)

lbl_roll = ctk.CTkLabel(
    info_frame,
    text="Roll: --"
)
lbl_roll.pack(pady=5)

ctk.CTkLabel(
    info_frame,
    text="Variável"
).pack(pady=(20,5))

variavel = ctk.StringVar(value="pitch")

combo = ctk.CTkOptionMenu(
    info_frame,
    variable=variavel,
    values=[
        "pitch",
        "roll",
        "yaw",
        "ax",
        "ay",
        "az",
        "gx",
        "gy",
        "gz",
        "magnitude"
    ],
    command=atualizar_grafico
)

combo.pack(pady=5, padx=10)

# ==========================
# Área principal
# ==========================

grafico_frame = ctk.CTkFrame(main_frame)

grafico_frame.pack(
    side="right",
    fill="both",
    expand=True,
    pady=10
)

# ==========================
# Botões
# ==========================

bottom_frame = ctk.CTkFrame(app)
bottom_frame.pack(fill="x", padx=20, pady=10)

btn_csv = ctk.CTkButton(
    bottom_frame,
    text="📂 Abrir CSV",
    command=abrir_csv
)

btn_csv.pack(side="left", padx=10, pady=10)

btn_replay = ctk.CTkButton(
    bottom_frame,
    text="▶ Replay 3D"
)

btn_replay.pack(side="left", padx=10)

btn_exportar = ctk.CTkButton(
    bottom_frame,
    text="💾 Exportar PNG",
    command=exportar_png
)

btn_exportar.pack(side="left", padx=10)

app.mainloop()