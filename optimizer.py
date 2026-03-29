import os, shutil, winshell, subprocess, winreg, psutil, sys

def limpar_profundo():
    try:
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
        pastas = [os.environ.get('TEMP'), r'C:\Windows\Temp', r'C:\Windows\Prefetch']
        for pasta in pastas:
            if os.path.exists(pasta):
                for item in os.listdir(pasta):
                    try:
                        caminho = os.path.join(pasta, item)
                        if os.path.isfile(caminho): os.remove(caminho)
                        elif os.path.isdir(caminho): shutil.rmtree(caminho)
                    except: continue
        return True
    except: return False

def modo_desempenho_maximo():
    try:
        subprocess.run('powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c', shell=True)
        return True
    except: return False

def otimizar_resposta_teclado():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Keyboard", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "KeyboardDelay", 0, winreg.REG_SZ, "0")
        winreg.SetValueEx(key, "KeyboardSpeed", 0, winreg.REG_SZ, "31")
        winreg.CloseKey(key)
        return True
    except: return False

def otimizar_rede_estabilidade():
    try:
        subprocess.run('netsh int tcp set global autotuninglevel=disabled', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run('netsh int tcp set global ecncapability=disabled', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run('netsh int tcp set global rsc=disabled', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except: return False

def prioridade_total():
    try:
        executaveis = ["aika.exe", "aika_br.exe", "GameEngine.exe", "gameengine.exe"]
        for exe in executaveis:
            comando = f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\{exe}\\PerfOptions" /v CpuPriorityClass /t REG_DWORD /d 3 /f'
            subprocess.run(comando, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except: return False

def desativar_game_bar():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\GameDVR", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "AppCaptureEnabled", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        return True
    except: return False

def injetar_mods(lista_arquivos_mods, pasta_jogo=r"C:\CBMgames\AikaOnlineBrasil"):
    try:
        mapa_mods = {os.path.basename(caminho).lower(): caminho for caminho in lista_arquivos_mods}
        arquivos_substituidos = 0
        
        for root, dirs, files in os.walk(pasta_jogo):
            for file in files:
                if file.lower() in mapa_mods:
                    origem = mapa_mods[file.lower()]
                    destino = os.path.join(root, file)
                    
                    if os.path.exists(destino):
                        try: os.remove(destino)
                        except: pass
                        
                    shutil.copy2(origem, destino)
                    arquivos_substituidos += 1
                    
        return arquivos_substituidos
    except: 
        return -1

def iniciar_jogo(pasta_jogo=r"C:\CBMgames\AikaOnlineBrasil"):
    executaveis = ["AikaLauncher.exe", "aika_br.exe", "aika.exe", "GameEngine.exe"]
    for exe in executaveis:
        caminho = os.path.join(pasta_jogo, exe)
        if os.path.exists(caminho):
            os.startfile(caminho)
            return True
    return False

def remover_weaponeff3(pasta_jogo=r"C:\CBMgames\AikaOnlineBrasil"):
    try:
        removido = False
        for root, dirs, files in os.walk(pasta_jogo):
            for file in files:
                if file.lower() == "weaponeff3.bin":
                    caminho = os.path.join(root, file)
                    os.remove(caminho)
                    removido = True
        return removido
    except:
        return False

def aplicar_config_otimizada():
    try:
        config_texto = """[Version] 1109
[Resolution] 13
[Bright] 50
[FullScreen] 0
[BlurEffect] 0
[Reflection] 0
[MeshDetail] 0
[FieldDistance] 3
[ObjectDistance] 2
[Shadow] 0
[Music] 0
[3DSound] 1
[SoundVolume] 40
[Mouse] 0
[MouseMove] 1
[MouseAutoRun] 1
[ChatBalloon] 1
[ChatType] 0
[PopupMsg] 1
[Antialias] 0
[HideHelp] 1
[KeyType] 1
[Effect] 0
[Tile] 0
[Camera] 1
[Guild] 1
[Friend] 1
[Nation] 1
[Devir] 1
[Pran] 0
[PranName] 1
[QuestLog] 1
[MailNotice] 1
[MaxHuman] 6
[Blood] 1
[SPellBarMove] 0
[DamageShowToSys] 1
[MegaPhone] 1
[EtsWindow] 1
[PranQuest] 1
[ChangeBottomUI] 1
[PartyUI] 0
[InvenUI] 1
[Party/SquadInvite] 1
[FrinedAdd] 1
[TradeOnoff] 1
[Region/FriendOnlyInvite] 0
[Region/FriendOnlyTrade] 0"""

        pasta_jogo = r"C:\CBMgames\AikaOnlineBrasil"
        caminho_destino = os.path.join(pasta_jogo, "config.txt")
        
        if os.path.exists(caminho_destino):
            os.remove(caminho_destino)
            
        with open(caminho_destino, "w", encoding="utf-8") as f:
            f.write(config_texto)
            
        return True
    except: 
        return False
   
def alterar_dns(escolha):
    try:
        if escolha == "Google":
            cmd = 'powershell -Command "Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'} | Set-DnsClientServerAddress -ServerAddresses (\'8.8.8.8\',\'8.8.4.4\')"'
        elif escolha == "Cloudflare":
            cmd = 'powershell -Command "Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'} | Set-DnsClientServerAddress -ServerAddresses (\'1.1.1.1\',\'1.0.0.1\')"'
        else: 
            cmd = 'powershell -Command "Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'} | Set-DnsClientServerAddress -ResetServerAddresses"'
        
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except: 
        return False