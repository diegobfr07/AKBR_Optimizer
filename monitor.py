import socket, time, threading
import psutil

def calcular_ping(ip, porta):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.7)
        inicio = time.time()
        res = s.connect_ex((ip, porta))
        fim = time.time()
        s.close()
        return int((fim - inicio) * 1000) if res == 0 else None
    except: 
        return None

def definir_cor(ping):
    if ping is None: return "#ff0000"
    if ping <= 50: return "#00ff00"   
    if ping <= 100: return "#ffff00"  
    return "#ff4b4b"                  

def iniciar_monitor(ip, porta, callback):
    def loop():
        while True:
            p = calcular_ping(ip, porta)
            cor = definir_cor(p)
            
            try:
                ram = psutil.virtual_memory().percent
                disco = psutil.disk_usage('C:\\').percent
            except:
                ram, disco = 0, 0
                
            try:
                callback(p, cor, ram, disco)
            except:
                pass 
                
            time.sleep(3)
            
    threading.Thread(target=loop, daemon=True).start()