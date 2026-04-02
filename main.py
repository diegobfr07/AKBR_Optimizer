import sys
import os
import ctypes
import threading
import string
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel,
                               QTextEdit, QWidget, QVBoxLayout, QHBoxLayout,
                               QGridLayout, QFrame, QGraphicsDropShadowEffect,
                               QStackedWidget, QButtonGroup, QFileDialog, QMessageBox)
# Adicionado QIcon aqui na linha abaixo!
from PySide6.QtGui import QCursor, QColor, QPainter, QPainterPath, QPen, QPixmap, QIcon
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup, Signal, QObject, QUrl, QThread
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

import optimizer as opt
import monitor

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

# BÚSSOLA DE CAMINHOS DO PYINSTALLER
def resolver_caminho(caminho_relativo):
    """Retorna o caminho absoluto compatível com PyInstaller e VS Code"""
    try:
        # PyInstaller cria uma pasta temporária em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, caminho_relativo)

class TarefaWorker(QThread):
    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        try:
            self.func()
        except Exception:
            pass

class SinaisUI(QObject):
    log_signal = Signal(str)
    monitor_signal = Signal(int, str, float, float)

class GraficoPing(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(90, 25)
        self.historico = [0] * 20

    def atualizar(self, ping):
        if ping is None or ping > 999:
            ping = 0
        self.historico.pop(0)
        self.historico.append(ping)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        path = QPainterPath()
        w, h = self.width(), self.height()
        passo_x = w / (len(self.historico) - 1)
        max_ping = max(100, max(self.historico))

        for i, p in enumerate(self.historico):
            x = i * passo_x
            y = h - ((p / max_ping) * h)
            y = max(2, min(h - 2, y))
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)

        pen = QPen(QColor(191, 0, 255))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawPath(path)

