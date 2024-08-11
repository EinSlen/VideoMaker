import math
import os
import random
import re
import shutil
import time
import schedule

import yt_dlp
import subprocess

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.video.compositing.CompositeVideoClip import clips_array
from pytube import YouTube

from app.components.TiktokFeedsProviders import TiktokFeedsProviders
from app.components.TiktokUploader import upload_to_tiktok
from app.configuration import *
import requests

class CreateTiktokSplit:
    def __init__(self, link_length = 1, add_sound = False, upload_tiktok = False):
        self.tiktokFeedsProviders = TiktokFeedsProviders(TRENDING_FILE_PATH, link_length)
        self.list_main_video = self.tiktokFeedsProviders.getProvideTiktokFeeds()
        self.list_part_video = self.tiktokFeedsProviders.getVideosLinkFeeds()
        self.tiktok_link_for_upload = []
        self.is_upload_tiktok = upload_tiktok
        self.is_add_sound = add_sound
        if upload_tiktok:
            print("CreateTiktokSplit : UPLOAD ACTIF /!\\ ")
        if add_sound:
            print("CreateTiktokSplit : SOUND ACTIF /!\\ ")


    def download_dynamic_video(self, lien, output_path):
        link, title = None, None

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
                    user_video = self.extract_video_user_name_from_tiktok_link(url)

                print(f"Vidéo téléchargée avec succès : {video_file}")
                return video_file, user_video.lower()

            except Exception as e:
                print(f"Erreur lors du téléchargement de la vidéo : {e}")
                return None

        def download_youtube_video(youtube_url, output_path):
            yt = YouTube(youtube_url)
            video_stream = yt.streams.filter(file_extension='mp4', res='720p').first()

            if video_stream:
                video_stream.download(output_path)
                print("\nVidéo téléchargée avec succès !")
                return os.path.join(output_path, video_stream.default_filename), video_stream.default_filename.lower()
            else:
                raise RuntimeError("VideoMaker : Votre vidéo n'est pas connue de l'API")

        if "tiktok.com" in lien:
            link, title = download_tiktok_video(lien, output_path)
        elif "youtube.com" in lien:
            link, title = download_youtube_video(lien, output_path)
        return link, title

    def extract_video_user_name_from_tiktok_link(self, url):
        match = re.search(r'tiktok\.com/@([a-zA-Z0-9._]+)', url)

        if match :
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
                    try:
                        clip = VideoFileClip(file_path)
                        clip.close()
                    except Exception as e:
                        print(f"Erreur lors de la fermeture du clip : {e}")
                    os.remove(file_path)
                    print(f"Fichier supprimé : {file_path}")
                # Si c'est un dossier, le supprimer avec son contenu
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"Dossier supprimé : {file_path}")

        except Exception as e:
            print(f"Erreur lors de la suppression des fichiers : {e}")

    def split_video(self):
        if len(self.list_part_video) == 0 or len(self.list_main_video) == 0:
            print("La liste des vidéos part est vide.")
            print("Aucune vidéo n'a été faite. Reload vidéo...")
            self.list_main_video = self.tiktokFeedsProviders.getProvideTiktokFeeds()
            self.list_part_video = self.tiktokFeedsProviders.getVideosLinkFeeds()
            self.split_video()
            return

        self.remove_all_files_in_directory(PATH_TEMP)

        for link_video in self.list_main_video:
            try:
                path_main_video, title = self.download_dynamic_video(link_video, PATH_TEMP)
                main_video = VideoFileClip(path_main_video)
            except:
                print("CreateTiktokSplit : Erreur lors du téléchargement de la vidéo main.")
                print("Reencoding")

                self.tiktokFeedsProviders = TiktokFeedsProviders(TRENDING_FILE_PATH, len(self.list_main_video))
                self.list_main_video = self.tiktokFeedsProviders.getProvideTiktokFeeds()
                self.list_part_video = self.tiktokFeedsProviders.getVideosLinkFeeds()
                self.split_video()
                return

            try:
                total_duration = main_video.duration
                index = 0

                for start in range(0, int(total_duration), TIKTOK_TEMPS_VIDEO):
                    end = min(start + TIKTOK_TEMPS_VIDEO, total_duration)

                    if math.ceil(end) - math.ceil(start) < TIKTOK_TEMPS_VIDEO - 2:
                        print("Temps de la vidéo restant trop court pour une nouvelle vidéo. Abandon.")
                        if index == 0:
                            print("Aucune vidéo n'a été faite. Reload vidéo...")

                            self.tiktokFeedsProviders = TiktokFeedsProviders(TRENDING_FILE_PATH, len(self.list_main_video))
                            self.list_main_video = self.tiktokFeedsProviders.getProvideTiktokFeeds()
                            self.list_part_video = self.tiktokFeedsProviders.getVideosLinkFeeds()
                            self.split_video()
                            return
                        break

                    segment = main_video.subclip(start, end)

                    choose_part_video = random.choice(self.list_part_video)
                    try:
                        secondary_video_path = self.download_dynamic_video(choose_part_video, PATH_TEMP)[0]
                        secondary_video = VideoFileClip(secondary_video_path)
                        secondary_video = secondary_video.subclip(0, main_video.duration)
                    except:
                        print("CreateTiktokSplit : Erreur lors du téléchargement de la vidéo secondaire.")
                        print("Reencoding")
                        self.tiktokFeedsProviders = TiktokFeedsProviders(TRENDING_FILE_PATH, len(self.list_main_video))
                        self.list_main_video = self.tiktokFeedsProviders.getProvideTiktokFeeds()
                        self.list_part_video = self.tiktokFeedsProviders.getVideosLinkFeeds()
                        self.split_video()
                        return

                    try:
                        print(f"Create Video : {index+1}/{len(self.list_main_video)}")
                        # Redimensionner les vidéos tout en maintenant le rapport d'aspect
                        segment = segment.resize(
                            height=RESOLUTION_TIKTOK[1])
                        secondary_video = secondary_video.resize(
                            height=RESOLUTION_TIKTOK[1])

                        # Enlever le son de la deuxième vidéo
                        secondary_video = secondary_video.without_audio()

                        # Créer un array de clips côte à côte
                        combined_clip = clips_array([[segment, secondary_video]])

                        #resize le clip finish
                        resolution_temp = (RESOLUTION_TIKTOK[0], 1000)
                        combined_clip = combined_clip.resize(newsize=resolution_temp)

                        if self.is_add_sound:
                            sound_files = [f for f in os.listdir(SOUND_DIRECTORY) if f.endswith('.mp3')]
                            if sound_files:
                                random_sound = random.choice(sound_files)
                                added_audio = AudioFileClip(os.path.join(SOUND_DIRECTORY, random_sound)).volumex(0.01)
                                original_audio = combined_clip.audio
                                combined_audio = CompositeAudioClip(
                                    [original_audio, added_audio.set_duration(original_audio.duration)])
                                combined_clip = combined_clip.set_audio(combined_audio)
                            else:
                                print("No sound file in " + SOUND_DIRECTORY)

                        # Sauvegarder le résultat
                        output_filename_base = f"combined_video_{index}.mp4"
                        output_filename = os.path.join(OUPUT_FOR_THE_NEW_UPLOAD, output_filename_base)
                        combined_clip.write_videofile(output_filename, fps=FPS_TIKTOK)
                        print("Saved video to", output_filename)
                        if index == 0:
                            self.tiktok_link_for_upload.append([output_filename_base, title])
                        else:
                            self.tiktok_link_for_upload.append([output_filename_base, title + " - Part " + str((index+1))])

                        index += 1

                    finally:
                        secondary_video.close()

            finally:
                main_video.close()
                try:
                    if self.is_upload_tiktok and len(self.tiktok_link_for_upload) > 0:
                        for link, title in self.tiktok_link_for_upload:
                            upload_to_tiktok(USER_CONFIG_NAME_1, link, title, True)
                            # os.remove(OUPUT_FOR_THE_NEW_UPLOAD + '/' + link)
                        self.tiktok_link_for_upload.clear()
                    # self.remove_all_files_in_directory(OUPUT_FOR_THE_NEW_UPLOAD)
                except Exception as e:
                    print("CreateTiktokSplit: Error lors de l'upload de la vidéo. Abandon.")
                    print("Error : " + str(e))

                self.remove_all_files_in_directory(PATH_TEMP)


"""
createTiktokSplit = CreateTiktokSplit() # on a 3 arguments optionnel (la taille des liens de la liste de base c'est 1 lien) et un pour le sond et upload sur tiktok automatiquement CreateTiktokSplit(5, True, True)
createTiktokSplit.split_video()
"""

def createTiktokSplit_TASK():
    createTiktokSplit = CreateTiktokSplit(1, True, True) # on a 2 arguments optionnel (la taille des liens de la liste de base c'est 1 lien) et un pour upload sur tiktok automatiquement CreateTiktokSplit(5, true)
    createTiktokSplit.split_video()

for hour in HOUR_LIST:
    schedule.every().day.at(hour).do(createTiktokSplit_TASK)

while True:
    schedule.run_pending()
    time.sleep(1)