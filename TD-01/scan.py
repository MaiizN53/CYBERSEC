# Scanner de port
import threading
import socket

# Définir une fonction qui va tester un port spécifique
def scan_port(host, port):
    try:
        # Création d'un objet socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Définir un délai pour éviter le TIMEOUT et blocage
        sock.settimeout(1)
        # Tentative de connexion sur le port (0 si la connexion a réussi)
        result = sock.connect_ex((host, port))
        # Si le port est ouvert (result == 0), on l'affiche
        if result == 0:
            print(f"[+] Port {port} is open")
        # Fermer le socket
        sock.close()
    except Exception as e:
        # Gestion des erreurs
        print(f"[-] Erreur sur le port {port}: {e}")

# Demander l'IP à scanner
target = input("Entrez l'IP à scanner: ")

# Demander la plage d'adresses à scanner
start_port = int(input("Port de début: "))
end_port = int(input("Port de fin: "))

# Informer l'utilisateur qu'on commence le scan
print(f"\n[***] Scan de la cible {target} sur les ports {start_port} à {end_port} [***]\n")

# Scanner les ports en parallèle
for port in range(start_port, end_port + 1):
    t = threading.Thread(target=scan_port, args=(target, port))
    t.start()
