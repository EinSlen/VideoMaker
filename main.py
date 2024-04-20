import os
import time
from colorama import init, Fore
import schedule
from pytube import YouTube

from app.components.TiktokUploader import TiktokUploader
from app.components.TrendingVideo import TrendingVideo
from app.components.VideoEditor import VideoEditorStart
from app.components.YoutubeForTiktok import YoutubeForTiktok
from app.configuration import MODEL_PATH, TEMPS_UPLOAD, VIDEOS_ID, VIDEOS_DIRECTORY
from app.lib.video_transcription.main import VideoTranscriber

init()

colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]

text = """𝓓𝓥𝓛𝓐𝓓 - TIKTOK UPLOADER"""

for i, char in enumerate(text):
    color = colors[i % len(colors)]
    print(color + char, end="", flush=True)
    time.sleep(0.1)
print()
time.sleep(1)

def execute_youtube_for_tiktok():
    youtubefortiktok = YoutubeForTiktok()
    youtubefortiktok.start()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def download_videos_from_file():
    try:
        print("Installation des vidéos d'édition...")
        with open(VIDEOS_ID, 'r') as file:
            links = file.readlines()
            for link in links:
                link = link.strip()  # Supprimer les espaces et les sauts de ligne
                try:

                    yt = YouTube(link)
                    stream = yt.streams.get_highest_resolution()
                    print(f"Téléchargement de {yt.title}...")
                    stream.download(VIDEOS_DIRECTORY)
                    print(f"{yt.title} téléchargée avec succès!")
                except Exception as e:
                    print(f"Erreur lors du téléchargement de la vidéo à partir du lien {link}: {e}")
    except FileNotFoundError:
        print(f"Fichier {VIDEOS_ID} introuvable!")

def select_number():
    mp4_files = [file for file in os.listdir(VIDEOS_DIRECTORY) if file.endswith(".mp4")]
    if len(mp4_files) == 0:
        print("Aucune vidéo pour éditer à été trouvé...")
        download_videos_from_file()
    else:
        print("Des vidéos ont été trouvée pour l'édition. Voulez-vous quand même installer les vidéos ?")
        download_input = input("Oui/Non : ")
        if download_input.lower() == "oui":
            download_videos_from_file()
    while True:
        try:
            print("MENU : ")
            print("1) - Récupérer toutes les vidéos tendances feed YouTube")
            print("2) - Upload une vidéo de YouTube sur TikTok (automatique)")
            print("3) - Editer une vidéo pour mettre sur TikTok (automatique)")
            print("4) - Sous titrer une vidéo (format tiktok)")
            print("5) - Envoyer une vidéo YouTube (tendance) vers TikTok (automatique)")
            print("6) - AUTOMATIQUE UPLOADER YOUTUBE TENDANCE VERS TIKTOK (Chaque 24h)")
            print(Fore.WHITE)
            number = int(input("Veuillez sélectionner un chiffre parmi 1, 2, 3, 4, 5, 6 : "))
            if number == 1:
                trending = TrendingVideo()
                trending.get_trending_videos()
            elif number == 2:
                path_video = input("Veuillez entrer le chemin de la vidéo : ")
                abs_path_video = os.path.abspath(path_video)
                if os.path.exists(abs_path_video):
                    titre = input("Veuillez entrer le titre de la vidéo : ")
                    TiktokUploader([(abs_path_video, titre)])
                else:
                    print("Le chemin spécifié n'existe pas. Veuillez réessayer.")
            elif number == 3:
                VideoEditorStart()
            elif number == 4:
                text = "TIPS : Le model de base est MEDIUM. Il faudrait mieux ne pas le changer /!\\ Pour ça faite entrer sans rien mettre"
                print("\033[91m {}\033[00m".format(text))
                model = input("Veuillez entrer le model de la vidéo : ")
                if model == "":
                    model = MODEL_PATH
                path_video = input("Veuillez entrer le chemin de la vidéo : ")
                abs_path_video = os.path.abspath(path_video)
                if os.path.exists(abs_path_video):
                    trannscriber = VideoTranscriber(model, path_video)
                    trannscriber.extract_audio()
                    trannscriber.transcribe_video()
                    trannscriber.create_video(path_video)
                else:
                    print("Le chemin spécifié n'existe pas. Veuillez réessayer.")
            elif number == 5:
                youtubefortiktok = YoutubeForTiktok()
                youtubefortiktok.start()
            elif number == 6:
                execute_youtube_for_tiktok()
                schedule.every(TEMPS_UPLOAD).minutes.do(execute_youtube_for_tiktok)
                print("Prochain envoie dans : ", TEMPS_UPLOAD)
                while True:
                    schedule.run_pending()
                    time.sleep(1)
            else:
                print("Choix invalide. Veuillez sélectionner un chiffre valide.")
        except ValueError:
            print("Entrée invalide. Veuillez saisir un chiffre entier.")
        clear_console()

select_number()

