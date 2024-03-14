import os
import random
import string
import sys

from pytube import YouTube
from moviepy.video.VideoClip import TextClip, ColorClip
from moviepy.video.compositing.CompositeVideoClip import clips_array
from moviepy.editor import VideoFileClip, CompositeVideoClip
from moviepy.video.fx import all as vfx

VIDEOS_DIRECTORY = "videos/"
RESOLUTION_TIKTOK = (720, 720)
FPS_TIKTOK = 60
EDITED_PATH = "edited/"

class VideoEditor:
    def __init__(self, titre_video='', youtube_url=None, start_time_input=0, end_time_input=30, sous_title="non"):
        self.titre_video = titre_video
        self.youtube_url = youtube_url
        self.start_time_input = start_time_input
        self.end_time_input = end_time_input
        self.PATH = ''
        self.VIDEO_PATH = ''
        if sous_title.lower() == "oui":
            self.sous_title = True
        else:
            self.sous_title = False

    def generate_random_filename(self):
        path = ''.join(random.choices(string.ascii_letters.upper() + string.digits.upper(), k=12))
        self.PATH = path
        return path

    def delete_file(self, file_path):
        if os.path.exists(file_path) and file_path != '':
            os.remove(file_path)
            print(f"Fichier supprimé : {file_path}")
        else:
            print(f"Le fichier n'existe pas : {file_path}")

    def download_youtube_video(self, output_path='.'):
        yt = YouTube(self.youtube_url)
        print("Vidéo en cours de téléchargement...")
        video_stream = yt.streams.filter(file_extension='mp4', res='720p').first()

        if video_stream:
            video_stream.download(output_path)
            print("Vidéo téléchargée avec succès !")
            self.VIDEO_PATH = os.path.join(output_path, video_stream.default_filename)
            return self.VIDEO_PATH
        else:
            raise RuntimeError("Votre vidéo n'est pas connu de l'API")
            return None

    def merge_videos(self, video_path1, video_path2, output_path, start_time, end_time):
        clip1 = VideoFileClip(video_path1).subclip(start_time, end_time)
        clip2 = VideoFileClip(video_path2).subclip(start_time, end_time)

        # Couper le son de la deuxième vidéo
        clip2 = clip2.set_audio(None)

        # Ajuster la résolution de la deuxième vidéo pour correspondre à la première
        clip2 = clip2.resize(height=clip1.h)

        print("Merge des vidéos... ")
        final_clip = clips_array([[clip1], [clip2]])

        final_clip = final_clip.resize(RESOLUTION_TIKTOK)

        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=FPS_TIKTOK)

        clip1.close()
        clip2.close()
        final_clip.close()

        self.add_text_to_video(output_path, EDITED_PATH + self.PATH + "F.mp4", self.titre_video)

        print("Merge des vidéos avec succès ! ")

    def add_text_to_video(self, input_video_path, output_video_path, title):
        try:
            if input_video_path is None or not os.path.exists(input_video_path):
                raise ValueError("Erreur : Le chemin de la vidéo d'entrée n'est pas valide.")

            video_clip = VideoFileClip(input_video_path)

            # Ajouter du texte à la vidéo
            text_clip = TextClip(title, fontsize=70, color='black', font='Helvetica-Bold',
                                 size=(video_clip.size[0] // 4, None))
            text_clip = text_clip.set_pos(('center', 'center')).set_duration(video_clip.duration)

            background_clip = ColorClip(size=(text_clip.w, text_clip.h), color=(255, 255, 255))
            background_clip = background_clip.set_pos(('center', 'center')).set_duration(video_clip.duration)

            # Fusionner la vidéo et le texte
            final_clip = CompositeVideoClip([video_clip, background_clip, text_clip])

            # Écrire la vidéo résultante
            final_clip.write_videofile(output_video_path, codec='libx264', audio_codec='aac', fps=video_clip.fps)

            # Fermer les ressources
            final_clip.close()

            self.delete_file(input_video_path)

        except Exception as e:
            self.delete_file(os.path.join(self.PATH, "TEMP_MPY_wvf_snd.mp4"))
            self.delete_file(self.VIDEO_PATH)
            print(f"Erreur : {e}")

    def main(self):
        try:
            start_time = sum(x * int(t) for x, t in zip([60, 1], self.start_time_input.split(":")))
            end_time = sum(x * int(t) for x, t in zip([60, 1], self.end_time_input.split(":")))

            #TODO Si une personne n'a pas d'abonnement mettre cette restriction
            """
            if (end_time - start_time) > 30:
                raise ValueError("Erreur: Vous n'avez pas le droit aussi longtemps !")
            """

            # Télécharger la vidéo YouTube
            downloaded_video_path = self.download_youtube_video()

            if downloaded_video_path is None:
                print("Le téléchargement de la vidéo a échoué.")
                return

            # Choisir aléatoirement une vidéo du répertoire "videos"
            random_video = random.choice(os.listdir(VIDEOS_DIRECTORY))
            random_video_path = os.path.join(VIDEOS_DIRECTORY, random_video)

            # Extraire les clips nécessaires des vidéos
            random_filename = self.generate_random_filename()
            output_path = os.path.join('edited', f"{random_filename}.mp4")

            # Ajouter le titre à la vidéo
            self.merge_videos(downloaded_video_path, random_video_path, output_path, start_time, end_time)

            # Supprimer les fichiers temporaires
            self.delete_file(self.VIDEO_PATH)

            print(f"La vidéo résultante a été enregistrée à : {EDITED_PATH}{self.PATH}F.mp4")

        except Exception as e:
            self.delete_file(os.path.join(self.PATH, "TEMP_MPY_wvf_snd.mp4"))
            self.delete_file(self.VIDEO_PATH)
            print(f"Erreur : {e}")



if __name__ == "__main__":
    titre_video = input("Entrez le titre de la vidéo YouTube (ou tapez 'quit' pour quitter) : ")
    if titre_video.lower() == 'quit':
        print("Programme quitté.")
        sys.exit()
    youtube_url = input("Entrez le lien de la vidéo YouTube : ")
    start_time_input = input("Entrez le temps de début (format MM:SS) : ")
    end_time_input = input("Entrez le temps de fin (format MM:SS) : ")
    sous_title_input = input("Entrez si vous voulez les sous titre (oui/non): ")

    video_editor = VideoEditor(titre_video.upper(), youtube_url, start_time_input, end_time_input, sous_title_input)
    video_editor.main()
