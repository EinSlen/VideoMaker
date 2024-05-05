import re
import threading

import requests
from bs4 import BeautifulSoup

from app.components.TiktokUploader import TiktokUploader
from app.components.TrendingVideo import TrendingVideo, get_video_length
from app.components.VideoEditor import VideoEditor
from app.configuration import VIDEOS_LIMIT_FOR_YT_TO_TK
from queue import Queue

class YoutubeForTiktok:
    def __init__(self):
        self.videos_with_title = []
        self.videos_with_format_tiktok = []
        self.videos_with_yt_restriction = []
        self.nb_count_videos_use = 0

    def get_videos_with_title(self):
        trending_videos = TrendingVideo()
        videos = trending_videos.get_trending_videos()
        self.videos_with_title = videos

    def process_video_editing(self, title, video_uid, output_queue):
        youtube_url = "https://www.youtube.com/watch?v=" + video_uid
        video_duration_youtube = get_video_length(youtube_url)

        if "Erreur" not in video_duration_youtube:
            minutes, seconds = map(int, video_duration_youtube.split(':'))
            total_video_seconds = minutes * 60 + seconds

            segment_length = 60  # Durée de chaque segment en secondes
            total_segments = total_video_seconds // segment_length
            remainder_seconds = total_video_seconds % segment_length
            if remainder_seconds >= 30:
                total_segments += 1

            for part in range(total_segments):
                start_time = part * segment_length
                end_time = min((part + 1) * segment_length, total_video_seconds)

                video_editor = VideoEditor(title + " - Part " + str(part + 1), youtube_url,
                                           str(start_time), str(end_time), 'oui')
                path_video_edited = video_editor.editor()
                output_queue.put(path_video_edited)

            if remainder_seconds >= 30:
                video_editor = VideoEditor(title + " - Part final", youtube_url,
                                           str(total_video_seconds - remainder_seconds), str(total_video_seconds),
                                           'oui')
                path_video_edited = video_editor.editor()
                output_queue.put(path_video_edited)
        else:
            video_editor = VideoEditor(title, youtube_url, str(0), str(60), 'oui')
            path_video_edited = video_editor.editor()
            output_queue.put(path_video_edited)

    def set_videos_to_format_tiktok(self):
        global nb_video
        try:
            print(f"YoutubeForTiktok: Editor for : {self.videos_with_yt_restriction}")
            nb_video = -1
            for title, video_uid, channel_name in self.videos_with_yt_restriction:
                nb_video +=1
                output_queue = Queue()
                edit_thread = threading.Thread(target=self.process_video_editing,
                                               args=(title, video_uid, output_queue))
                edit_thread.start()
                edit_thread.join()

                path_video_edited = output_queue.get()
                if "C:\\" in path_video_edited:
                    self.videos_with_format_tiktok.append((path_video_edited, title, channel_name))
                    del self.videos_with_yt_restriction[nb_video]
                else:
                    RuntimeError("YoutubeForTiktok: Aucun chemin de vidéo trouvé.")
                    del self.videos_with_yt_restriction[nb_video]
        except Exception as e:
            print(f"YoutubeForTiktok: Une erreur est survenue dans le vidéo editor :")
            print(e)
            if 'age restricted' in str(e) or 'WinError' in str(e) or 'Errno' in str(e) or 'disconnect' in str(e):
                print("YoutubeForTiktok: -> Nouvelle vidéo en cours.")
                if (self.nb_count_videos_use+VIDEOS_LIMIT_FOR_YT_TO_TK) < len(self.videos_with_title):
                    self.nb_count_videos_use += 1
                    del self.videos_with_yt_restriction[nb_video]
                    self.videos_with_yt_restriction.append(self.videos_with_title[VIDEOS_LIMIT_FOR_YT_TO_TK+self.nb_count_videos_use])
                    #self.videos_with_yt_restriction = [self.videos_with_title[VIDEOS_LIMIT_FOR_YT_TO_TK+self.nb_count_videos_use]]
                    #self.videos_with_yt_restriction = self.videos_with_yt_restriction[0]
                    print("YoutubeForTiktok: Reload videos format tiktok.")
                    self.set_videos_to_format_tiktok()
                else:
                    print("YoutubeForTiktok: Aucune vidéo n'est disponible.")

    def upload_to_tiktok(self):
        TiktokUploader(self.videos_with_format_tiktok)
        #tiktok_upload.upload()

    def start(self):
        self.get_videos_with_title()
        self.videos_with_yt_restriction = self.videos_with_title[:VIDEOS_LIMIT_FOR_YT_TO_TK]
        self.set_videos_to_format_tiktok()
        self.upload_to_tiktok()

"""
Utilisation (prend une vidéo tendance et la met sur youtube)
youtubefortiktok = YoutubeForTiktok()
youtubefortiktok.start()
"""
