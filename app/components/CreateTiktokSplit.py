import random
import re
import shutil
import time

import yt_dlp

from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.video.compositing.CompositeVideoClip import clips_array
from pytube import YouTube

from app.components.TiktokFeedsProviders import TiktokFeedsProviders
from app.configuration import *
import requests

class CreateTiktokSplit:
    def __init__(self):
        tiktokFeedsProviders = TiktokFeedsProviders(TRENDING_FILE_PATH, 1)
        self.list_main_video = tiktokFeedsProviders.getProvideTiktokFeeds()
        self.list_part_video = tiktokFeedsProviders.getVideosLinkFeeds()
        self.output_video_path = EDITED_PATH

    def download_dynamic_video(self, lien, output_path):
        link = None

        def download_tiktok_video(url, output_dir):
            try:
                # Créez un objet YT-DLP avec les options nécessaires
                ydl_opts = {
                    'format': 'mp4',
                    'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),  # Utilise l'ID vidéo pour nommer le fichier
                    'noplaylist': True,  # Télécharge seulement la vidéo et pas la playlist
                    'quiet': False,  # Affiche les logs pour le débogage
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Télécharger la vidéo
                    info_dict = ydl.extract_info(url, download=True)
                    video_id = info_dict.get('id', 'video')
                    video_file = os.path.join(output_dir, f'{video_id}.mp4')

                print(f"Vidéo téléchargée avec succès : {video_file}")
                return video_file

            except Exception as e:
                print(f"Erreur lors du téléchargement de la vidéo : {e}")
                return None

        def download_youtube_video(youtube_url, output_path):
            yt = YouTube(youtube_url)
            video_stream = yt.streams.filter(file_extension='mp4', res='720p').first()

            if video_stream:
                video_stream.download(output_path)
                print("\nVidéo téléchargée avec succès !")
                return os.path.join(output_path, video_stream.default_filename)
            else:
                raise RuntimeError("VideoMaker : Votre vidéo n'est pas connue de l'API")

        if "tiktok.com" in lien:
            link = download_tiktok_video(lien, output_path)
        elif "youtube.com" in lien:
            link = download_youtube_video(lien, output_path)
        return link

    def extract_video_id(self, url):
        # Regex pour capturer l'identifiant vidéo dans l'URL
        match = re.search(r'/video/(\d+)', url)
        if match:
            # Renvoie l'identifiant de la vidéo
            return match.group(1)
        else:
            # Si aucun identifiant n'est trouvé, renvoie None
            return None

    def remove_all_files_in_directory(self, directory_path):
        try:
            # Liste des fichiers et dossiers dans le répertoire spécifié
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)

                # Si c'est un fichier, le supprimer
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Fichier supprimé : {file_path}")
                # Si c'est un dossier, le supprimer avec son contenu
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"Dossier supprimé : {file_path}")

        except Exception as e:
            print(f"Erreur lors de la suppression des fichiers : {e}")

    def split_video(self):

        for link_video in self.list_main_video:

            path_main_video = self.download_dynamic_video(link_video, PATH_TEMP)
            print(path_main_video)
            # Charger la vidéo principale
            main_video = VideoFileClip(path_main_video)

            # Durée totale de la vidéo principale
            total_duration = main_video.duration

            # Index pour les noms des fichiers de sortie
            index = 0

            # Découper la vidéo principale en segments de 63 secondes
            for start in range(0, int(total_duration), TIKTOK_TEMPS_VIDEO):
                end = min(start + TIKTOK_TEMPS_VIDEO, total_duration)
                segment = main_video.subclip(start, end)

                if len(self.list_part_video) == 0:
                    print("La liste des vidéos part est vide.")
                    return

                choose_part_video = random.choice(self.list_part_video)
                secondary_video_path = self.download_dynamic_video(choose_part_video, PATH_TEMP)

                # Charger la vidéo secondaire
                secondary_video = VideoFileClip(secondary_video_path)

                # Ajuster la taille des vidéos pour les mettre côte à côte
                min_height = min(segment.h, secondary_video.h)
                segment = segment.resize(height=min_height)
                secondary_video = secondary_video.resize(height=min_height)

                # Enlever le son de la deuxième vidéo
                secondary_video = secondary_video.without_audio()

                # Créer un array de clips côte à côte
                combined_clip = clips_array([[segment, secondary_video]])

                # Sauvegarder le résultat
                output_filename = os.path.join(EDITED_PATH, f"combined_video_{index}.mp4")
                combined_clip.write_videofile(output_filename)

                index += 1

                # Libérer les ressources
                main_video.close()
                secondary_video.close()
                time.sleep(2)
                self.remove_all_files_in_directory(PATH_TEMP)

createTiktokSplit = CreateTiktokSplit()
createTiktokSplit.split_video()