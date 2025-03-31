# Demander une adresse ip à l'utilisateur
import platform
import subprocess

ip = input("entrez une adresse ip à PING")
# On detecte l'os pour adapté la commande
param = "-n" if platform.system().lower() == "windows" else "-c"
#Construction du PING vers une liste
commande = ["ping", param, "1", ip]

print("Ping en cours")

#On execute le PING
try:
    result = subprocess.run(commande,stdout=subprocess.DEVNULL)
    if result.returncode == 0:
        print("la cible est en ligne")
    else:
        print("Aucune réponse")
except Exception as e:
    print(f"Erreur lors du ping {e}")


