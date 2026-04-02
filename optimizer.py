import os
import shutil
import subprocess
import winreg
import psutil
import stat
import winshell
import logging
import threading
import json
import hashlib
import re
import time

PASTA_JOGO_PADRAO = r"C:\CBMgames\AikaOnlineBrasil"
PASTA_BACKUP = r"C:\CBMgames\AikaOptimizer_Backups"
PASTA_BACKUP_REG = os.path.join(PASTA_BACKUP, "Registro_Sistema")
ARQUIVO_ESTADO = os.path.join(PASTA_BACKUP, "estado_sistema.json")

lock_otimizacao = threading.Lock()
snapshot_lock = threading.Lock()

os.makedirs(PASTA_BACKUP, exist_ok=True)
logging.basicConfig(filename=os.path.join(PASTA_BACKUP, 'aika_optimizer.log'),
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log(mensagem):
    logging.info(mensagem)

class TransacaoSistema:
    def __init__(self):
        self.passos_executados = []

    def executar(self, func, *args, rollback=None):
        try:
            resultado = func(*args)
            if rollback:
                self.passos_executados.append(rollback)
            return resultado
        except Exception as e:
            log(f"[TRANSAÇÃO FALHOU] Erro na função {func.__name__}: {e}")
            self.rollback_total()
            raise e

    def rollback_total(self):
        log("[ROLLBACK] Iniciando rollback completo da transação...")
        for acao in reversed(self.passos_executados):
            try:
                acao()
            except Exception as e:
                log(f"[ERRO ROLLBACK] Falha ao reverter passo: {e}")

def obter_plano_energia_atual():
    try:
        res = subprocess.check_output(['powercfg', '/getactivescheme'], text=True, stderr=subprocess.DEVNULL)
        match = re.search(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', res)
        return match.group(0) if match else None
    except Exception as e:
        log(f"Erro ao obter plano de energia: {e}")
        return None

def obter_dns_atual():
    try:
        cmd = "Get-NetAdapter | Where-Object {$_.Status -eq 'Up' -and $_.InterfaceDescription -notmatch 'Virtual|VMware|Hyper-V|TAP'} | Get-DnsClientServerAddress | Select-Object -ExpandProperty ServerAddresses"
        res = subprocess.check_output(['powershell', '-Command', cmd], text=True, stderr=subprocess.DEVNULL)
        ips = [linha.strip() for linha in res.splitlines() if linha.strip()]
        return ips if ips else None
    except Exception as e:
        log(f"Erro ao obter DNS atual: {e}")
        return None

def salvar_snapshot_sistema():
    with snapshot_lock:
        if os.path.exists(ARQUIVO_ESTADO):
            return
        try:
            estado = {
                "power_plan": obter_plano_energia_atual(),
                "dns": obter_dns_atual(),
                "timestamp": time.time()
            }
            temp_file = ARQUIVO_ESTADO + ".tmp"
            with open(temp_file, "w") as f:
                json.dump(estado, f, indent=4)
            os.replace(temp_file, ARQUIVO_ESTADO)
            log("[SNAPSHOT] Estado do sistema salvo com integridade garantida (Atomic Write).")
        except Exception as e:
            log(f"Erro ao salvar snapshot JSON: {e}")

def restaurar_snapshot_sistema():
    if not os.path.exists(ARQUIVO_ESTADO):
        return
    try:
        with open(ARQUIVO_ESTADO, "r") as f:
            estado = json.load(f)

        if estado.get("power_plan"):
            executar_comando_seguro(['powercfg', '/setactive', estado.get("power_plan")], "Rollback do Plano de Energia")

        if estado.get("dns"):
            dns_limpos = [f"'{d}'" for d in estado["dns"] if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", d)]
            if dns_limpos:
                dns_list = ",".join(dns_limpos)
                cmd = f"Get-NetAdapter | Where-Object {{$_.Status -eq 'Up' -and $_.InterfaceDescription -notmatch 'Virtual|VMware|Hyper-V|TAP'}} | Set-DnsClientServerAddress -ServerAddresses ({dns_list})"
                executar_comando_seguro(['powershell', '-Command', cmd], f"Rollback de DNS exato: {dns_list}")
        else:
            executar_comando_seguro(['powershell', '-Command', "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Set-DnsClientServerAddress -ResetServerAddresses"], "Rollback DNS Automático")

        log("[ROLLBACK] Snapshot JSON restaurado com sucesso.")
    except Exception as e:
        log(f"Erro ao restaurar snapshot JSON: {e}")

_pid_jogo_cache = None

def jogo_esta_aberto():
    global _pid_jogo_cache
    if _pid_jogo_cache and psutil.pid_exists(_pid_jogo_cache):
        return True
    try:
        for proc in psutil.process_iter(['name', 'pid']):
            nome = proc.info['name']
            if nome and nome.lower() in ['aika.exe', 'aika_br.exe', 'aikabr.exe', 'gameengine.exe', 'aikalauncher.exe']:
                _pid_jogo_cache = proc.info['pid']
                return True
    except Exception as e:
        log(f"Aviso ao checar processos abertos: {e}")
    return False

def executar_comando_seguro(cmd, descricao):
    try:
        resultado = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if resultado.returncode == 0:
            log(f"[SUCESSO] {descricao}")
            return True
        else:
            log(f"[FALHA] {descricao} (Erro: {resultado.returncode})")
            return False
    except Exception as e:
        log(f"[ERRO CRÍTICO] {descricao}: {e}")
        return False

def fazer_backup_com_hash_otimizado(caminho_original, caminho_backup):
    try:
        if not os.path.exists(caminho_original):
            return False
        os.makedirs(os.path.dirname(caminho_backup), exist_ok=True)
        h = hashlib.sha256()
        buffer_size = 65536
        with open(caminho_original, 'rb') as src, open(caminho_backup, 'wb') as dst:
            while chunk := src.read(buffer_size):
                dst.write(chunk)
                h.update(chunk)
        hash_val = h.hexdigest()
        log(f"Backup preservado: {os.path.basename(caminho_original)} [SHA256: {hash_val[:8]}...]")
        return True
    except Exception as e:
        log(f"Erro ao fazer backup otimizado: {e}")
        return False

def fazer_backup_registro(chave_completa, nome_arquivo):
    try:
        os.makedirs(PASTA_BACKUP_REG, exist_ok=True)
        destino = os.path.join(PASTA_BACKUP_REG, f"{nome_arquivo}.reg")
        if not os.path.exists(destino):
            executar_comando_seguro(['reg', 'export', chave_completa, destino, '/y'], f"Backup do Registro: {nome_arquivo}")
    except Exception as e:
        log(f"Erro backup de registro: {e}")

def criar_ponto_restauracao():
    try:
        marcador = os.path.join(PASTA_BACKUP, "ponto_restauracao_criado.txt")
        if os.path.exists(marcador):
            return True
        cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-Command',
               'Checkpoint-Computer -Description "AikaOptimizer_Backup_Seguranca" -RestorePointType "MODIFY_SETTINGS"']
        if executar_comando_seguro(cmd, "Ponto de Restauração do Windows"):
            os.makedirs(PASTA_BACKUP, exist_ok=True)
            with open(marcador, 'w') as f:
                f.write("Ponto de restauracao criado.")
            return True
        return False
    except Exception as e:
        log(f"Aviso ao criar ponto de restauração: {e}")
        return False

def restaurar_tudo_jogo(pasta_jogo=PASTA_JOGO_PADRAO):
    with lock_otimizacao:
        if jogo_esta_aberto():
            return False, "⚠️ FECHE O JOGO PRIMEIRO! O Aika está aberto."
        try:
            if not os.path.exists(PASTA_BACKUP):
                return False, "Nenhum backup de jogo encontrado."
            arquivos_restaurados = 0
            for root, dirs, files in os.walk(PASTA_BACKUP):
                if "Registro_Sistema" in root:
                    continue
                for file in files:
                    if file in ["aika_optimizer.log", "ponto_restauracao_criado.txt", "estado_sistema.json", "estado_sistema.json.tmp"]:
                        continue
                    caminho_backup = os.path.join(root, file)
                    caminho_relativo = os.path.relpath(caminho_backup, PASTA_BACKUP)
                    caminho_destino_jogo = os.path.join(pasta_jogo, caminho_relativo)
                    
                    if os.path.exists(caminho_backup) and os.path.getsize(caminho_backup) > 0:
                        if os.path.exists(caminho_destino_jogo):
                            try:
                                os.chmod(caminho_destino_jogo, stat.S_IWRITE)
                                os.remove(caminho_destino_jogo)
                            except Exception as e:
                                log(f"Aviso ao remover arquivo original para restore: {e}")
                        os.makedirs(os.path.dirname(caminho_destino_jogo), exist_ok=True)
                        shutil.copy2(caminho_backup, caminho_destino_jogo)
                        arquivos_restaurados += 1
                    else:
                        log(f"Aviso: Arquivo de backup ignorado por estar vazio ou ausente ({file}).")
            
            log(f"Rollback do jogo executado. {arquivos_restaurados} arquivos restaurados.")
            return True, f"Sucesso! {arquivos_restaurados} arquivos restaurados."
        except Exception as e:
            return False, f"Erro ao restaurar: {str(e)}"

def restaurar_registro_sistema():
    with lock_otimizacao:
        try:
            restaurar_snapshot_sistema()
            for exe in ["aika.exe", "aika_br.exe", "aikabr.exe", "GameEngine.exe", "gameengine.exe"]:
                chave_ifeo = f"HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\{exe}\\PerfOptions"
                executar_comando_seguro(['reg', 'delete', chave_ifeo, '/f'], f"Limpando IFEO de {exe}")

            if not os.path.exists(PASTA_BACKUP_REG):
                return False, "Backup de registro não encontrado."
            restaurados = 0
            for arquivo in os.listdir(PASTA_BACKUP_REG):
                if arquivo.endswith(".reg"):
                    caminho = os.path.join(PASTA_BACKUP_REG, arquivo)
                    if executar_comando_seguro(['reg', 'import', caminho], f"Restaurando {arquivo}"):
                        restaurados += 1
            return True, f"Sistema revertido com sucesso! ({restaurados} chaves, + Snapshot JSON)"
        except Exception as e:
            return False, str(e)

def apagar_arquivos_pasta(caminho_pasta):
    if not os.path.exists(caminho_pasta):
        return
    for root, dirs, files in os.walk(caminho_pasta):
        for f in files:
            try:
                caminho = os.path.join(root, f)
                os.chmod(caminho, stat.S_IWRITE)
                os.remove(caminho)
            except Exception:
                pass 

def limpar_profundo(esvaziar_lixeira=False):
    try:
        criar_ponto_restauracao()
        if esvaziar_lixeira:
            try:
                winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            except Exception as e:
                log(f"Aviso ao limpar lixeira: {e}")

        windir = os.environ.get('WINDIR', r'C:\Windows')
        programdata = os.environ.get('PROGRAMDATA', r'C:\ProgramData')
        pastas_limpeza = [
            os.environ.get('TEMP'),
            os.path.join(windir, 'Temp'),
            os.path.join(windir, 'SoftwareDistribution', 'Download'),
            os.path.join(programdata, 'Microsoft', 'Windows', 'WER', 'ReportArchive')
        ]
        for pasta in pastas_limpeza:
            if pasta:
                apagar_arquivos_pasta(pasta)
        log("Limpeza profunda concluída.")
        return True
    except Exception as e:
        raise Exception(f"Falha na limpeza: {e}")

def modo_desempenho_maximo():
    if not executar_comando_seguro(['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'], "Plano Alto Desempenho"):
        log("Aviso: Plano Alto Desempenho padrão não encontrado, o Windows pode estar usando um plano customizado.")
    return True

def otimizar_multimidia_jogos():
    try:
        chave = r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
        fazer_backup_registro(chave, "backup_multimidia")
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "NetworkThrottlingIndex", 0, winreg.REG_DWORD, 0xFFFFFFFF)
        winreg.SetValueEx(key, "SystemResponsiveness", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        log("[SUCESSO] Network Throttling desativado e System Responsiveness otimizado.")
        return True
    except Exception as e:
        log(f"Erro ao otimizar multimídia: {e}")
        return False

def otimizar_resposta_teclado():
    try:
        fazer_backup_registro(r"HKCU\Control Panel\Keyboard", "backup_teclado")
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Keyboard", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "KeyboardDelay", 0, winreg.REG_SZ, "0")
        winreg.SetValueEx(key, "KeyboardSpeed", 0, winreg.REG_SZ, "31")
        winreg.CloseKey(key)
        return True
    except Exception as e:
        raise Exception(f"Falha de permissão no Registro do Teclado: {e}")

def otimizar_rede_estabilidade():
    if not executar_comando_seguro(['ipconfig', '/flushdns'], "Limpeza Cache DNS"):
        raise Exception("Falha ao limpar DNS")
    return True

def prioridade_total():
    try:
        sucesso = False
        lista_exes = ["aika.exe", "aika_br.exe", "aikabr.exe", "GameEngine.exe", "gameengine.exe"]
        for exe in lista_exes:
            chave = f"HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\{exe}"
            fazer_backup_registro(chave, f"backup_prioridade_{exe}")
            cmd = ['reg', 'add', f"{chave}\\PerfOptions", '/v', 'CpuPriorityClass', '/t', 'REG_DWORD', '/d', '3', '/f']
            if executar_comando_seguro(cmd, f"Prioridade {exe}"):
                sucesso = True

        for proc in psutil.process_iter(['name', 'pid']):
            nome = proc.info['name']
            if nome and nome.lower() in lista_exes:
                try:
                    p = psutil.Process(proc.info['pid'])
                    if hasattr(psutil, "HIGH_PRIORITY_CLASS"):
                        p.nice(psutil.HIGH_PRIORITY_CLASS)
                    elif hasattr(psutil, "ABOVE_NORMAL_PRIORITY_CLASS"):
                        p.nice(psutil.ABOVE_NORMAL_PRIORITY_CLASS)
                    log(f"[SUCESSO] Prioridade alterada em tempo real para: {nome}")
                    sucesso = True
                except Exception as e:
                    log(f"Falha ao mudar prioridade em tempo real: {e}")
        return sucesso
    except Exception as e:
        raise e

def desativar_game_bar():
    try:
        fazer_backup_registro(r"HKCU\Software\Microsoft\Windows\CurrentVersion\GameDVR", "backup_gamedvr")
        key1 = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\GameDVR", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key1, "AppCaptureEnabled", 0, winreg.REG_DWORD, 0)
        winreg.SetValueEx(key1, "GameDVR_Enabled", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key1)

        fazer_backup_registro(r"HKCU\System\GameConfigStore", "backup_gameconfigstore")
        key2 = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key2, "GameDVR_Enabled", 0, winreg.REG_DWORD, 0)
        winreg.SetValueEx(key2, "GameDVR_FSEBehaviorMode", 0, winreg.REG_DWORD, 2)
        winreg.CloseKey(key2)

        return True
    except Exception as e:
        log(f"Aviso ao desativar Game Bar: {e}")
        return True

def testar_conexao():
    try:
        return subprocess.run(["ping", "-n", "1", "-w", "2000", "8.8.8.8"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
    except Exception:
        return False

def alterar_dns(escolha):
    salvar_snapshot_sistema()
    dns_backup = obter_dns_atual()
    try:
        base_cmd = "Get-NetAdapter | Where-Object {$_.Status -eq 'Up' -and $_.InterfaceDescription -notmatch 'Virtual|VMware|Hyper-V|TAP'} | "
        if escolha == "Google":
            cmd = ['powershell', '-Command', base_cmd + "Set-DnsClientServerAddress -ServerAddresses ('8.8.8.8','8.8.4.4')"]
        elif escolha == "Cloudflare":
            cmd = ['powershell', '-Command', base_cmd + "Set-DnsClientServerAddress -ServerAddresses ('1.1.1.1','1.0.0.1')"]
        else:
            cmd = ['powershell', '-Command', base_cmd + "Set-DnsClientServerAddress -ResetServerAddresses"]

        if not executar_comando_seguro(cmd, f"DNS para {escolha}"):
            return False

        time.sleep(2)
        if not testar_conexao():
            log("[FALHA] O novo DNS quebrou a conexão com a internet. Iniciando Rollback...")
            if dns_backup:
                dns_list = ",".join([f"'{d}'" for d in dns_backup])
                executar_comando_seguro(['powershell', '-Command', base_cmd + f"Set-DnsClientServerAddress -ServerAddresses ({dns_list})"], "Rollback DNS")
            else:
                executar_comando_seguro(['powershell', '-Command', base_cmd + "Set-DnsClientServerAddress -ResetServerAddresses"], "Rollback DNS Automático")
            return False
        return True
    except Exception as e:
        log(f"Erro inesperado no DNS: {e}")
        return False

def injetar_mods(lista_arquivos_mods, pasta_jogo=PASTA_JOGO_PADRAO):
    with lock_otimizacao:
        if jogo_esta_aberto():
            return -2
        try:
            mapa_mods = {os.path.basename(c).lower(): c for c in lista_arquivos_mods}
            arquivos_substituidos = 0

            for root, dirs, files in os.walk(pasta_jogo):
                for file in files:
                    if file.lower() in mapa_mods:
                        origem = mapa_mods[file.lower()]
                        destino = os.path.join(root, file)

                        caminho_relativo = os.path.relpath(destino, PASTA_JOGO_PADRAO)
                        caminho_backup = os.path.join(PASTA_BACKUP, caminho_relativo)

                        if not os.path.exists(caminho_backup):
                            fazer_backup_com_hash_otimizado(destino, caminho_backup)

                        try:
                            os.chmod(destino, stat.S_IWRITE)
                            with open(origem, 'rb') as src, open(destino, 'wb') as dst:
                                shutil.copyfileobj(src, dst, length=65536)
                            arquivos_substituidos += 1
                        except Exception:
                            try:
                                os.remove(destino)
                                shutil.copy2(origem, destino)
                                arquivos_substituidos += 1
                            except Exception as e:
                                log(f"Erro ao substituir {file}: {e}")

            return arquivos_substituidos
        except Exception as e:
            log(f"Erro no mapeamento de mods: {e}")
            return -1

def iniciar_jogo(pasta_jogo=PASTA_JOGO_PADRAO):
    for exe in ["AikaLauncher.exe", "aika_br.exe", "aika.exe", "GameEngine.exe"]:
        caminho = os.path.join(pasta_jogo, exe)
        if os.path.exists(caminho):
            try:
                os.startfile(caminho)
                return True
            except Exception as e:
                log(f"Aviso ao tentar iniciar executável {exe}: {e}")
    return False

def remover_weaponeff3(pasta_jogo=PASTA_JOGO_PADRAO):
    with lock_otimizacao:
        if jogo_esta_aberto():
            return -2
        try:
            removido = False
            for root, dirs, files in os.walk(pasta_jogo):
                for file in files:
                    if file.lower() == "weaponeff3.bin":
                        caminho = os.path.join(root, file)
                        caminho_relativo = os.path.relpath(caminho, PASTA_JOGO_PADRAO)
                        caminho_backup = os.path.join(PASTA_BACKUP, caminho_relativo)
                        if not os.path.exists(caminho_backup):
                            fazer_backup_com_hash_otimizado(caminho, caminho_backup)
                        try:
                            os.chmod(caminho, stat.S_IWRITE)
                            os.remove(caminho)
                            removido = True
                        except Exception as e:
                            log(f"Falha ao remover WeaponEff3.bin: {e}")
            return removido
        except Exception as e:
            log(f"Erro geral ao remover WeaponEff3: {e}")
            return False

def substituir_audio_customizado(novo_audio, arquivo_alvo):
    with lock_otimizacao:
        if jogo_esta_aberto():
            return False, "⚠️ FECHE O JOGO PRIMEIRO! O Aika está aberto."
        try:
            novo_audio = os.path.normpath(novo_audio)
            arquivo_alvo = os.path.normpath(arquivo_alvo)
            if not os.path.exists(novo_audio) or not os.path.exists(arquivo_alvo):
                return False, "Arquivo não encontrado."

            caminho_relativo = os.path.relpath(arquivo_alvo, PASTA_JOGO_PADRAO)
            caminho_backup = os.path.join(PASTA_BACKUP, caminho_relativo)
            if not os.path.exists(caminho_backup):
                fazer_backup_com_hash_otimizado(arquivo_alvo, caminho_backup)

            try:
                os.chmod(arquivo_alvo, stat.S_IWRITE)
                os.remove(arquivo_alvo)
            except Exception as e:
                log(f"Aviso ao remover áudio alvo: {e}")
            shutil.copy2(novo_audio, arquivo_alvo)
            return True, "Sucesso"
        except Exception as e:
            log(f"Erro ao injetar áudio: {e}")
            return False, str(e)

def restaurar_audio_original(arquivo_alvo):
    with lock_otimizacao:
        if jogo_esta_aberto():
            return False, "⚠️ FECHE O JOGO PRIMEIRO!"
        try:
            arquivo_alvo = os.path.normpath(arquivo_alvo)
            caminho_relativo = os.path.relpath(arquivo_alvo, PASTA_JOGO_PADRAO)
            caminho_backup = os.path.join(PASTA_BACKUP, caminho_relativo)
            
            if os.path.exists(caminho_backup) and os.path.getsize(caminho_backup) > 0:
                try:
                    os.chmod(arquivo_alvo, stat.S_IWRITE)
                    os.remove(arquivo_alvo)
                except Exception as e:
                    log(f"Aviso ao remover arquivo original para restore: {e}")
                shutil.copy2(caminho_backup, arquivo_alvo)
                return True, "Áudio restaurado com sucesso!"
            return False, "Nenhum backup válido foi encontrado para este arquivo."
        except Exception as e:
            return False, str(e)

def otimizar_tcp_nodelay():
    try:
        interfaces_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
        fazer_backup_registro(f"HKLM\\{interfaces_path}", "backup_tcp_nodelay")

        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, interfaces_path, 0, winreg.KEY_READ)
        for i in range(winreg.QueryInfoKey(key)[0]):
            subkey_name = winreg.EnumKey(key, i)
            subkey_path = f"{interfaces_path}\\{subkey_name}"
            try:
                subkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(subkey, "TcpAckFrequency", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(subkey, "TCPNoDelay", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(subkey)
            except Exception as e:
                log(f"Aviso na interface {subkey_name}: {e}")
        winreg.CloseKey(key)

        return True
    except Exception as e:
        raise e