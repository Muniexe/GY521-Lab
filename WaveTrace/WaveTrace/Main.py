import customtkinter as ctk
from tkinter import filedialog
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from replay import iniciar_replay

# ==========================
# Configuração da UI
# ==========================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLUNAS = ["pitch", "roll", "yaw", "ax", "ay", "az", "gx", "gy", "gz", "magnitude"]

app = ctk.CTk()
app.geometry("1200x700")
app.title("WaveTrace")

canvas_grafico = None
df_global      = None


# ==========================
# Funções de dados
# ==========================

def abrir_csv():
    global df_global

    caminho = filedialog.askopenfilename(
        title="Escolha um CSV",
        filetypes=[("CSV", "*.csv")]
    )
    if not caminho:
        return

    try:
        df_global = pd.read_csv(caminho)
        df = df_global

        duracao   = (df["tempo_ms"].iloc[-1] - df["tempo_ms"].iloc[0]) / 1000
        pitch_min, pitch_max = df["pitch"].min(), df["pitch"].max()
        roll_min,  roll_max  = df["roll"].min(),  df["roll"].max()

        lbl_arquivo.configure(text=f"Arquivo: {caminho.split('/')[-1]}")
        lbl_amostras.configure(text=f"Amostras: {len(df)}")
        lbl_duracao.configure(text=f"Duração: {duracao:.1f} s")
        lbl_pitch.configure(text=f"Pitch: {pitch_min:.2f}° / {pitch_max:.2f}°")
        lbl_roll.configure(text=f"Roll:  {roll_min:.2f}° / {roll_max:.2f}°")

        atualizar_grafico(variavel.get())

    except Exception as erro:
        lbl_arquivo.configure(text=f"Erro ao abrir: {erro}")


# ==========================
# Funções de gráfico
# ==========================

def atualizar_grafico(escolha):
    global canvas_grafico

    if df_global is None:
        return

    if canvas_grafico is not None:
        canvas_grafico.get_tk_widget().destroy()

    fig = Figure(figsize=(7, 5), dpi=100)
    ax  = fig.add_subplot(111)
    tempo = df_global["tempo_ms"] / 1000

    ax.plot(tempo, df_global[escolha], linewidth=2, label=escolha.upper())
    ax.set_title(escolha.upper())
    ax.set_xlabel("Tempo (s)")
    ax.grid(True)
    ax.legend()

    canvas_grafico = FigureCanvasTkAgg(fig, master=grafico_frame)
    canvas_grafico.draw()
    canvas_grafico.get_tk_widget().pack(fill="both", expand=True)


def exportar_png():
    if df_global is None:
        return

    coluna  = variavel.get()
    caminho = filedialog.asksaveasfilename(
        title="Salvar gráfico",
        defaultextension=".png",
        initialfile=f"WaveTrace_{coluna}.png",
        filetypes=[("Imagem PNG", "*.png"), ("Todos os arquivos", "*.*")]
    )
    if not caminho:
        return

    fig = Figure(figsize=(10, 5), dpi=300)
    ax  = fig.add_subplot(111)
    tempo = df_global["tempo_ms"] / 1000

    ax.plot(tempo, df_global[coluna], linewidth=2, label=coluna.upper())
    ax.set_title(f"WaveTrace – {coluna.upper()}")
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel(coluna.upper())
    ax.grid(True)
    ax.legend()

    fig.savefig(caminho, bbox_inches="tight")
    print(f"Exportado para: {caminho}")


# ==========================
# Layout – título
# ==========================

ctk.CTkLabel(app, text="🌊 WaveTrace", font=("Arial", 32, "bold")).pack(pady=15)

# ==========================
# Layout – container principal
# ==========================

main_frame = ctk.CTkFrame(app)
main_frame.pack(fill="both", expand=True, padx=20, pady=10)

# ---------- painel esquerdo (informações) ----------

info_frame = ctk.CTkFrame(main_frame, width=300)
info_frame.pack(side="left", fill="y", padx=(0, 10), pady=10)

ctk.CTkLabel(info_frame, text="Informações", font=("Arial", 20, "bold")).pack(pady=15)

lbl_arquivo  = ctk.CTkLabel(info_frame, text="Nenhum arquivo carregado")
lbl_arquivo.pack(pady=5)

lbl_amostras = ctk.CTkLabel(info_frame, text="Amostras: --")
lbl_amostras.pack(pady=5)

lbl_duracao  = ctk.CTkLabel(info_frame, text="Duração: --")
lbl_duracao.pack(pady=5)

lbl_pitch    = ctk.CTkLabel(info_frame, text="Pitch: --")
lbl_pitch.pack(pady=5)

lbl_roll     = ctk.CTkLabel(info_frame, text="Roll: --")
lbl_roll.pack(pady=5)

ctk.CTkLabel(info_frame, text="Variável").pack(pady=(20, 5))

variavel = ctk.StringVar(value="pitch")
combo = ctk.CTkOptionMenu(
    info_frame,
    variable=variavel,
    values=COLUNAS,
    command=atualizar_grafico
)
combo.pack(pady=5, padx=10)

# ---------- área do gráfico ----------

grafico_frame = ctk.CTkFrame(main_frame)
grafico_frame.pack(side="right", fill="both", expand=True, pady=10)

# ==========================
# Layout – botões inferiores
# ==========================

bottom_frame = ctk.CTkFrame(app)
bottom_frame.pack(fill="x", padx=20, pady=10)

ctk.CTkButton(bottom_frame, text="📂 Abrir CSV",    command=abrir_csv).pack(side="left", padx=10, pady=10)
ctk.CTkButton(bottom_frame, text="▶ Replay 3D",     command=lambda: iniciar_replay(df_global)).pack(side="left", padx=10)
ctk.CTkButton(bottom_frame, text="💾 Exportar PNG", command=exportar_png).pack(side="left", padx=10)

# ==========================
# Iniciar aplicação
# ==========================

app.mainloop()
