import socket
import subprocess
import webbrowser
import os
import time
import platform

# --- CONFIGURATION ---
HOST = '103fa379dfd22edd-93-23-16-243.serveousercontent.com'  # URL Serveo ou IP locale
PORT = 65432
PASSWORD = "1234"
RECONNECT_DELAY = 5

def execute_action(command):
    sys_type = platform.system()
    try:
        if command.startswith("popup:"):
            msg = command[6:]
            if sys_type == "Windows":
                subprocess.run(['powershell', '-Command',
                    f'Add-Type -AssemblyName PresentationFramework; '
                    f'[System.Windows.MessageBox]::Show("{msg}")'])
            else:
                subprocess.run(['notify-send', '📱 Alerte Ractt', msg])
            return "Notification affichée"

        elif command.startswith("speak:"):
            msg = command[6:]
            if sys_type == "Windows":
                subprocess.run(['powershell', '-Command',
                    f'(New-Object -ComObject SAPI.SpVoice).Speak("{msg}")'])
            else:
                subprocess.run(['espeak-ng', '-v', 'fr', msg])
            return "Message vocal envoyé"

        elif command == "lock":
            if sys_type == "Windows":
                os.system("rundll32.exe user32.dll,LockWorkStation")
            else:
                os.system("xdg-screensaver lock")
            return "Écran verrouillé"

        elif command.startswith("browser:"):
            url = command[8:]
            if not url.startswith("http"):
                url = "https://" + url
            webbrowser.open(url)
            return f"Navigateur ouvert sur {url}"

        elif command == "battery":
            if sys_type == "Linux":
                bat_path = "/sys/class/power_supply/BAT0/capacity"
                if os.path.exists(bat_path):
                    with open(bat_path) as f:
                        return f"Batterie : {f.read().strip()}%"
                return "Batterie : fichier introuvable"
            return "Info batterie non supportée sur Windows"

        return f"Commande inconnue : {command}"

    except Exception as e:
        return f"Erreur : {str(e)}"


def main():
    print(f"[*] Client Ractt ({platform.system()}) — connexion vers {HOST}:{PORT}")
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect((HOST, PORT))

                if s.recv(1024).decode() == "AUTH_REQUIRED":
                    s.sendall(PASSWORD.encode())

                if s.recv(1024).decode() != "AUTH_SUCCESS":
                    print("[-] Authentification échouée.")
                    time.sleep(RECONNECT_DELAY)
                    continue

                print(f"[+] Connecté à {HOST} !")
                s.settimeout(None)

                while True:
                    data = s.recv(4096).decode()
                    if not data or data == "exit":
                        print("[*] Déconnexion demandée par le serveur.")
                        break
                    response = execute_action(data)
                    print(f"[>] {data} → {response}")
                    s.sendall(response.encode())

        except (ConnectionRefusedError, socket.timeout):
            print(f"[!] Serveur injoignable. Retry dans {RECONNECT_DELAY}s...")
        except Exception as e:
            print(f"[!] Erreur inattendue : {e}")

        time.sleep(RECONNECT_DELAY)


if __name__ == "__main__":
    main()
    
