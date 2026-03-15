import socket
import platform

# --- CONFIGURATION ---
PORT = 4444 # Doit être le même que celui du tunnel Serveo
PASSWORD = "1234"

HELP_TEXT = """
╔══════════════════════════════════════════╗
║           AIDE COMMANDES RACTT           ║
╠══════════════════════════════════════════╣
║  popup:message   → Bulle de notification ║
║  speak:message   → Synthèse vocale (FR)  ║
║  browser:url     → Ouvre un site web     ║
║  lock            → Verrouille le PC      ║
║  battery         → Niveau batterie Linux ║
║  exit            → Fermer la connexion   ║
║  [Toute autre commande shell ex: ls, cd] ║
╚══════════════════════════════════════════╝
"""

def handle_client(conn, addr):
    print(f"\n[+] APPAREIL DISTANT CONNECTÉ")
    
    # Réception des infos (IP et Hostname envoyés par le client)
    infos_initiales = conn.recv(1024).decode('utf-8')
    print(infos_initiales)

    conn.sendall(b"AUTH_REQUIRED")
    auth = conn.recv(1024).decode().strip()

    if auth != PASSWORD:
        conn.sendall(b"AUTH_FAILED")
        print("[-] Mot de passe incorrect. Connexion rejetée.")
        return

    conn.sendall(b"AUTH_SUCCESS")
    print("[OK] Accès autorisé. Tapez 'help' pour les options.")

    while True:
        try:
            cmd = input(f"RACTT > ").strip()
            if not cmd: continue
            if cmd.lower() == "help":
                print(HELP_TEXT)
                continue

            conn.sendall(cmd.encode())
            if cmd.lower() == "exit": break

            reponse = conn.recv(4096).decode()
            print(f"\n[RÉPONSE PC DISTANT] :\n{reponse}")

        except Exception as e:
            print(f"[!] Erreur : {e}")
            break

def start_server():
    print("--- RACTT SERVER CENTRAL ---")
    print(f"[*] Système  : {platform.system()}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', PORT))
        s.listen(1)
        print(f"[*] En attente sur le port {PORT}...")
        while True:
            conn, addr = s.accept()
            handle_client(conn, addr)

if __name__ == "__main__":
    start_server()
