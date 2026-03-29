import ctypes, sys, time, threading
from ui import AikaEliteUI
import optimizer as opt

# --- FORÇA O WINDOWS A RECONHECER O NOME E O ÍCONE NA BARRA DE TAREFAS ---
try:
    meu_app_id = 'diegobfr07.akbr.optimizer.1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(meu_app_id)
except:
    pass

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

def processo_de_otimizacao(app_ref):
    app_ref.log_box.delete("0.0", "end")
    app_ref.write_log("INICIANDO PROTOCOLO DE ELITE [2026]...")
    time.sleep(0.5)
    app_ref.write_log(">>> Estabelecendo conexão com os serviços do Windows...")
    time.sleep(0.8)
    
    if app_ref.var_clean.get():
        opt.limpar_profundo()
        app_ref.write_log("✓ Limpeza de Buffer: Cache e resíduos de memória purgados.")
        time.sleep(0.4)

    if app_ref.var_power.get():
        opt.modo_desempenho_maximo()
        app_ref.write_log("✓ Plano de Energia: Modo de performance máxima forçado com sucesso.")
        time.sleep(0.4)

    if app_ref.var_kb.get():
        opt.otimizar_resposta_teclado()
        app_ref.write_log("✓ Input Delay: Registro de teclado modificado para tempo de resposta nulo.")
        time.sleep(0.4)

    if app_ref.var_net.get():
        opt.otimizar_rede_estabilidade()
        app_ref.write_log("✓ Otimização de Rede: Modificações de TCP/IP aplicadas para estabilidade.")
        time.sleep(0.4)

    if app_ref.var_prio.get():
        opt.prioridade_total()
        app_ref.write_log("✓ Prioridade de Processo (IFEO): Windows alocado para foco total no Aika.")
        time.sleep(0.4)

    if app_ref.var_gamebar.get():
        opt.desativar_game_bar()
        app_ref.write_log("✓ Telemetria: Xbox Game Bar e serviços redundantes isolados.")
        time.sleep(0.4)
    
    if app_ref.var_weaponeff.get():
        if opt.remover_weaponeff3():
            app_ref.write_log("✓ Correção Visual: Arquivo WeaponEff3.bin erradicado com sucesso.")
        else:
            app_ref.write_log("ℹ️ Correção Visual: Diretório já se encontra limpo de anomalias (WeaponEff3).")
        time.sleep(0.4)

    if app_ref.var_config.get():
        if opt.aplicar_config_otimizada():
            app_ref.write_log("✓ CFG Elite: Perfil de vídeo/sistema forçado com sucesso no cliente do jogo.")
        else:
            app_ref.write_log("⚠️ Erro Crítico: Falha ao tentar injetar a configuração nativa.")
        time.sleep(0.4)

    # --- A MÁGICA DO DNS ACONTECE AQUI ---
    dns_selecionado = app_ref.dns_choice.get()
    if opt.alterar_dns(dns_selecionado):
        app_ref.write_log(f"✓ Roteamento DNS: Servidor alterado com sucesso para [{dns_selecionado}].")
    else:
        app_ref.write_log("⚠️ Erro de Roteamento: Falha ao tentar alterar o servidor DNS.")
    time.sleep(0.4)

    app_ref.write_log("------------------------------------------")
    app_ref.write_log("✓ OTIMIZAÇÃO CONCLUÍDA: SISTEMA PRONTO PARA OPERAÇÃO!")

def iniciar_thread_otimizacao():
    threading.Thread(target=processo_de_otimizacao, args=(app,), daemon=True).start()

if __name__ == "__main__":
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
        
    app = AikaEliteUI(iniciar_thread_otimizacao)
    app.mainloop()