class OverlayPing(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.lbl = QLabel("Ping: -- ms")
        self.lbl.setStyleSheet("color: #00ff00; font-family: Consolas; font-size: 16px; font-weight: bold; background: rgba(10,10,15,200); padding: 8px 15px; border-radius: 8px; border: 2px solid #BF00FF;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.lbl)
        self.move(20, 20)
        self.dragPos = None

    def atualizar(self, p, c):
        self.lbl.setText(f"Ping: {p} ms")
        cor_atual = f"color: {c};"
        if cor_atual not in self.lbl.styleSheet():
            self.lbl.setStyleSheet(f"{cor_atual} font-family: Consolas; font-size: 16px; font-weight: bold; background: rgba(10,10,15,200); padding: 8px 15px; border-radius: 8px; border: 2px solid #BF00FF;")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragPos:
            delta = event.globalPosition().toPoint() - self.dragPos
            self.move(self.pos() + delta)
            self.dragPos = event.globalPosition().toPoint()
            event.accept()

class AikaCardGlow(QWidget):
    def __init__(self, parent, image_path, titulo):
        super().__init__(parent)
        self.setFixedSize(150, 190)
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(8)

        self.caixa_imagem = QFrame()
        self.caixa_imagem.setFixedSize(145, 145)
        self.caixa_imagem.setStyleSheet("background-color: transparent;")

        layout_caixa = QVBoxLayout(self.caixa_imagem)
        layout_caixa.setContentsMargins(0, 0, 0, 0)
        self.lbl_image = QLabel()
        self.lbl_image.setAlignment(Qt.AlignCenter)
        self.lbl_image.setStyleSheet("border-radius: 18px;")

        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.lbl_image.setPixmap(pixmap.scaled(145, 145, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        else:
            self.lbl_image.setText("ERRO")
            self.lbl_image.setStyleSheet("color: red; font-weight: bold;")

        layout_caixa.addWidget(self.lbl_image)

        self.lbl_titulo = QLabel(titulo)
        self.lbl_titulo.setStyleSheet("color: #E0E0E0; font-size: 14px; font-weight: bold;")
        self.lbl_titulo.setAlignment(Qt.AlignCenter)

        layout_principal.addWidget(self.caixa_imagem, 0, Qt.AlignCenter)
        layout_principal.addWidget(self.lbl_titulo, 0, Qt.AlignTop | Qt.AlignHCenter)

class AikaOptimizerPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aika Optimizer Pro V2.0")
        self.resize(1100, 750)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # SETANDO O ÍCONE DA JANELA E BARRA DE TAREFAS
        caminho_icone = resolver_caminho("icone.ico")
        self.setWindowIcon(QIcon(caminho_icone))

        self.sinais = SinaisUI()
        self.sinais.log_signal.connect(self.atualizar_log)
        self.sinais.monitor_signal.connect(self.atualizar_monitor)

        self.tarefa_lock = threading.Lock()
        self.executando_tarefa = False
        self.overlay_ativo = False
        self.overlay_window = OverlayPing()
        self.dragPos = None
        self.worker = None

        estilo_global = """
            QWidget#CentralWidget { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #050508, stop:1 #111118); border: 2px solid #2A004D; border-radius: 18px; }
            QLabel#Titulo { color: white; font-size: 22px; font-weight: bold; letter-spacing: 1px; }
            QFrame#AikaCard { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0A0A0E, stop:1 #12121A); border: 3px solid #3d0066; border-radius: 20px; }
            QTextEdit#AikaTerminal { background-color: rgba(5, 5, 8, 200); border: 2px solid #4D0080; border-radius: 12px; color: #BF00FF; font-family: Consolas; font-size: 13px; padding: 10px; }
            QScrollBar:vertical { width: 0px; }
            QPushButton.WinButton { background-color: transparent; color: #BF00FF; font-size: 16px; font-weight: bold; }
            QPushButton#BtnClose:hover { background-color: #FF2222; color: white; border-radius: 8px; }
            QFrame#Sidebar { background-color: rgba(10, 10, 15, 150); border-right: 2px solid #2A004D; border-radius: 15px; }
            QPushButton.MenuButton { background-color: transparent; color: #888899; text-align: left; padding: 12px 20px; font-size: 15px; font-weight: bold; border: none; border-left: 4px solid transparent; }
            QPushButton.MenuButton:checked { color: #BF00FF; border-left: 4px solid #BF00FF; background-color: rgba(191, 0, 255, 0.1); }
            QPushButton.ToolButton { background-color: rgba(77, 0, 128, 0.2); border: 1px solid #4D0080; border-radius: 8px; color: white; font-weight: bold; padding: 15px; font-size: 13px; }
            QPushButton.ToolButton:hover { background-color: rgba(191, 0, 255, 0.3); border: 1px solid #BF00FF; }
        """
        self.central_widget = QWidget()
        self.central_widget.setObjectName("CentralWidget")
        self.central_widget.setStyleSheet(estilo_global)
        self.setCentralWidget(self.central_widget)
        layout_principal = QVBoxLayout(self.central_widget)

        layout_titulo = QHBoxLayout()
        self.lbl_logo = QLabel()
        logo_pixmap = QPixmap(caminho_icone)
        self.lbl_logo.setPixmap(logo_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.lbl_titulo = QLabel("AIKA OPTIMIZER PRO V2.0")
        self.lbl_titulo.setObjectName("Titulo")

        self.lbl_ping = QLabel("Ping: -- ms")
        self.grafico_ping = GraficoPing()

        self.btn_overlay = QPushButton("🖥️ OSD Overlay")
        self.btn_overlay.setFixedSize(110, 25)
        self.btn_overlay.setStyleSheet("background-color: rgba(77, 0, 128, 0.5); color: white; border-radius: 5px; font-size: 11px; font-weight: bold; border: 1px solid #BF00FF;")
        self.btn_overlay.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_overlay.clicked.connect(self.toggle_overlay)

        self.lbl_ram = QLabel("RAM: --%")
        self.lbl_disco = QLabel("Disco: --%")

        estilo_monitor = "color: #00ff00; font-family: Consolas; font-size: 14px; background: rgba(0,0,0,100); padding: 5px; border-radius: 5px;"
        self.lbl_ping.setStyleSheet(estilo_monitor)
        self.lbl_ram.setStyleSheet(estilo_monitor.replace("#00ff00", "white"))
        self.lbl_disco.setStyleSheet(estilo_monitor.replace("#00ff00", "white"))

        btn_min = QPushButton("—")
        btn_min.setFixedSize(40, 30)
        btn_min.setProperty("class", "WinButton")
        btn_min.clicked.connect(self.showMinimized)

        btn_close = QPushButton("✕")
        btn_close.setObjectName("BtnClose")
        btn_close.setFixedSize(45, 35)
        btn_close.clicked.connect(self.fechar_app)

        layout_titulo.addWidget(self.lbl_logo)
        layout_titulo.addWidget(self.lbl_titulo)
        layout_titulo.addStretch()
        layout_titulo.addWidget(self.lbl_ping)
        layout_titulo.addWidget(self.grafico_ping)
        layout_titulo.addWidget(self.btn_overlay)
        layout_titulo.addSpacing(15)
        layout_titulo.addWidget(self.lbl_ram)
        layout_titulo.addWidget(self.lbl_disco)
        layout_titulo.addSpacing(10)
        layout_titulo.addWidget(btn_min)
        layout_titulo.addWidget(btn_close)
        layout_principal.addLayout(layout_titulo)

        layout_corpo = QHBoxLayout()

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(200)
        layout_sidebar = QVBoxLayout(sidebar)
        self.grupo_menu = QButtonGroup(self)
        self.btn_aba_performance = self.criar_botao_menu("🚀 Performance", 0)
        self.btn_aba_ferramentas = self.criar_botao_menu("🛠️ Sistema", 1)
        self.btn_aba_automod     = self.criar_botao_menu("📦 AutoMod", 2)
        self.btn_aba_audio       = self.criar_botao_menu("🎵 Áudio", 3)
        self.btn_aba_restore     = self.criar_botao_menu("🛡️ Segurança", 4)
        layout_sidebar.addWidget(self.btn_aba_performance)
        layout_sidebar.addWidget(self.btn_aba_ferramentas)
        layout_sidebar.addWidget(self.btn_aba_automod)
        layout_sidebar.addWidget(self.btn_aba_audio)
        layout_sidebar.addWidget(self.btn_aba_restore)
        layout_sidebar.addStretch()
        layout_corpo.addWidget(sidebar)

        self.telas = QStackedWidget()

        # --- TELA 0: PERFORMANCE ---
        page_perf = QWidget()
        layout_perf = QVBoxLayout(page_perf)
        layout_perf.setContentsMargins(10, 20, 10, 10)

        def obter_imagem(nome_base):
            caminho_png = resolver_caminho(f"{nome_base}.png")
            caminho_jpg = resolver_caminho(f"{nome_base}.jpg")
            return caminho_png if os.path.exists(caminho_png) else caminho_jpg

        grid_cards = QGridLayout()
        grid_cards.addWidget(AikaCardGlow(self, obter_imagem("Limpeza"), "Limpeza\nProfunda"), 0, 0)
        grid_cards.addWidget(AikaCardGlow(self, obter_imagem("Desempenho"), "Modo\nDesempenho"), 0, 1)
        grid_cards.addWidget(AikaCardGlow(self, obter_imagem("Teclado"), "Reduzir\nInput Lag"), 0, 2)
        grid_cards.addWidget(AikaCardGlow(self, obter_imagem("Rede"), "Estabilidade\nde Rede"), 0, 3)
        layout_perf.addLayout(grid_cards)

        layout_perf.addStretch(1)

        desc_perf = QLabel("💡 <b>O que a Otimização faz?</b> Ela executa as melhorias simultaneamente:<br>"
                           "• <b>Limpeza:</b> Apaga arquivos inúteis temporários do Windows para liberar espaço.<br>"
                           "• <b>Desempenho:</b> Prioriza o processo do jogo na CPU e define o Perfil de Energia para Máximo.<br>"
                           "• <b>Teclado:</b> Tira o atraso das teclas, ajudando você a soltar combos de skills mais rapidamente.<br>"
                           "• <b>Rede:</b> Remove os limites do Windows (Network Throttling) focando na estabilidade.")
        desc_perf.setWordWrap(True)
        desc_perf.setStyleSheet("color: #A0A0B0; font-size: 13px; background-color: rgba(255,255,255,10); padding: 12px; border-radius: 8px;")
        desc_perf.setAlignment(Qt.AlignLeft)
        layout_perf.addWidget(desc_perf)
        layout_perf.addSpacing(15)

        self.btn_boost = QPushButton("⚡ INICIAR OTIMIZAÇÃO")
        self.btn_boost.setMinimumHeight(80)
        self.btn_boost.setMinimumWidth(450)
        self.btn_boost.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_boost.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #BF00FF, stop:1 #660099); color: white; font-weight: bold; font-size: 20px; border-radius: 15px; border: 2px solid #BF00FF;")
        self.btn_glow = QGraphicsDropShadowEffect(self)
        self.btn_glow.setBlurRadius(35)
        self.btn_glow.setColor(QColor(191, 0, 255, 180))
        self.btn_glow.setOffset(0, 0)
        self.btn_boost.setGraphicsEffect(self.btn_glow)
        self.setup_botao_pulsar()

        self.btn_boost.clicked.connect(self.iniciar_boost_seguro)

        layout_perf.addWidget(self.btn_boost, 0, Qt.AlignCenter)
        layout_perf.addStretch(1)
        self.telas.addWidget(page_perf)

        # --- TELA 1: SISTEMA ---
        page_sys = QWidget()
        layout_sys = QVBoxLayout(page_sys)
        layout_sys.setSpacing(25)
        lbl_sys_t = QLabel("🛠️ Configurações Avançadas do Sistema")
        lbl_sys_t.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout_sys.addWidget(lbl_sys_t)
        lbl_dns = QLabel("Seleção de Servidor DNS:")
        lbl_dns.setStyleSheet("color: #BF00FF; font-weight: bold;")
        layout_sys.addWidget(lbl_dns)
        grid_dns = QGridLayout()
        grid_dns.addWidget(self.criar_botao_ferramenta("Google DNS (8.8.8.8)", lambda: self.acao_dns("Google")), 0, 0)
        grid_dns.addWidget(self.criar_botao_ferramenta("Cloudflare DNS (1.1.1.1)", lambda: self.acao_dns("Cloudflare")), 0, 1)
        grid_dns.addWidget(self.criar_botao_ferramenta("Restaurar Padrão", lambda: self.acao_dns("Padrao")), 0, 2)
        layout_sys.addLayout(grid_dns)

        lbl_m = QLabel("Otimizações Aika Online:")
        lbl_m.setStyleSheet("color: #BF00FF; font-weight: bold;")
        layout_sys.addWidget(lbl_m)
        grid_m = QGridLayout()
        grid_m.setVerticalSpacing(15)
        lay_cpu = self.criar_botao_com_desc("🔥 Prioridade Máxima CPU", self.acao_prioridade, "Força o Windows a dedicar o máximo de poder do processador ao Aika.")
        lay_gb = self.criar_botao_com_desc("🚫 Desativar Game Bar", self.acao_gamebar, "Desliga os recursos pesados do Xbox que rodam no fundo do Windows.")
        lay_wp = self.criar_botao_com_desc("🗑️ Remover WeaponEff3", self.acao_weapon, "Apaga os efeitos visuais pesados das armas. Ideal para tirar o lag no PvP.")
        lay_tcp = self.criar_botao_com_desc("⚡ Otimizar Ping (TCP NoDelay)", self.acao_tcp_nodelay, "Envia as informações instantaneamente ao servidor, derrubando o delay.")
        grid_m.addLayout(lay_cpu, 0, 0)
        grid_m.addLayout(lay_gb, 0, 1)
        grid_m.addLayout(lay_wp, 1, 0)
        grid_m.addLayout(lay_tcp, 1, 1)
        layout_sys.addLayout(grid_m)
        layout_sys.addStretch()
        self.telas.addWidget(page_sys)

        # --- TELA 2: AUTOMOD ---
        page_automod = QWidget()
        layout_automod = QVBoxLayout(page_automod)
        layout_automod.setSpacing(15)
        lbl_automod_t = QLabel("📦 AutoMod - Injetor de Modificações (Texturas/Effects)")
        lbl_automod_t.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin-bottom: 5px;")
        layout_automod.addWidget(lbl_automod_t)

        desc_automod = QLabel("💡 <b>Como funciona:</b> Selecione TODOS os arquivos modificados de uma única vez. O sistema vasculha o jogo, audita o Hash SHA256, faz o backup dos originais e faz a substituição de forma automática.")
        desc_automod.setWordWrap(True)
        desc_automod.setStyleSheet("color: #A0A0B0; font-size: 13px; background-color: rgba(255,255,255,10); padding: 12px; border-radius: 8px;")
        layout_automod.addWidget(desc_automod)

        lay_status_mods = QHBoxLayout()
        self.lbl_mods_selecionados = QLabel("Nenhum mod carregado para injeção.")
        self.lbl_mods_selecionados.setStyleSheet("color: #888; font-size: 13px; font-family: Consolas; padding: 5px;")

        self.btn_limpar_mods = QPushButton("🗑️ Limpar Seleção")
        self.btn_limpar_mods.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_limpar_mods.setStyleSheet("background-color: rgba(255, 34, 34, 0.8); color: white; font-weight: bold; border-radius: 5px; padding: 5px 15px; border: 1px solid #FF2222;")
        self.btn_limpar_mods.hide()
        self.btn_limpar_mods.clicked.connect(self.limpar_selecao_mods)

        lay_status_mods.addWidget(self.lbl_mods_selecionados)
        lay_status_mods.addWidget(self.btn_limpar_mods)
        layout_automod.addLayout(lay_status_mods)

        self.terminal_automod = QTextEdit()
        self.terminal_automod.setReadOnly(True)
        self.terminal_automod.setPlaceholderText("Lista de arquivos selecionados aparecerá aqui...")
        self.terminal_automod.setStyleSheet("""
            background-color: rgba(0, 0, 0, 80); 
            border: 1px solid #3d0066; 
            border-radius: 8px; 
            color: #AAA; 
            font-family: Consolas; 
            font-size: 11px;
        """)
        self.terminal_automod.setFixedHeight(180)
        layout_automod.addWidget(self.terminal_automod)

        layout_automod.addWidget(self.criar_botao_ferramenta("📂 Selecionar Arquivos de Mod", self.selecionar_arquivos_mod))

        btn_inj_mod = QPushButton("⚙️ INJETAR MODS NO AIKA")
        btn_inj_mod.setStyleSheet("background: #BF00FF; color: white; padding: 20px; border-radius: 12px; font-weight: bold; font-size: 16px;")
        btn_inj_mod.setCursor(QCursor(Qt.PointingHandCursor))
        btn_inj_mod.clicked.connect(self.acao_injetar_mods)

        layout_automod.addStretch()
        layout_automod.addWidget(btn_inj_mod)
        self.telas.addWidget(page_automod)

        # --- TELA 3: ÁUDIO ---
        page_audio = QWidget()
        layout_audio = QVBoxLayout(page_audio)
        layout_audio.setSpacing(15)
        lbl_audio_t = QLabel("🎵 Injetor de Áudio Customizado")
        lbl_audio_t.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin-bottom: 5px;")
        layout_audio.addWidget(lbl_audio_t)
        desc_audio = QLabel("💡 <b>Como funciona:</b> Escolha qualquer música (MP3 ou WAV) e o sistema injeta e aplica a música no jogo. O arquivo original fica salvo e auditado no nosso Snapshot de Backup.")
        desc_audio.setWordWrap(True)
        desc_audio.setStyleSheet("color: #A0A0B0; font-size: 13px; background-color: rgba(255,255,255,10); padding: 12px; border-radius: 8px;")
        layout_audio.addWidget(desc_audio)

        self.estilo_default_lbl = "color: #888; font-size: 13px; margin-top: 5px; padding: 2px;"

        self.lbl_alvo = QLabel("1. Arquivo Original do Jogo: Nenhum selecionado")
        self.lbl_alvo.setStyleSheet(self.estilo_default_lbl)
        btn_alvo = self.criar_botao_ferramenta("📂 Buscar .bin na Pasta Sound do Jogo", self.selecionar_audio_jogo)

        self.lbl_novo_audio = QLabel("2. Sua Nova Música/Efeito: Nenhum selecionado")
        self.lbl_novo_audio.setStyleSheet(self.estilo_default_lbl.replace("margin-top: 5px;", ""))

        lay_aud_btns = QHBoxLayout()
        btn_novo = self.criar_botao_ferramenta("🎵 Escolher Música (MP3/WAV)", self.selecionar_arquivo_audio)
        self.btn_play = self.criar_botao_ferramenta("▶️ Ouvir Prévia", self.tocar_previa)
        lay_aud_btns.addWidget(btn_novo)
        lay_aud_btns.addWidget(self.btn_play)

        self.btn_conv_aud = QPushButton("🔄 ALTERAR ÁUDIO (APLICAR)")
        self.btn_conv_aud.setStyleSheet("background: #BF00FF; color: white; padding: 20px; border-radius: 12px; font-weight: bold; font-size: 16px;")
        self.btn_conv_aud.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_conv_aud.clicked.connect(self.acao_substituir_audio)

        btn_restaurar_1 = QPushButton("↩️ RESTAURAR APENAS ESTE ÁUDIO")
        btn_restaurar_1.setStyleSheet("background: rgba(255, 34, 34, 0.7); border: 1px solid #FF2222; color: white; padding: 15px; border-radius: 12px; font-weight: bold; font-size: 14px;")
        btn_restaurar_1.setCursor(QCursor(Qt.PointingHandCursor))
        btn_restaurar_1.clicked.connect(self.acao_restaurar_audio)

        layout_audio.addWidget(self.lbl_alvo)
        layout_audio.addWidget(btn_alvo)
        layout_audio.addWidget(self.lbl_novo_audio)
        layout_audio.addLayout(lay_aud_btns)
        layout_audio.addStretch()
        layout_audio.addWidget(self.btn_conv_aud)
        layout_audio.addWidget(btn_restaurar_1)
        self.telas.addWidget(page_audio)

        # --- TELA 4: RESTAURAÇÃO E SEGURANÇA ---
        page_restore = QWidget()
        layout_restore = QVBoxLayout(page_restore)
        layout_restore.setSpacing(25)

        lbl_res_t = QLabel("🛡️ Central de Restauração e Segurança do Sistema")
        lbl_res_t.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin-bottom: 5px;")
        layout_restore.addWidget(lbl_res_t)

        desc_res = QLabel("💡 <b>Auditoria Ativa (V2.0 Snapshot):</b> O Aika Optimizer salva o estado EXATO do seu Windows em um arquivo JSON antes de aplicar as otimizações. Além disso, criamos a pasta de Backups do jogo.<br><br>"
                          "Aqui você pode desfazer qualquer modificação e reverter o seu computador ou os arquivos do jogo para o estado original.")
        desc_res.setWordWrap(True)
        desc_res.setStyleSheet("color: #A0A0B0; font-size: 14px; background-color: rgba(255,255,255,10); padding: 15px; border-radius: 8px; line-height: 1.5;")
        layout_restore.addWidget(desc_res)

        btn_res_all = QPushButton("🎮 DESFAZER MODIFICAÇÕES NO JOGO (Arquivos .bin / Texturas)")
        btn_res_all.setStyleSheet("background: #FF1111; color: white; padding: 25px; border-radius: 15px; font-weight: bold; font-size: 16px; border: 2px solid #880000;")
        btn_res_all.setCursor(QCursor(Qt.PointingHandCursor))
        btn_res_all.clicked.connect(self.acao_restaurar_tudo)

        btn_res_sys = QPushButton("🖥️ DESFAZER OTIMIZAÇÕES DE SISTEMA (Rollback JSON e Registro)")
        btn_res_sys.setStyleSheet("background: #FF8800; color: white; padding: 25px; border-radius: 15px; font-weight: bold; font-size: 16px; border: 2px solid #CC6600;")
        btn_res_sys.setCursor(QCursor(Qt.PointingHandCursor))
        btn_res_sys.clicked.connect(self.acao_restaurar_sistema)

        layout_restore.addStretch()
        layout_restore.addWidget(btn_res_sys)
        layout_restore.addWidget(btn_res_all)
        self.telas.addWidget(page_restore)

        # LAYOUT FINAL DIREITA E LOGS INICIAIS
        layout_direita = QVBoxLayout()
        layout_direita.addWidget(self.telas)
        self.log_box = QTextEdit()
        self.log_box.setObjectName("AikaTerminal")
        self.log_box.setReadOnly(True)
        self.log_box.setFixedHeight(160)

        self.log_box.setText(">> 🟢 SISTEMA AIKA 2.0 INICIALIZADO (MODO BLINDADO)...\n>> 🟢 ARQUIVO DE AUDITORIA .LOG ATIVADO.")
        layout_direita.addWidget(self.log_box)
        layout_corpo.addLayout(layout_direita)
        layout_principal.addLayout(layout_corpo)

        # SISTEMAS AUXILIARES
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.5)
        self.btn_aba_performance.setChecked(True)
        monitor.iniciar_monitor("45.134.141.84", 8822, self.receber_dados_monitor)

    # ========================================================
    # FUNÇÕES DE UI E CONTROLE
    # ========================================================
    def criar_botao_com_desc(self, t, a, d):
        lay = QVBoxLayout()
        lay.setSpacing(5)
        btn = self.criar_botao_ferramenta(t, a)
        lay.addWidget(btn)
        lbl = QLabel(d)
        lbl.setWordWrap(True)
        lbl.setStyleSheet("color: #A0A0B0; font-size: 11px; padding: 0px 5px;")
        lbl.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        lay.addWidget(lbl)
        lay.addStretch()
        return lay

    def setup_botao_pulsar(self):
        a1 = QPropertyAnimation(self.btn_glow, b"color")
        a1.setDuration(800)
        a1.setStartValue(QColor(191,0,255,50))
        a1.setEndValue(QColor(191,0,255,255))
        a2 = QPropertyAnimation(self.btn_glow, b"color")
        a2.setDuration(800)
        a2.setStartValue(QColor(191,0,255,255))
        a2.setEndValue(QColor(191,0,255,50))
        self.btn_anim = QSequentialAnimationGroup()
        self.btn_anim.addAnimation(a1)
        self.btn_anim.addAnimation(a2)
        self.btn_anim.setLoopCount(-1)
        self.btn_anim.start()

    def criar_botao_menu(self, t, i):
        btn = QPushButton(t)
        btn.setProperty("class", "MenuButton")
        btn.setCheckable(True)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.grupo_menu.addButton(btn, i)
        btn.clicked.connect(lambda: self.telas.setCurrentIndex(i))
        return btn

    def criar_botao_ferramenta(self, t, a):
        btn = QPushButton(t)
        btn.setProperty("class", "ToolButton")
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.clicked.connect(a)
        return btn

    def atualizar_log(self, m):
        self.log_box.append(f">> {m}")
        self.log_box.verticalScrollBar().setValue(self.log_box.verticalScrollBar().maximum())

    def atualizar_monitor(self, p, c, r, d):
        self.lbl_ping.setText(f"Ping: {p}ms")
        self.lbl_ping.setStyleSheet(f"color: {c}; font-family: Consolas; font-size: 14px; background: rgba(0,0,0,100); padding: 5px; border-radius: 5px;")
        self.lbl_ram.setText(f"RAM: {r}%")
        self.lbl_disco.setText(f"Disco: {d}%")
        self.grafico_ping.atualizar(p)
        if self.overlay_ativo:
            self.overlay_window.atualizar(p, c)

    def toggle_overlay(self):
        self.overlay_ativo = not self.overlay_ativo
        if self.overlay_ativo:
            self.overlay_window.show()
            self.btn_overlay.setStyleSheet("background-color: #BF00FF; color: white; border-radius: 5px; font-size: 11px; font-weight: bold; border: 1px solid white;")
            self.sinais.log_signal.emit("🟢 OSD Overlay In-Game ATIVADO.")
        else:
            self.overlay_window.hide()
            self.btn_overlay.setStyleSheet("background-color: rgba(77, 0, 128, 0.5); color: white; border-radius: 5px; font-size: 11px; font-weight: bold; border: 1px solid #BF00FF;")
            self.sinais.log_signal.emit("🟡 OSD Overlay In-Game DESATIVADO.")

    def receber_dados_monitor(self, p, c, r, d):
        self.sinais.monitor_signal.emit(p if p else 999, c, r, d)

    def limpar_execucao(self):
        with self.tarefa_lock:
            self.executando_tarefa = False
        if self.worker:
            self.worker.deleteLater()
            self.worker = None

    def executar_em_background(self, f):
        with self.tarefa_lock:
            if self.executando_tarefa:
                self.sinais.log_signal.emit("🟡 Uma tarefa já está em andamento. Aguarde...")
                return
            self.executando_tarefa = True

        self.worker = TarefaWorker(f)
        self.worker.finished.connect(self.limpar_execucao)
        self.worker.start()

    # ========================================================
    # AÇÕES DO SISTEMA E LOGS COM EMOJIS PADRONIZADOS
    # ========================================================
    def iniciar_boost_seguro(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Limpeza Opcional da Lixeira")
        msg_box.setText("Deseja esvaziar a Lixeira do Windows durante a otimização?\n\nArquivos excluídos na lixeira não poderão ser recuperados.")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText("Sim, Limpar")
        msg_box.button(QMessageBox.No).setText("Não, Manter")

        estilo_msgbox = """
            QMessageBox { background-color: #0A0A0E; border: 2px solid #2A004D; }
            QLabel { color: white; font-size: 14px; font-weight: bold; }
            QPushButton { background-color: rgba(77, 0, 128, 0.3); border: 1px solid #4D0080; border-radius: 8px; color: white; font-weight: bold; padding: 8px 15px; font-size: 13px; min-width: 80px; }
            QPushButton:hover { background-color: #BF00FF; border: 1px solid white; }
        """
        msg_box.setStyleSheet(estilo_msgbox)

        limpar_lix = (msg_box.exec() == QMessageBox.Yes)

        def tarefa_transacao():
            self.sinais.log_signal.emit("🟢 Iniciando modo BLINDADO (Motor Transacional)...")
            transacao = opt.TransacaoSistema()

            try:
                transacao.executar(opt.salvar_snapshot_sistema)
                self.sinais.log_signal.emit("🟢 Limpando arquivos temporários e cache...")
                transacao.executar(opt.limpar_profundo, limpar_lix)
                self.sinais.log_signal.emit("🟢 Aplicando otimizações de Desempenho e Rede...")
                transacao.executar(opt.modo_desempenho_maximo, rollback=opt.restaurar_snapshot_sistema)
                transacao.executar(opt.otimizar_multimidia_jogos)
                transacao.executar(opt.otimizar_resposta_teclado, rollback=opt.restaurar_registro_sistema)
                transacao.executar(opt.otimizar_rede_estabilidade)
                self.sinais.log_signal.emit("🟢 OTIMIZAÇÃO COMPLETA FINALIZADA COM SEGURANÇA MÁXIMA!")
                opt.iniciar_jogo()
            except Exception as e:
                self.sinais.log_signal.emit(f"🔴 ERRO CRÍTICO: {e}")
                self.sinais.log_signal.emit("🟡 O sistema foi revertido automaticamente para proteção (Rollback ativado).")

        self.executar_em_background(tarefa_transacao)

    def encontrar_pasta_sound(self):
        p = r"C:\CBMgames\AikaOnlineBrasil\Sound"
        if os.path.exists(p):
            return p
        for d in string.ascii_uppercase:
            c = os.path.join(f"{d}:\\", "CBMgames", "AikaOnlineBrasil", "Sound")
            if os.path.exists(c):
                return c
        return ""

    ESTILO_NEON_CARREGADO = "color: #00FF00; font-size: 13px; font-weight: bold; background-color: rgba(0, 50, 0, 150); border: 1px solid #00FF00; padding: 5px; border-radius: 5px;"

    def selecionar_audio_jogo(self):
        f, _ = QFileDialog.getOpenFileName(self, "Selecionar Original", self.encontrar_pasta_sound(), "Aika (*.bin *.wav);;Tudo (*.*)")
        if f:
            self.arquivo_alvo_jogo = f
            nome = f.split('/')[-1]
            self.lbl_alvo.setText(f"1. Original: {nome}")
            self.lbl_alvo.setStyleSheet(self.ESTILO_NEON_CARREGADO + " margin-top: 5px;")
            self.sinais.log_signal.emit(f"🟢 Original selecionado: {nome}")

    def selecionar_arquivo_audio(self):
        f, _ = QFileDialog.getOpenFileName(self, "Selecionar Novo", "", "Áudio (*.mp3 *.wav *.ogg *.m4a)")
        if f:
            self.arquivo_audio_selecionado = f
            nome = f.split('/')[-1]
            self.lbl_novo_audio.setText(f"2. Novo: {nome}")
            self.lbl_novo_audio.setStyleSheet(self.ESTILO_NEON_CARREGADO)
            self.sinais.log_signal.emit(f"🟢 Novo áudio carregado: {nome}")

    def tocar_previa(self):
        if not hasattr(self, 'arquivo_audio_selecionado'):
            return
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.stop()
            self.btn_play.setText("▶️ Ouvir Prévia")
        else:
            self.player.setSource(QUrl.fromLocalFile(self.arquivo_audio_selecionado))
            self.player.play()
            self.btn_play.setText("⏹️ Parar Prévia")

    def selecionar_arquivos_mod(self):
        f, _ = QFileDialog.getOpenFileNames(self, "Mods", "", "Tudo (*.*)")
        if f:
            self.arquivos_mod_selecionados = f
            self.lbl_mods_selecionados.setText(f"🔥 {len(f)} mods prontos para injeção.")
            self.lbl_mods_selecionados.setStyleSheet("color: #00FF00; font-size: 13px; font-weight: bold; background-color: rgba(0, 50, 0, 150); border: 1px solid #00FF00; padding: 5px; border-radius: 5px;")
            self.btn_limpar_mods.show()
            self.terminal_automod.clear()
            for caminho in f:
                nome_arquivo = caminho.split('/')[-1]
                self.terminal_automod.append(f"• {nome_arquivo}")
            self.sinais.log_signal.emit(f"🟢 {len(f)} mods selecionados e auditados na lista.")

    def limpar_selecao_mods(self):
        self.arquivos_mod_selecionados = []
        self.lbl_mods_selecionados.setText("Nenhum mod carregado para injeção.")
        self.lbl_mods_selecionados.setStyleSheet("color: #888; font-size: 13px; font-family: Consolas; padding: 5px;")
        self.terminal_automod.clear()
        self.btn_limpar_mods.hide()
        self.sinais.log_signal.emit("🟡 Seleção de mods limpa pelo usuário.")

    def acao_injetar_mods(self):
        mods = getattr(self, 'arquivos_mod_selecionados', None)
        if not mods:
            self.sinais.log_signal.emit("🔴 ERRO: Selecione os arquivos primeiro.")
            return
        def tarefa():
            r = opt.injetar_mods(mods)
            if r == -2:
                self.sinais.log_signal.emit("🔴 FECHE O JOGO PRIMEIRO! O Aika está bloqueando a modificação.")
            elif r >= 0:
                self.sinais.log_signal.emit(f"🟢 OK: {r} mods injetados com sucesso.")
            else:
                self.sinais.log_signal.emit("🔴 ERRO: Falha ao injetar mods.")
        self.executar_em_background(tarefa)

    def acao_substituir_audio(self):
        alvo = getattr(self, 'arquivo_alvo_jogo', None)
        novo = getattr(self, 'arquivo_audio_selecionado', None)
        if not alvo or not novo:
            self.sinais.log_signal.emit("🔴 ERRO: Selecione o original e o novo primeiro.")
            return
        def tarefa():
            s, m = opt.substituir_audio_customizado(novo, alvo)
            self.sinais.log_signal.emit("🟢 Sucesso! Áudio injetado e backup gerado." if s else f"🔴 ERRO: {m}")
        self.executar_em_background(tarefa)

    def acao_restaurar_audio(self):
        alvo = getattr(self, 'arquivo_alvo_jogo', None)
        if not alvo:
            self.sinais.log_signal.emit("🔴 ERRO: Selecione o arquivo .bin original primeiro para restaurar.")
            return
        def tarefa():
            s, m = opt.restaurar_audio_original(alvo)
            self.sinais.log_signal.emit(f"🟢 {m}" if s else f"🔴 ERRO: {m}")
        self.executar_em_background(tarefa)

    def acao_restaurar_tudo(self):
        def tarefa():
            self.sinais.log_signal.emit("🟡 INICIANDO ROLLBACK DOS ARQUIVOS DO JOGO...")
            s, m = opt.restaurar_tudo_jogo()
            self.sinais.log_signal.emit(f"🟢 {m}" if s else f"🔴 {m}")
        self.executar_em_background(tarefa)

    def acao_restaurar_sistema(self):
        def tarefa():
            self.sinais.log_signal.emit("🟡 INICIANDO ROLLBACK DO REGISTRO E JSON...")
            s, m = opt.restaurar_registro_sistema()
            self.sinais.log_signal.emit(f"🟢 {m}" if s else f"🔴 {m}")
        self.executar_em_background(tarefa)

    def acao_dns(self, p):
        def tarefa():
            if opt.alterar_dns(p):
                self.sinais.log_signal.emit(f"🟢 DNS {p} aplicado (ignorando VPNs).")
        self.executar_em_background(tarefa)

    def acao_prioridade(self):
        def tarefa():
            if opt.prioridade_total():
                self.sinais.log_signal.emit("🟢 Prioridade Máxima ativa no Registro e no Processo.")
        self.executar_em_background(tarefa)

    def acao_gamebar(self):
        def tarefa():
            if opt.desativar_game_bar():
                self.sinais.log_signal.emit("🟢 Xbox Game Bar desativada no Registro.")
        self.executar_em_background(tarefa)

    def acao_weapon(self):
        def tarefa():
            r = opt.remover_weaponeff3()
            if r == -2:
                self.sinais.log_signal.emit("🔴 FECHE O JOGO PRIMEIRO! O Aika está aberto.")
            else:
                self.sinais.log_signal.emit("🟢 Arquivo WeaponEff3 removido com backup!" if r else "🟡 Arquivo WeaponEff3 não encontrado ou já removido.")
        self.executar_em_background(tarefa)

    def acao_tcp_nodelay(self):
        def tarefa():
            self.sinais.log_signal.emit("🟢 Salvando registro anterior e Aplicando TCP NoDelay...")
            try:
                if opt.otimizar_tcp_nodelay():
                    self.sinais.log_signal.emit("🟢 Ping otimizado com sucesso!")
                else:
                    self.sinais.log_signal.emit("🔴 Erro ao otimizar TCP.")
            except Exception as e:
                self.sinais.log_signal.emit(f"🔴 Falha de permissão no TCP: {e}")
        self.executar_em_background(tarefa)

    def fechar_app(self):
        monitor.parar_monitor()
        if self.overlay_window:
            self.overlay_window.close()
        self.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragPos:
            delta = event.globalPosition().toPoint() - self.dragPos
            self.move(self.pos() + delta)
            self.dragPos = event.globalPosition().toPoint()
            event.accept()

if __name__ == "__main__":
    myappid = 'aika.optimizer.pro.2.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    app = QApplication(sys.argv)
    window = AikaOptimizerPro()
    window.show()
    sys.exit(app.exec())