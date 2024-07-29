import os
from app.configuration import *
import subprocess
import time

#PATH FOR THE NEW TIKTOK UPLOADER SUBMODULE
# lien du submodule : https://github.com/makiisthenes/TiktokAutoUploader
OUPUT_FOR_THE_NEW_UPLOAD = os.path.join(LIBRARY_PATH, 'TiktokAutoUploader/VideosDirPath')
COOKIE_SESSION_DIRECTORY = os.path.join(LIBRARY_PATH, 'TiktokAutoUploader/CookiesDir')
TiktokAutoUploader_DIR = os.path.join(LIBRARY_PATH, 'TiktokAutoUploader')
USER_CONFIG_NAME = 'dvlad'
TAGS = "#humour #fyp #foryou #foryoupage #fy #viral #funnyvideos"


def upload_to_tiktok(link, title):
    try:
        os.chdir(TiktokAutoUploader_DIR)

        def check_files_for_string_in_name(directory, search_string):
            # Parcourt tous les fichiers dans le répertoire spécifié
            for filename in os.listdir(directory):
                # Vérifie si le nom du fichier contient la chaîne recherchée
                if search_string in filename:
                    print(f'Cookie de {USER_CONFIG_NAME} est enregistré.')
                    return True
            print(f'Cookie de {USER_CONFIG_NAME} n\'est pas enregistré.')
            return False

        if not check_files_for_string_in_name(COOKIE_SESSION_DIRECTORY, USER_CONFIG_NAME):
            commande = [
                "python",
                "cli.py",
                "login",
                "-n",
                "{}".format(USER_CONFIG_NAME),
            ]

            resultat = subprocess.run(commande, check=True, capture_output=True, text=True)
            print(f"Sortie standard : {resultat.stdout}")
            print(f"Sortie d'erreur : {resultat.stderr}")

        # Commande à exécuter
        commande = [
            "python",
            "cli.py",
            "upload",
            "--user",
            "{}".format(USER_CONFIG_NAME),
            "-v",
            "{}".format(link),
            "-t",
            "{} - {}".format(title, TAGS)
        ]

        resultat = subprocess.run(commande, check=True, capture_output=True, text=True)
        print(f"Sortie standard : {resultat.stdout}")
        print(f"Sortie d'erreur : {resultat.stderr}")
        time.sleep(5)

    except Exception as e:
        print(str(e))