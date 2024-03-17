import os
import random
import string
import sys
import wave

import numpy as np
from pytube import YouTube
from moviepy.video.VideoClip import TextClip, ColorClip
from moviepy.video.compositing.CompositeVideoClip import clips_array
from moviepy.editor import VideoFileClip, CompositeVideoClip
import speech_recognition as sr
from pocketsphinx import AudioFile, get_model_path

VIDEOS_DIRECTORY = "videos/"
RESOLUTION_TIKTOK = (720, 720)
FPS_TIKTOK = 60
EDITED_PATH = "edited/"
LIBRARY_PATH = "./app/lib/"
PBMM = LIBRARY_PATH + 'output_graph.pbmm'
SCORER = LIBRARY_PATH + 'kenlm.scorer'
FRENCH_DICT = LIBRARY_PATH + 'fr.dict'
LANGUAGE = "fr-FR"

class VideoEditor:
    def __init__(self, titre_video='', youtube_url=None, start_time_input=0, end_time_input=30, sous_title="non"):
        self.titre_video = titre_video
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
            print(f"Le fichier n'existe pas : {file_path}")

    def download_youtube_video(self, output_path='.'):
        print("Vidéo en cours de téléchargement...")
        yt = YouTube(self.youtube_url)
        video_stream = yt.streams.filter(file_extension='mp4', res='720p').first()

        if video_stream:
            video_stream.download(output_path)
            print("Vidéo téléchargée avec succès !")
            self.VIDEO_PATH = os.path.join(output_path, video_stream.default_filename)
        else:
            raise RuntimeError("Votre vidéo n'est pas connu de l'API")

    def add_subtitle_to_video(self, input_video_path):
        try:
            if input_video_path is None or not os.path.exists(input_video_path):
                raise ValueError(f"Erreur : Le chemin de la vidéo d'entrée n'est pas valide. -> {input_video_path}")

            # Extraire l'audio de la vidéo
            temp_audio_path = "temp_audio.wav"
            video_clip = VideoFileClip(input_video_path)
            video_clip.audio.write_audiofile(temp_audio_path)


            print("VideoMaker: Transcription de la parole en texte...")

            # Transcrire l'audio en texte
            transcript = self.transcribe_audio(temp_audio_path)

            # Supprimer le fichier audio temporaire
            self.delete_file(temp_audio_path)

            print("VideoMaker: Transcription terminée.")

            if transcript:
                # Diviser le texte transcrit en phrases
                sentences = transcript.split('. ')

                print("VideoMaker: Ajout des text en sous titre")

                # Créer des clips texte pour chaque phrase
                text_clips = []
                for sentence in sentences:
                    text_clip = TextClip(sentence, fontsize=20, color='white', font='Arial', bg_color='black')
                    text_clip = text_clip.set_position(('center', 'bottom')).set_duration(video_clip.duration)
                    text_clips.append(text_clip)

                # Combinez les clips texte avec le clip vidéo original
                video_with_subtitles = CompositeVideoClip([video_clip] + text_clips)

                return video_with_subtitles

            else:
                print("La transcription audio a échoué.")
                return video_clip

        except Exception as e:
            if self.titre_video != '':
                self.delete_file(os.path.join(self.titre_video, "TEMP_MPY_wvf_snd.mp4"))
            else:
                self.delete_file(os.path.join(self.PATH, "TEMP_MPY_wvf_snd.mp4"))
            self.delete_file(self.VIDEO_PATH)
            print(f"Erreur : {e}")

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
            RuntimeError(f"Erreur lors de la transcription audio : {e}")

    def merge_videos(self, video_path2, output_path, start_time, end_time):
        clip1 = VideoFileClip(self.VIDEO_PATH).subclip(start_time, end_time)
        clip2 = VideoFileClip(video_path2).subclip(start_time, end_time)

        clip2 = clip2.set_audio(None)
        clip2 = clip2.resize(height=clip1.h)

        print("Merge des vidéos... ")
        final_clip = clips_array([[clip1], [clip2]])

        final_clip = final_clip.resize(RESOLUTION_TIKTOK)

        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=FPS_TIKTOK)

        final_clip.close()

        clip_with_text = self.add_text_to_video(output_path)

        if self.sous_title:
            print("VideoMaker : Ajout des sous titres...")
            CompositeVideoClip([clip_with_text, self.add_subtitle_to_video(output_path)]).write_videofile(self.add_suffix_to_filename(output_path, EDITED_PATH), codec='libx264', audio_codec='aac')
        else:
            clip_with_text.write_videofile(self.add_suffix_to_filename(output_path, EDITED_PATH), codec='libx264',
                                   audio_codec='aac')


        clip1.close()
        clip2.close()
        clip_with_text.close()

        self.delete_file(output_path)

        print("Merge des vidéos avec succès ! ")

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
            print(f"Erreur : {e}")

    def main(self):
        try:
            start_time = sum(x * int(t) for x, t in zip([60, 1], self.start_time_input.split(":")))
            end_time = sum(x * int(t) for x, t in zip([60, 1], self.end_time_input.split(":")))

            # Télécharger la vidéo YouTube
            self.download_youtube_video()

            if self.VIDEO_PATH is None:
                print("VideoMaker : Le téléchargement de la vidéo a échoué.")
                return False

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
                    print("Changement du path : ", output_path)
                else:
                    CONTINUE = False

            output_path = self.add_suffix_to_filename(output_path, "./")

            # Ajouter le titre à la vidéo
            self.merge_videos(random_video_path, output_path, start_time, end_time)

            # Supprimer les fichiers temporaires
            self.delete_file(self.VIDEO_PATH)

            print(f"VideoMaker: La vidéo résultante a été enregistrée à : {self.add_suffix_to_filename(output_path, EDITED_PATH)}")

            return True

        except Exception as e:
            self.delete_file(os.path.join(self.PATH, "TEMP_MPY_wvf_snd.mp4"))
            self.delete_file(self.VIDEO_PATH)
            print(f"Erreur : {e}")
            return False

def start():
    CONTINUE = True
    while CONTINUE:
        titre_video = input("Entrez le titre de la vidéo YouTube (ou tapez 'quit' pour quitter) : ")
        if titre_video.lower() == 'quit':
            print("Programme quitté.")
            sys.exit()
        youtube_url = input("Entrez le lien de la vidéo YouTube : ")
        start_time_input = input("Entrez le temps de début (format MM:SS) : ")
        end_time_input = input("Entrez le temps de fin (format MM:SS) : ")
        sous_title_input = input("Entrez si vous voulez les sous titre (oui/non): ")

        video_editor = VideoEditor(titre_video.upper(), youtube_url, start_time_input, end_time_input, sous_title_input)
        CONTINUE = not video_editor.main()

start()
