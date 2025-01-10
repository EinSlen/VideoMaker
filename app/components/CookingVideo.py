import os

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.fx.resize import resize
from pytubefix import YouTube #FIX YOUTUBE 403 forbidden
import time
from moviepy.video.fx.fadein import fadein

from app.components.TrendingVideo import TrendingVideo


class CookingVideo:
    def __init__(self):
        self.keywords = [
            # Mots-clés en français
            "cuisine", "recette", "recettes", "cuisinier", "gastronomie", "culinaire",
            "nourriture", "repas", "dîner", "déjeuner", "petit-déjeuner",
            "cuisson", "rôtir", "griller", "mijoter", "bouillir", "poêler", "frire",
            "dessert", "pâtisserie", "gâteau", "plat", "entrée", "soupe", "salade", "pain", "pizza", "sandwich", "quiche", "tarte",
            "française", "italienne", "asiatique", "indienne", "mexicaine", "méditerranéenne", "végétarienne", "végan",
            "four", "poêle", "casserole", "mixeur", "robot", "blender", "autocuiseur", "friteuse",
            "poulet", "poisson", "viande", "légumes", "pâtes", "riz", "fromage", "chocolat", "fruits", "œufs", "farine", "lait",
            # Mots-clés en anglais
            "cooking", "recipe", "recipes", "chef", "culinary", "gastronomy",
            "food", "meal", "dish", "dinner", "lunch", "breakfast", "brunch",
            "baking", "roasting", "grilling", "simmering", "boiling", "frying", "sautéing",
            "dessert", "pastry", "cake", "dish", "appetizer", "soup", "salad", "bread", "pizza", "sandwich", "tart", "pie",
            "French", "Italian", "Asian", "Indian", "Mexican", "Mediterranean", "vegetarian", "vegan",
            "oven", "pan", "pot", "mixer", "blender", "food processor", "air fryer", "slow cooker",
            "chicken", "fish", "meat", "vegetables", "pasta", "rice", "cheese", "chocolate", "fruits", "eggs", "flour", "milk"
        ]

        self.already_video = []

        self.cooking_video()

    def on_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100
        progress_bar = "[" + "-" * int(percentage / 2) + " " * (50 - int(percentage / 2)) + "]"
        print("\rVideoMaker : Téléchargement en cours... {} ({:.2f}% complet)".format(progress_bar, percentage), end='',
              flush=True)

    def download_video(self, video_id):
        print(f"VideoMaker : Cette vidéo va être télécharger : {video_id}...")
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        yt = YouTube(youtube_url, on_progress_callback=self.on_progress)
        video_stream = yt.streams.filter(file_extension='mp4', res='720p').first()

        if video_stream:
            output_path = "downloads"
            os.makedirs(output_path, exist_ok=True)
            file_path = video_stream.download(output_path, filename=f"{video_id}.mp4")
            print("\nVidéo téléchargée avec succès !")
            return file_path
        else:
            print("Impossible de télécharger la vidéo.")
            return None

    def format_for_tiktok(self, file_path):
        try:
            output_path = "tiktok_videos"
            os.makedirs(output_path, exist_ok=True)
            output_file = os.path.join(output_path, f"tiktok_{os.path.basename(file_path)}")
            clip = VideoFileClip(file_path)

            # Redimensionner la vidéo pour le format TikTok (1080x1920)
            clip = resize(clip, height=1920, width=1080)

            # Couper la vidéo si elle dépasse 60 secondes
            clip = clip.subclip(0, min(clip.duration, 60))

            # Ajouter une transition simple pour éviter l'algorithme de détection
            clip = fadein(clip, duration=1)

            # Exporter la vidéo
            clip.write_videofile(output_file, codec="libx264", audio_codec="aac")
            print(f"Vidéo formatée pour TikTok : {output_file}")
            return output_file
        except Exception as e:
            print("Error: " + str(e))

    def video_create(self, video):
        try:
            file_path = self.download_video(video[0][1])
            if file_path is not None:
                self.format_for_tiktok(file_path)
            else:
                print("Impossible de télécharger la vidéo")
        except Exception as e:
            print("Erreur" + str(e) + " Try: " + video[0][1])
            self.cooking_video()

    def cooking_video(self):
        videos_cooking = []
        trending_videos = TrendingVideo()
        videos = trending_videos.get_trending_videos()
        for title, video_id, channel_name in videos:
            if any(keyword.lower() in title.lower() for keyword in self.keywords) or \
                    any(keyword.lower() in channel_name.lower() for keyword in self.keywords):
                if video_id not in self.already_video:
                    videos_cooking.append((title, video_id, channel_name))
                    self.already_video.append(video_id)
                    print(self.already_video)
                    break
                else:
                    print("Already video: " + video_id)

        if len(videos_cooking) > 0:
            self.video_create(videos_cooking)
        else:
            time.sleep(50000)
            self.cooking_video()

cooking = CookingVideo()
cooking.cooking_video()