import os
from app.configuration import *
import subprocess
import time

def upload_to_tiktok(cookie_name, link, title, is_delete_video = False):
    try:
        os.chdir(TiktokAutoUploader_DIR)

        def check_files_for_string_in_name(directory, search_string):
            # Parcourt tous les fichiers dans le répertoire spécifié
            for filename in os.listdir(directory):
                # Vérifie si le nom du fichier contient la chaîne recherchée
                if search_string in filename:
                    print(f'TiktokUpload : Cookie de {cookie_name} est enregistré.')
                    print(f'TiktokUpload : LA VIDEO VA ETRE UPLOAD...')
                    return True
            print(f'TiktokUpload : Cookie de {cookie_name} n\'est pas enregistré.')
            print(f'TiktokUpload : BESOIN DE S\'ENREGISTRER POUR UPLOAD LA VIDEO')
            return False

        if not check_files_for_string_in_name(COOKIE_SESSION_DIRECTORY, cookie_name):
            commande = [
                "py",
                "-m",
                "cli.py",
                "login",
                "-n",
                "{}".format(cookie_name),
            ]

            resultat = subprocess.run(commande, check=True, capture_output=True, text=True)
            print(f"Sortie standard : {resultat.stdout}")
            print(f"Sortie d'erreur : {resultat.stderr}")

        # Commande à exécuter
        commande = [
            "py",
            "-m",
            "cli.py",
            "upload",
            "--user",
            "{}".format(cookie_name),
            "-v",
            "{}".format(link),
            "-t",
            "{} - {}".format(title, TAGS)
        ]

        resultat = subprocess.run(commande, check=True, capture_output=True, text=True)
        print(f"Sortie standard : {resultat.stdout}")
        print(f"Sortie d'erreur : {resultat.stderr}")
        time.sleep(3)
        if is_delete_video:
            os.remove(OUPUT_FOR_THE_NEW_UPLOAD + '/' + link)
        time.sleep(0.5)

    except Exception as e:
        print(str(e))