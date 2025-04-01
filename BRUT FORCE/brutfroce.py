import itertools
import string
import time
import sys


def brute_force_demo(target, max_length=3, delay=1):
    """
    Démonstration éducative d'un principe de force brute
    À N'UTILISER QUE SUR DES SYSTÈMES AUTORISÉS
    """
    print("\n=== DÉMONSTRATION ÉDUCATIVE ===")
    print(f"Cible: {target}")
    print(f"Longueur max testée: {max_length}")
    print(f"Délai entre tentatives: {delay}s\n")

    chars = string.ascii_lowercase + string.digits
    attempts = 0
    start_time = time.time()

    try:
        for length in range(1, max_length + 1):
            for guess in itertools.product(chars, repeat=length):
                password = ''.join(guess)
                attempts += 1

                # Affichage dynamique
                sys.stdout.write(f"\rTentative {attempts}: {password.ljust(max_length)}")
                sys.stdout.flush()

                # Simulation de tentative de connexion
                # REMPLACER PAR UNE VÉRIFICATION RÉELLE SI AUTORISÉ
                if password == target:
                    elapsed = time.time() - start_time
                    print(f"\n\nMot de passe trouvé: '{password}'")
                    print(f"Tentatives: {attempts}")
                    print(f"Temps écoulé: {elapsed:.2f} secondes")
                    return True

                time.sleep(delay)  # Respect éthique

    except KeyboardInterrupt:
        print("\n\nInterruption par l'utilisateur")
        return False

    print("\n\nAucun résultat trouvé avec les paramètres actuels")
    return False


if __name__ == "__main__":
    # CONFIGURATION (À ADAPTER)
    DEMO_PASSWORD = "abc"  # Mot de passe de test pour la démo
    MAX_LENGTH = 4  # Longueur maximale à tester
    DELAY = 0.5  # Délai entre tentatives (en secondes)

    # AVERTISSEMENT
    print("ATTENTION: Ce script est à but éducatif uniquement.")
    print("N'UTILISEZ PAS CE SCRIPT SUR DES SYSTÈMES SANS AUTORISATION EXPRESSE.\n")

    # Exécution
    brute_force_demo(
        target=DEMO_PASSWORD,
        max_length=MAX_LENGTH,
        delay=DELAY
    )