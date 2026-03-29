import customtkinter as ctk
import os, pygame, shutil, sys, time, threading
from tkinter import filedialog, messagebox
from monitor import iniciar_monitor
import optimizer as opt 

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- DEFINIÇÃO DE CORES ---
C_BG_OLED     = "#050505" 
C_CARD_DEEP   = "#0A0A0A" 
C_BORDER_DARK = "#1A1A1A" 
C_GOLD_CLEAN  = "#D4AF37" 
C_TEXT_LIGHT  = "#E0E0E0" 
C_DESC_GREY   = "#00FFC3" 
C_LOG_CYAN    = "#00FF91" 
C_INPUT_BG    = "#121212" 

class AikaEliteUI(ctk.CTk):
    def __init__(self, start_callback):
        super().__init__()
        
        self.title("AKBR OPTIMIZER PRO | @diegobfr07 | v1.0.0")
        
        # --- CÁLCULO PARA CENTRALIZAR A TELA ---
        largura_app = 700
        altura_app = 675
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        
        # Calcula o ponto X (centro) e Y (centro, mas puxando 40 pixels para o alto)
        pos_x = (largura_tela // 2) - (largura_app // 2)
        pos_y = (altura_tela // 2) - (altura_app // 2) - 40
        
        self.geometry(f"{largura_app}x{altura_app}+{pos_x}+{pos_y}")
        self.configure(fg_color=C_BG_OLED) 

        try:
            self.iconbitmap(resource_path("icone.ico"))
        except: pass
        
        pygame.mixer.init()
        self.som_novo_path = ""
        self.pasta_audio_aika = r"C:\CBMgames\AikaOnlineBrasil\Sound"
        self.arquivos_mods_usuario = [] 
        
        if os.path.exists(self.pasta_audio_aika):
            self.arquivos_originais = sorted(os.listdir(self.pasta_audio_aika))
        else:
            self.arquivos_originais = ["Pasta Sound não encontrada"]

        # --- CABEÇALHO ---
        self.frame_top = ctk.CTkFrame(self, fg_color="#000", border_color="#1a1a1a", border_width=1, height=55, corner_radius=0)
        self.frame_top.pack(fill="x")
        
        self.status_frame = ctk.CTkFrame(self.frame_top, fg_color="transparent")
        self.status_frame.place(relx=0.02, rely=0.5, anchor="w")

        self.ping_pill = ctk.CTkFrame(self.status_frame, fg_color="#0D0D0D", border_color=C_BORDER_DARK, border_width=1, corner_radius=20, height=32)
        self.ping_pill.pack(side="left", padx=(0, 5))
        self.ping_dot = ctk.CTkLabel(self.ping_pill, text="●", font=("Arial", 16), text_color="#2ecc71")
        self.ping_dot.pack(side="left", padx=(12, 5))
        self.lbl_ping_app = ctk.CTkLabel(self.ping_pill, text="PING: --ms", font=("Orbitron", 11, "bold"), text_color="white")
        self.lbl_ping_app.pack(side="left", padx=(0, 15))

        self.ram_pill = ctk.CTkFrame(self.status_frame, fg_color="#0D0D0D", border_color=C_BORDER_DARK, border_width=1, corner_radius=20, height=32)
        self.ram_pill.pack(side="left", padx=5)
        self.lbl_ram = ctk.CTkLabel(self.ram_pill, text="RAM: --%", font=("Orbitron", 11, "bold"), text_color="#00ffcc")
        self.lbl_ram.pack(padx=15, pady=2)

        self.disk_pill = ctk.CTkFrame(self.status_frame, fg_color="#0D0D0D", border_color=C_BORDER_DARK, border_width=1, corner_radius=20, height=32)
        self.disk_pill.pack(side="left", padx=5)
        self.lbl_disk = ctk.CTkLabel(self.disk_pill, text="DISCO: --%", font=("Orbitron", 11, "bold"), text_color="#ff9900")
        self.lbl_disk.pack(padx=15, pady=2)

        ctk.CTkButton(self.frame_top, text="🖥️ ATIVAR HUD", command=self.toggle_hud, width=110, height=30, corner_radius=15,
                    fg_color=C_GOLD_CLEAN, hover_color="#B59410", text_color="black", font=("Arial", 11, "bold")).pack(side="right", padx=15)
        
        # --- ABAS (ALTO CONTRASTE OLED) ---
        self.tabview = ctk.CTkTabview(
            self, 
            segmented_button_selected_color=C_GOLD_CLEAN,             
            segmented_button_selected_hover_color="#B59410",          
            segmented_button_fg_color="#121212",                      
            segmented_button_unselected_hover_color="#2A2A2A",        
            border_color=C_BORDER_DARK, 
            border_width=1, 
            fg_color="transparent"
        )
        self.tabview.pack(padx=12, pady=5, fill="both", expand=True)
        
        self.tabview._segmented_button.configure(font=("Orbitron", 12, "bold"), text_color="#FFFFFF")
        
        self.tab_perf = self.tabview.add("🚀 PERFORMANCE ENGINE")
        self.tab_audio = self.tabview.add("🎵 CONVERSOR DE ÁUDIO")
        self.tab_mods = self.tabview.add("🎮 AUTO MODS") 

        self.setup_perf_tab(start_callback)
        self.setup_audio_tab()
        self.setup_mods_tab()

        self.log_box = ctk.CTkTextbox(self, height=120, fg_color="#030303", text_color=C_LOG_CYAN, border_color=C_BORDER_DARK, border_width=1, font=("Consolas", 11))
        self.log_box.pack(pady=(0, 12), padx=12, fill="x")

        self.hud_window = None
        iniciar_monitor("45.134.141.84", 8822, self.atualizar_visual)

    def setup_perf_tab(self, start_callback):
        container = ctk.CTkFrame(self.tab_perf, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=5, pady=5)
        self.col1 = ctk.CTkFrame(container, fg_color="transparent"); self.col1.pack(side="left", fill="both", expand=True)
        self.col2 = ctk.CTkFrame(container, fg_color="transparent"); self.col2.pack(side="left", fill="both", expand=True)

        self.var_clean = ctk.BooleanVar(value=True); self.var_power = ctk.BooleanVar(value=True)
        self.var_prio = ctk.BooleanVar(value=True); self.var_net = ctk.BooleanVar(value=True)
        self.var_kb = ctk.BooleanVar(value=True); self.var_gamebar = ctk.BooleanVar(value=True)
        self.var_weaponeff = ctk.BooleanVar(value=True) 
        self.var_config = ctk.BooleanVar(value=False) 

        self.add_option(self.col1, "Limpeza de Buffer (RAM/Cache)", self.var_clean, "Otimiza endereços de memória e elimina resíduos de sistema.")
        self.add_option(self.col1, "Plano de Energia Ultra", self.var_power, "Força o clock máximo do processador ignorando restrições de economia.")
        self.add_option(self.col1, "Prioridade de CPU (IFEO)", self.var_prio, "Injeta prioridade alta no processo do Aika via Registro do Windows.")
        self.add_option(self.col1, "Correção Visual de Armas", self.var_weaponeff, "Remove o arquivo WeaponEff3.bin para reduzir poluição visual.") 
        
        self.add_option(self.col2, "Otimização de TCP/IP", self.var_net, "Desativa Autotuning e RSC para reduzir latência e estabilizar pacotes.")
        self.add_option(self.col2, "Taxa de Resposta do Teclado", self.var_kb, "Zera o delay de input no registro para execução instantânea de skills.")
        self.add_option(self.col2, "Bloqueio de Telemetria", self.var_gamebar, "Desativa funções secundárias do Windows que causam travamentos.")
        self.add_option(self.col2, "CFG Opcional (Elite)", self.var_config, "Resolução e Efeitos ajustados: Injeta preset de máxima performance.") 

        self.dns_choice = ctk.CTkSegmentedButton(self.tab_perf, values=["Cloudflare", "Google", "Padrão"], fg_color="#111", selected_color=C_GOLD_CLEAN, text_color=C_TEXT_LIGHT)
        self.dns_choice.set("Padrão"); self.dns_choice.pack(pady=5, padx=80, fill="x")
        
        frame_botoes_perf = ctk.CTkFrame(self.tab_perf, fg_color="transparent")
        frame_botoes_perf.pack(pady=(5, 10), padx=20, fill="x")
        
        btn_opt = ctk.CTkButton(frame_botoes_perf, text="EXECUTAR OTIMIZAÇÃO", command=start_callback, height=45, fg_color="#d32f2f", hover_color="#a32424", font=("Orbitron", 13, "bold"))
        btn_opt.pack(side="left", padx=5, expand=True, fill="x")
        
        btn_play = ctk.CTkButton(frame_botoes_perf, text="🎮 INICIAR AIKA LAUNCHER", command=self.chamar_iniciar_jogo, height=45, fg_color="#0066aa", hover_color="#005588", font=("Orbitron", 13, "bold"))
        btn_play.pack(side="left", padx=5, expand=True, fill="x")

    def chamar_iniciar_jogo(self):
        self.write_log(">>> Iniciando o Aika Launcher...")
        if opt.iniciar_jogo():
            self.write_log("✓ O jogo foi iniciado com sucesso! Bom combate.")
        else:
            self.write_log("❌ ERRO: Executável do Aika não encontrado na pasta padrão.")

    def add_option(self, parent, title, var, desc):
        frame = ctk.CTkFrame(parent, fg_color=C_CARD_DEEP, border_color=C_BORDER_DARK, border_width=1, corner_radius=10, height=75)
        frame.pack(fill="x", padx=6, pady=4)
        frame.pack_propagate(False)
        check = ctk.CTkCheckBox(frame, text=title, variable=var, font=("Arial", 12, "bold"), text_color=C_GOLD_CLEAN, fg_color=C_GOLD_CLEAN)
        check.pack(anchor="w", padx=10, pady=(6, 0))
        ctk.CTkLabel(frame, text=desc, font=("Arial", 10), text_color=C_DESC_GREY, wraplength=220, justify="left").pack(anchor="w", padx=35, pady=(2, 0))

    def setup_audio_tab(self):
        desc_audio = ("Sistema de Conversão Nativa: O aplicativo converte seus arquivos MP3 ou WAV para "
                      "o formato .bin do jogo.\nIsso garante 100% de compatibilidade sem corromper a leitura.")
        ctk.CTkLabel(self.tab_audio, text=desc_audio, font=("Arial", 11), text_color=C_DESC_GREY, justify="center").pack(pady=(10, 15))
        
        ctk.CTkLabel(self.tab_audio, text="1. Filtre e selecione o som original do jogo:", font=("Arial", 12, "bold"), text_color=C_GOLD_CLEAN).pack(pady=(5, 5))
        self.entry_busca = ctk.CTkEntry(self.tab_audio, placeholder_text="🔍 Digite para buscar...", width=380, fg_color=C_INPUT_BG, border_color=C_BORDER_DARK, text_color=C_TEXT_LIGHT)
        self.entry_busca.pack(pady=5)
        self.entry_busca.bind("<KeyRelease>", self.filtrar_lista)

        self.combo_aika = ctk.CTkComboBox(self.tab_audio, values=self.arquivos_originais, width=420, fg_color=C_INPUT_BG, border_color=C_GOLD_CLEAN, text_color=C_TEXT_LIGHT)
        self.combo_aika.pack(pady=10)

        ctk.CTkLabel(self.tab_audio, text="2. Selecione seu Som Novo (MP3/WAV):", text_color=C_GOLD_CLEAN, font=("Arial", 11, "bold")).pack(pady=(15, 5))
        self.entry_som = ctk.CTkEntry(self.tab_audio, width=380, fg_color=C_INPUT_BG, border_color=C_BORDER_DARK, placeholder_text="Nenhum arquivo selecionado...", text_color=C_TEXT_LIGHT)
        self.entry_som.pack(pady=2)
        
        frame_botoes = ctk.CTkFrame(self.tab_audio, fg_color="transparent")
        frame_botoes.pack(pady=15)
        ctk.CTkButton(frame_botoes, text="📁 ESCOLHER ARQUIVO", command=self.buscar_som, width=160, fg_color="#333", hover_color="#444", text_color=C_TEXT_LIGHT).pack(side="left", padx=5)
        self.btn_play = ctk.CTkButton(frame_botoes, text="▶ OUVIR PREVIEW", command=self.play_preview, state="disabled", fg_color="transparent", border_width=1, border_color=C_GOLD_CLEAN, width=130, text_color=C_GOLD_CLEAN)
        self.btn_play.pack(side="left", padx=5)
        
        frame_aplicar = ctk.CTkFrame(self.tab_audio, fg_color="transparent")
        frame_aplicar.pack(pady=10, fill="x", padx=60)
        ctk.CTkButton(frame_aplicar, text="✅ CONVERTER E APLICAR", command=self.aplicar_mod, height=45, fg_color="#0066aa", hover_color="#005588", width=180, font=("Arial", 11, "bold")).pack(side="left", padx=10, expand=True)
        ctk.CTkButton(frame_aplicar, text="🔇 MUTAR ÁUDIO", command=self.mutar_audio, height=45, fg_color="#d32f2f", hover_color="#a82525", width=180, font=("Arial", 11, "bold")).pack(side="left", padx=10, expand=True)

    def setup_mods_tab(self):
        desc_mods = ("Injeção Inteligente de Recursos: O algoritmo varrerá todos os diretórios do Aika e,\nao encontrar arquivos com o exato nome e extensão dos seus Mods, fará a substituição automática.")
        ctk.CTkLabel(self.tab_mods, text=desc_mods, font=("Arial", 11), text_color=C_DESC_GREY, justify="center").pack(pady=(20, 15))
        
        ctk.CTkLabel(self.tab_mods, text="1. Selecione os arquivos modificados (Sons, Cursores, Skills):", font=("Arial", 11, "bold"), text_color=C_GOLD_CLEAN).pack(pady=(15, 5))
        
        self.lbl_arquivos_mods = ctk.CTkLabel(self.tab_mods, text="Nenhum arquivo selecionado...", text_color=C_DESC_GREY, fg_color=C_INPUT_BG, width=420, height=35, corner_radius=5)
        self.lbl_arquivos_mods.pack(pady=10)
        
        ctk.CTkButton(self.tab_mods, text="📁 ESCOLHER ARQUIVOS", command=self.selecionar_arquivos_mods, width=220, height=35, fg_color="#333", hover_color="#444", text_color=C_TEXT_LIGHT).pack(pady=5)
        
        ctk.CTkLabel(self.tab_mods, text="2. Substituir arquivos originais no cliente do jogo:", font=("Arial", 11, "bold"), text_color=C_GOLD_CLEAN).pack(pady=(30, 5))
        
        ctk.CTkButton(self.tab_mods, text="APLICAR MODIFICAÇÕES", command=self.iniciar_injecao_mods, height=55, fg_color="#8c720d", hover_color="#B59410", font=("Orbitron", 14, "bold"), text_color="black").pack(pady=10, padx=80, fill="x")

    def selecionar_arquivos_mods(self):
        arquivos = filedialog.askopenfilenames(title="Selecione os arquivos de Mod")
        if arquivos:
            self.arquivos_mods_usuario = arquivos
            qtd = len(arquivos)
            texto = f"{qtd} arquivo(s) selecionado(s) prontos para injeção." if qtd > 1 else os.path.basename(arquivos[0])
            self.lbl_arquivos_mods.configure(text=texto)

    def iniciar_injecao_mods(self):
        if not self.arquivos_mods_usuario:
            messagebox.showwarning("Aviso", "Por favor, selecione os arquivos modificados primeiro!")
            return
        threading.Thread(target=self._processo_injetar_mods, daemon=True).start()

    def _processo_injetar_mods(self):
        self.write_log(">>> Escaneando a pasta do jogo e executando injeção de Mods...")
        arquivos_substituidos = opt.injetar_mods(self.arquivos_mods_usuario)
        
        if arquivos_substituidos > 0:
            self.write_log(f"✓ SUCESSO! {arquivos_substituidos} arquivos foram substituídos no jogo.")
        elif arquivos_substituidos == 0:
            self.write_log("⚠️ AVISO: Nenhum arquivo correspondente foi encontrado na pasta do jogo.")
        else:
            self.write_log("❌ ERRO: Falha ao injetar os arquivos. Verifique as permissões.")

    def filtrar_lista(self, event):
        termo = self.entry_busca.get().lower()
        filtrados = [f for f in self.arquivos_originais if termo in f.lower()]
        if not filtrados: filtrados = ["Nenhum encontrado"]
        self.combo_aika.configure(values=filtrados)
        self.combo_aika.set(filtrados[0])

    def buscar_som(self):
        arquivo = filedialog.askopenfilename(filetypes=[("Arquivos de Áudio", "*.mp3 *.wav")])
        if arquivo:
            self.som_novo_path = arquivo
            self.entry_som.delete(0, "end")
            self.entry_som.insert(0, os.path.basename(arquivo))
            self.btn_play.configure(state="normal", fg_color="#1a1a1a")

    def play_preview(self):
        if self.som_novo_path:
            try:
                pygame.mixer.music.load(self.som_novo_path)
                pygame.mixer.music.play()
            except Exception as e: messagebox.showerror("Erro", f"Erro: {e}")

    def aplicar_mod(self):
        arquivo_alvo = self.combo_aika.get()
        if not self.som_novo_path:
            messagebox.showwarning("Aviso", "Escolha um som novo primeiro!")
            return
        if not arquivo_alvo or arquivo_alvo == "Nenhum encontrado": return
        
        caminho_destino = os.path.join(self.pasta_audio_aika, arquivo_alvo)
        try: pygame.mixer.music.unload() 
        except: pass
        
        try:
            shutil.copy(self.som_novo_path, caminho_destino)
            self.write_log(f"O áudio '{arquivo_alvo}' foi formatado e substituído.")
            messagebox.showinfo("Sucesso", "Conversão e aplicação realizadas com sucesso!")
        except Exception as e:
            self.write_log(f"ERRO: {e}")

    def mutar_audio(self):
        arquivo_alvo = self.combo_aika.get()
        caminho_destino = os.path.join(self.pasta_audio_aika, arquivo_alvo)
        try: pygame.mixer.music.unload() 
        except: pass

        try:
            if os.path.exists(caminho_destino): os.remove(caminho_destino)
            with open(caminho_destino, 'w') as f: pass
            self.write_log(f"O arquivo de áudio '{arquivo_alvo}' foi silenciado nativamente.")
            messagebox.showinfo("Sucesso", "Áudio silenciado com sucesso!")
        except Exception as e:
            self.write_log(f"ERRO: {e}")

    def write_log(self, msg):
        self.after(0, lambda: self._write_log_safe(msg))

    def _write_log_safe(self, msg):
        self.log_box.insert("end", f">>> {msg}\n"); self.log_box.see("end")

    def toggle_hud(self):
        if self.hud_window is None or not self.hud_window.winfo_exists():
            self.hud_window = ctk.CTkToplevel(self)
            self.hud_window.geometry("100x40") 
            self.hud_window.overrideredirect(True) 
            self.hud_window.attributes("-topmost", True) 
            
            cor_transparente = "#000001" 
            self.hud_window.attributes("-transparentcolor", cor_transparente)
            self.hud_window.attributes("-alpha", 0.85) 
            self.hud_window.configure(fg_color=cor_transparente)
            
            self.hud_frame = ctk.CTkFrame(self.hud_window, fg_color="#0A0A0A", corner_radius=15, border_color=C_GOLD_CLEAN, border_width=1)
            self.hud_frame.pack(fill="both", expand=True, padx=2, pady=2) 
            
            self.lbl_hud = ctk.CTkLabel(self.hud_frame, text="ᯤ --ms", font=("Orbitron", 18, "bold"), text_color="#00ffcc")
            self.lbl_hud.pack(expand=True)
            
            self.lbl_hud.bind("<Button-1>", self.start_drag)
            self.lbl_hud.bind("<B1-Motion>", self.do_drag)
            self.hud_frame.bind("<Button-1>", self.start_drag)
            self.hud_frame.bind("<B1-Motion>", self.do_drag)
            
            self.write_log("ℹ️ HUD Dinâmico de Telemetria ATIVADO.")
        else: 
            self.hud_window.destroy()
            self.hud_window = None
            self.write_log("ℹ️ HUD Dinâmico DESATIVADO.")

    def start_drag(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def do_drag(self, event):
        x = self.hud_window.winfo_x() - self._drag_start_x + event.x
        y = self.hud_window.winfo_y() - self._drag_start_y + event.y
        self.hud_window.geometry(f"+{x}+{y}")

    def atualizar_visual(self, v, c, ram, disco):
        msg = f"ᯤ {v}ms" if v else "OFFLINE"
        self.after(0, lambda: self._atualizar_visual_safe(msg, c, ram, disco))

    def _atualizar_visual_safe(self, msg, c, ram, disco):
        self.lbl_ping_app.configure(text=msg)
        self.ping_dot.configure(text_color=c)
        self.lbl_ram.configure(text=f"RAM: {int(ram)}%")
        self.lbl_disk.configure(text=f"DISCO: {int(disco)}%")
        
        if self.hud_window and self.hud_window.winfo_exists() and hasattr(self, 'lbl_hud'): 
            self.lbl_hud.configure(text=msg, text_color=c)