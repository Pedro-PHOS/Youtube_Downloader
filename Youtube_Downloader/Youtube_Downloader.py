import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from yt_dlp import YoutubeDL
import os

# ============================================================
# CAMINHO DO FFMPEG INTERNO (necessário para EXE)
# ============================================================

BASE_DIR = os.path.dirname(__file__)
FFMPEG_PATH = os.path.join(BASE_DIR, "ffmpeg", "ffmpeg.exe")  # <--- PASTA LOCAL

# ============================================================
# MODO ESCURO
# ============================================================

def aplicar_dark_mode(janela):
    janela.configure(bg="#1e1e1e")

    style = ttk.Style(janela)
    style.theme_use("clam")

    style.configure("TLabel", background="#1e1e1e", foreground="#ffffff")
    style.configure("TFrame", background="#1e1e1e")
    style.configure("TEntry", fieldbackground="#2b2b2b", foreground="#ffffff")
    style.configure("TButton",
                    background="#3a3a3a",
                    foreground="#ffffff",
                    padding=6)
    style.map("TButton",
              background=[("active", "#505050")])

    style.configure("TCombobox",
                    fieldbackground="#2b2b2b",
                    background="#2b2b2b",
                    foreground="#ffffff")
    style.map("TCombobox",
              fieldbackground=[("readonly", "#2b2b2b")],
              foreground=[("readonly", "#ffffff")])

# ============================================================
# DOWNLOAD (corrigido com ffmpeg interno)
# ============================================================

def baixar(url_entry, pasta_entry, cookie_entry, tipo_combo):
    url = url_entry.get().strip()
    pasta = pasta_entry.get().strip()
    cookie = cookie_entry.get().strip()
    tipo = tipo_combo.get()

    if not url:
        messagebox.showerror("Erro", "Informe a URL do vídeo.")
        return

    if not pasta or not os.path.isdir(pasta):
        messagebox.showerror("Erro", "Selecione uma pasta válida.")
        return

    # opcoes base
    opcoes = {
        "outtmpl": os.path.join(pasta, "%(title)s.%(ext)s"),
        "ffmpeg_location": FFMPEG_PATH     # <---- ESSENCIAL
    }

    if tipo == "Áudio (MP3)":
        opcoes.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }]
        })

    else:
        # Corrigindo áudio OPUS ➜ AAC
        opcoes.update({
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "postprocessor_args": {
                "ffmpeg": ["-c:a", "aac", "-b:a", "192k"]
            }
        })

    if cookie:
        if os.path.isfile(cookie):
            opcoes["cookiefile"] = cookie
        else:
            messagebox.showerror("Erro", "O arquivo de cookie não existe.")
            return

    try:
        with YoutubeDL(opcoes) as ydl:
            ydl.download([url])

        messagebox.showinfo("Sucesso", f"{tipo} baixado com sucesso!")

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro:\n{e}")

# ============================================================
# INTERFACE
# ============================================================

janela = tk.Tk()
janela.title("Downloader YouTube – yt-dlp")
janela.geometry("600x530")
janela.resizable(False, False)

aplicar_dark_mode(janela)

# URL
ttk.Label(janela, text="URL do vídeo:").pack(anchor="w", pady=5, padx=10)
entrada_url = ttk.Entry(janela, width=70)
entrada_url.pack(padx=10)

# Tipo
ttk.Label(janela, text="Tipo de download:").pack(anchor="w", pady=5, padx=10)
combo_tipo = ttk.Combobox(janela, values=["Áudio (MP3)", "Vídeo (MP4)"], state="readonly")
combo_tipo.current(0)
combo_tipo.pack(padx=10)

# Pasta
ttk.Label(janela, text="Local para salvar:").pack(anchor="w", pady=5, padx=10)
frame_pasta = ttk.Frame(janela)
frame_pasta.pack(padx=10)

entrada_pasta = ttk.Entry(frame_pasta, width=50)
entrada_pasta.pack(side="left")

def escolher_pasta():
    pasta = filedialog.askdirectory()
    if pasta:
        entrada_pasta.delete(0, tk.END)
        entrada_pasta.insert(0, pasta)

ttk.Button(frame_pasta, text="Procurar", command=escolher_pasta).pack(side="left", padx=5)

# Cookie
ttk.Label(janela, text="Cookie (opcional):").pack(anchor="w", pady=5, padx=10)
frame_cookie = ttk.Frame(janela)
frame_cookie.pack(padx=10)

entrada_cookie = ttk.Entry(frame_cookie, width=50)
entrada_cookie.pack(side="left")

def escolher_cookie():
    cookie = filedialog.askopenfilename(
        title="Selecione o arquivo cookies.txt",
        filetypes=[("Cookies TXT", "*.txt"), ("Todos os arquivos", "*.*")]
    )
    if cookie:
        entrada_cookie.delete(0, tk.END)
        entrada_cookie.insert(0, cookie)

ttk.Button(frame_cookie, text="Selecionar", command=escolher_cookie).pack(side="left", padx=5)

# Botão baixar
ttk.Button(
    janela,
    text="Baixar",
    command=lambda: baixar(entrada_url, entrada_pasta, entrada_cookie, combo_tipo)
).pack(pady=15)

# Texto explicativo
texto_cookie = (
    "✅ Como usar o cookie?\n\n"
    "1. Instale a extensão Get cookies.txt\n"
    "2. Acesse o YouTube logado\n"
    "3. Exporte o arquivo cookies.txt\n"
    "4. Selecione o arquivo no programa\n\n"
    "Permite baixar conteúdos privados, +18, playlists privadas e resoluções altas."
)

frame_texto = ttk.Frame(janela)
frame_texto.pack(padx=10, pady=5, fill="both", expand=True)

scroll = tk.Scrollbar(frame_texto)
scroll.pack(side="right", fill="y")

caixa_texto = tk.Text(
    frame_texto, height=10, width=70, wrap="word",
    yscrollcommand=scroll.set,
    bg="#2b2b2b", fg="#ffffff"
)
caixa_texto.insert("1.0", texto_cookie)
caixa_texto.config(state="disabled")
caixa_texto.pack(side="left", fill="both", expand=True)

scroll.config(command=caixa_texto.yview)

janela.mainloop()
