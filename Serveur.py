import socket
import platform

# --- CONFIGURATION ---
PORT = 65432
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
╚══════════════════════════════════════════╝
"""

def handle_client(conn, addr):
    print(f"\n[+] APPAREIL DISTANT CONNECTÉ : {addr[0]}")

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
            cmd = input(f"\n({addr[0]}) > ").strip()
            if not cmd:
                continue

            if cmd.lower() == "help":
                print(HELP_TEXT)
                continue

            conn.sendall(cmd.encode())

            if cmd.lower() == "exit":
                print("[*] Déconnexion envoyée.")
                break

            try:
                conn.settimeout(10)
                reponse = conn.recv(4096).decode()
                print(f"[PC DISTANT] : {reponse}")
            except socket.timeout:
                print("[!] Timeout — pas de réponse du client.")
            finally:
                conn.settimeout(None)

        except (BrokenPipeError, ConnectionResetError):
            print("[!] Connexion interrompue par le client.")
            break
        except KeyboardInterrupt:
            print("\n[*] Interruption clavier. Fermeture.")
            conn.sendall(b"exit")
            break


def start_server():
    print("--- RACTT SERVER CENTRAL ---")
    print(f"[*] Système  : {platform.system()}")
    print(f"[*] Port     : {PORT}")
    print("[*] En attente d'une connexion...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            s.bind(('0.0.0.0', PORT))
            s.listen(1)
        except Exception as e:
            print(f"[!] Erreur de démarrage : {e}")
            return

        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    handle_client(conn, addr)
                print("\n[*] En attente d'une nouvelle connexion...")
            except KeyboardInterrupt:
                print("\n[*] Serveur arrêté.")
                break


if __name__ == "__main__":
    start_server()
