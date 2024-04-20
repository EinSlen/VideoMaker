import os
import random
import shutil
import string
import sys
import wave

import numpy as np
from pytube import YouTube
from moviepy.video.VideoClip import TextClip, ColorClip
from moviepy.video.compositing.CompositeVideoClip import clips_array
from moviepy.editor import VideoFileClip, CompositeVideoClip
from app.components.SubtitleSrt import SubtitlesGenerator

import speech_recognition as sr
from app.configuration import *


#https://github.com/elebumm/RedditVideoMakerBot

from app.lib.video_transcription.main import VideoTranscriber


class VideoEditor:
    def __init__(self, titre_video='', youtube_url=None, start_time_input=0, end_time_input=30, sous_title="non"):
        self.titre_video = titre_video.upper()
        self.youtube_url = youtube_url
        self.start_time_input = start_time_input
        self.end_time_input = end_time_input
        self.PATH = ''.join(random.choices(string.ascii_letters.upper() + string.digits.upper(), k=12))
        self.VIDEO_PATH = ''
        if sous_title.lower() == "oui":
            self.sous_title = True
        else:
            self.sous_title = False

    def add_suffix_to_filename(self, filepath, new_directory=""):
        if new_directory == "":
            directory, filename_with_ext = os.path.split(filepath)
            filename, ext = os.path.splitext(filename_with_ext)
            suffix = 1
            new_filename = filename + ext
            while os.path.exists(os.path.join(directory, new_filename)):
                new_filename = f"{filename} ({suffix}){ext}"
                suffix += 1
            return os.path.join(directory, new_filename)

        directory, filename_with_ext = os.path.split(filepath)
        return os.path.join(new_directory, filename_with_ext)

    def delete_file(self, file_path):
        if os.path.exists(file_path) and file_path != '':
            try:
                VideoFileClip(file_path).close()
            except:
                print(f"VideoMaker : Impossible de close le fichier : {file_path}")
            os.remove(file_path)
            print(f"Fichier supprimé : {file_path}")
        else:
            print(f"VideoMaker : Le fichier n'existe pas : {file_path}")

    def download_youtube_video(self, output_path='./'):
        print("VideoMaker : Vidéo en cours de téléchargement...")
        yt = YouTube(self.youtube_url)
        video_stream = yt.streams.filter(file_extension='mp4', res='720p').first()

        if video_stream:
            video_stream.download(output_path)
            print("Vidéo téléchargée avec succès !")
            self.VIDEO_PATH = os.path.join(output_path, video_stream.default_filename)
        else:
            raise RuntimeError("VideoMaker : Votre vidéo n'est pas connu de l'API")

    def add_subtitle_to_video(self, input_video_path):
        try:
            if input_video_path is None or not os.path.exists(input_video_path):
                raise ValueError(f"Erreur : Le chemin de la vidéo d'entrée n'est pas valide. -> {input_video_path}")

            # Extraire l'audio de la vidéo
            if self.titre_video != '':
                temp_audio_path = self.titre_video+"temp_audio.wav"
            else:
                temp_audio_path = self.PATH+"temp_audio.wav"

            video_clip = VideoFileClip(input_video_path)
            video_clip.audio.write_audiofile(PATH_TEMP+temp_audio_path)

            file_name_srt, _ = os.path.splitext(temp_audio_path)
            srt_path = file_name_srt + '.srt'

            print(f"VideoMaker : Audio .wave ({PATH_TEMP+temp_audio_path}) -> .srt {PATH_TEMP+srt_path}")

            SubtitlesGenerator(PATH_TEMP+temp_audio_path, PATH_TEMP+srt_path)

            video_clip = VideoFileClip(input_video_path)
            subtitle_clip = self.create_subtitle_clip_from_srt(PATH_TEMP + srt_path, video_clip.size)
            
            self.delete_file(temp_audio_path)

            return CompositeVideoClip([video_clip, subtitle_clip])


        except Exception as e:
            if self.titre_video != '':
                self.delete_file(os.path.join(self.titre_video, "TEMP_MPY_wvf_snd.mp4"))
            else:
                self.delete_file(os.path.join(self.PATH, "TEMP_MPY_wvf_snd.mp4"))
            self.delete_file(self.VIDEO_PATH)
            print(f"VideoMaker : Erreur : {e}")

    def transcribe_audio(self, audio_path):
        try:
            print("VideoMaker : Transcription de l'audio à venir.")
            recognizer = sr.Recognizer()

            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_sphinx(audio_data, language='fr-FR')

            print("VideoMaker : Transcription de l'audio terminée.")

            return text

        except Exception as e:
            RuntimeError(f"VideoMaker : Erreur lors de la transcription audio : {e}")

    def merge_videos(self, video_path2, output_path, start_time, end_time):
        clip1 = VideoFileClip(self.VIDEO_PATH).subclip(start_time, end_time)
        clip2 = VideoFileClip(video_path2).subclip(0, end_time-start_time)

        clip2 = clip2.set_audio(None)
        clip2 = clip2.resize(height=clip1.h)

        print("Merge des vidéos... ")
        final_clip = clips_array([[clip1], [clip2]])

        final_clip = final_clip.resize(RESOLUTION_TIKTOK)

        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=FPS_TIKTOK)

        final_clip.close()

        clip_with_text = self.add_text_to_video(output_path)

        output_path_with_temp = self.add_suffix_to_filename(output_path, EDITED_PATH)

        clip_with_text.write_videofile(output_path_with_temp, codec='libx264',
                                   audio_codec='aac')

        clip_with_text.close()
        clip1.close()
        clip2.close()

        if self.sous_title:
            print("VideoMaker : Ajout des sous titres...")
            trannscriber = VideoTranscriber(MODEL_PATH, output_path_with_temp)
            trannscriber.extract_audio()
            trannscriber.transcribe_video()
            trannscriber.create_video(output_path_with_temp)

        self.delete_folder(PATH_TEMP)
        #self.deplacer_fichiers(PATH_TEMP, EDITED_PATH)

        print("VideoMaker : Merge des vidéos avec succès ! ")

    def delete_folder(self, dossier_source):
        fichiers = os.listdir(dossier_source)

        for fichier in fichiers:
            self.delete_file(os.path.join(dossier_source, fichier))

    def deplacer_fichiers(self, dossier_source, dossier_destination):
        """
        Déplace tous les fichiers d'un dossier source vers un dossier destination.

        Args:
            dossier_source (str): Le chemin du dossier source.
            dossier_destination (str): Le chemin du dossier destination.
        """
        # Liste de tous les fichiers dans le dossier source
        print(f"VideoMaker : déplacement de tous les fichiers {dossier_source} vers -> {dossier_destination}")
        fichiers = os.listdir(dossier_source)

        # Boucle à travers tous les fichiers et les déplacer vers le dossier destination
        for fichier in fichiers:
            chemin_complet_source = os.path.join(dossier_source, fichier)
            chemin_complet_destination = os.path.join(dossier_destination, fichier)
            shutil.move(chemin_complet_source, chemin_complet_destination)

        print("VideoMaker : Les fichiers ont été déplacés avec succès.")

    def add_text_to_video(self, input_video_path):
        try:
            if input_video_path is None or not os.path.exists(input_video_path):
                raise ValueError(f"Erreur : Le chemin de la vidéo d'entrée n'est pas valide. -> {input_video_path}")

            video_clip = VideoFileClip(input_video_path)

            if self.titre_video != '':

                text_clip = TextClip(self.titre_video, fontsize=70, color='black', font='Helvetica-Bold',
                                     size=(video_clip.size[0] // 4, None))
                text_clip = text_clip.set_pos(('center', 'center')).set_duration(video_clip.duration)

                background_clip = ColorClip(size=(text_clip.w, text_clip.h), color=(255, 255, 255))
                background_clip = background_clip.set_pos(('center', 'center')).set_duration(video_clip.duration)

                return CompositeVideoClip([video_clip, background_clip, text_clip])

            else:
                return video_clip

        except Exception as e:
            if self.titre_video != '':
                self.delete_file(os.path.join(self.titre_video, "TEMP_MPY_wvf_snd.mp4"))
            else:
                self.delete_file(os.path.join(self.PATH, "TEMP_MPY_wvf_snd.mp4"))
            self.delete_file(self.VIDEO_PATH)
            raise RuntimeError(f"Erreur : {e}")

    def editor(self):
        try:
            if ":" in self.start_time_input:
                start_time = sum(x * int(t) for x, t in zip([60, 1], self.start_time_input.split(":")))
            else:
                start_time = int(self.start_time_input)
            if ":" in self.end_time_input:
                end_time = sum(x * int(t) for x, t in zip([60, 1], self.end_time_input.split(":")))
            else:
                end_time = int(self.end_time_input)

            self.download_youtube_video(PATH_TEMP)

            if self.VIDEO_PATH is None:
                raise RuntimeError("VideoMaker : Le téléchargement de la vidéo a échoué.")

            # Choisir aléatoirement une vidéo du répertoire "videos"
            random_video = random.choice(os.listdir(VIDEOS_DIRECTORY))
            random_video_path = os.path.join(VIDEOS_DIRECTORY, random_video)

            # Extraire les clips nécessaires des vidéos
            if self.titre_video != '':
                random_filename = self.titre_video
            else:
                random_filename = self.PATH

            output_path = os.path.join(EDITED_PATH, f"{random_filename}.mp4")

            CONTINUE = True
            while CONTINUE:
                print(self.add_suffix_to_filename(output_path, EDITED_PATH))
                if os.path.exists(output_path):
                    output_path = self.add_suffix_to_filename(output_path)
                    print("VideoMaker : Changement du path : ", output_path)
                else:
                    CONTINUE = False

            output_path = self.add_suffix_to_filename(output_path, PATH_TEMP)

            # Ajouter le titre à la vidéo
            self.merge_videos(random_video_path, output_path, start_time, end_time)

            path_finish = self.add_suffix_to_filename(output_path, EDITED_PATH)

            print(f"VideoMaker: La vidéo résultante a été enregistrée à : {path_finish}")

            return path_finish

        except Exception as e:
            self.delete_file(os.path.join(self.PATH, "TEMP_MPY_wvf_snd.mp4"))
            self.delete_file(self.VIDEO_PATH)
            raise RuntimeError(f"Erreur : {e}")

    def create_subtitle_clip_from_srt(self, srt_path, video_size):
        subtitle_clips = []
        with open(srt_path, 'r') as f:
            lines = f.readlines()
            for i in range(0, len(lines), 4):
                index = lines[i].strip()
                start, end = lines[i + 1].strip().split(' --> ')
                print("Start:", start)
                print("End:", end)
                # Nettoyer les espaces et remplacer les virgules par des points
                start = start.strip().replace(',', '.')
                end = end.strip().replace(',', '.')
                print("Cleaned Start:", start)
                print("Cleaned End:", end)
                duration = float(end[:-3]) - float(start[:-3])
                text = lines[i + 2].strip()
                sub_clip = TextClip(text, fontsize=24, color='white', bg_color='black', size=video_size)
                sub_clip = sub_clip.set_position(("center", "bottom")).set_start(float(start[:-3])).set_duration(
                    duration)
                subtitle_clips.append(sub_clip)
        if subtitle_clips:
            return CompositeVideoClip(subtitle_clips)
        else:
            raise RuntimeError("VideoMaker : Subtitle ne peut pas faire d'opération dessus.")


def VideoEditorStart():
    CONTINUE = True
    while CONTINUE:
        titre_video = input("VideoMaker : Entrez le titre de la vidéo YouTube (ou tapez 'quit' pour quitter) : ")
        if titre_video.lower() == 'quit':
            print("VideoMaker : Programme quitté.")
            sys.exit()
        youtube_url = input("VideoMaker : Entrez le lien de la vidéo YouTube : ")
        start_time_input = input("VideoMaker : Entrez le temps de début (format MM:SS) : ")
        end_time_input = input("VideoMaker : Entrez le temps de fin (format MM:SS) : ")
        sous_title_input = input("VideoMaker : Entrez si vous voulez les sous titre (oui/non): ")

        video_editor = VideoEditor(titre_video.upper(), youtube_url, start_time_input, end_time_input, sous_title_input)
        if video_editor.editor() != False:
            CONTINUE = False
        else:
            CONTINUE = True
"""
VideoEditorStart()
"""