import os
from app.configuration import *
import subprocess
import time

def upload_to_tiktok(cookie_name, link, title, is_delete_video=False):
    try:
        os.chdir(TiktokAutoUploader_DIR)
        print("Move to -> " + TiktokAutoUploader_DIR)

        def check_files_for_string_in_name(directory, search_string):
            for filename in os.listdir(directory):
                if search_string in filename:
                    print(f'TiktokUpload : Cookie de {cookie_name} est enregistré.')
                    print(f'TiktokUpload : LA VIDEO VA ETRE UPLOAD...')
                    return True
            print(f'TiktokUpload : Cookie de {cookie_name} n\'est pas enregistré.')
            print(f'TiktokUpload : BESOIN DE S\'ENREGISTRER POUR UPLOAD LA VIDEO')
            return False

        def run_command(command):
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for stdout_line in iter(process.stdout.readline, ""):
                print(stdout_line, end="")
            process.stdout.close()
            process.wait()
            stderr = process.stderr.read()
            if stderr:
                print(f"Sortie d'erreur : {stderr}")

        if not check_files_for_string_in_name(COOKIE_SESSION_DIRECTORY, cookie_name):
            commande = [
                "py",
                "cli.py",
                "login",
                "-n",
                "{}".format(cookie_name),
            ]
            run_command(commande)

        # Commande à exécuter
        commande = [
            "py",
            "cli.py",
            "upload",
            "--user",
            "{}".format(cookie_name),
            "-v",
            "{}".format(link),
            "-t",
            "{} - {}".format(title, TAGS)
        ]
        run_command(commande)

        time.sleep(3)
        if is_delete_video:
            os.remove(OUPUT_FOR_THE_NEW_UPLOAD + '/' + link)
        time.sleep(0.5)

    except Exception as e:
        print(str(e))

#upload_to_tiktok("dvlad", "pre-processed.mp4", "test")