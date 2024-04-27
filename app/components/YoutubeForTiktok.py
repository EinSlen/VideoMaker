from app.components.TiktokUploader import TiktokUploader
from app.components.TrendingVideo import TrendingVideo
from app.components.VideoEditor import VideoEditor
from app.configuration import VIDEOS_LIMIT_FOR_YT_TO_TK


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

    def set_videos_to_format_tiktok(self):
        global nb_video
        try:
            print(f"YoutubeForTiktok: Editor for : {self.videos_with_yt_restriction}")
            nb_video = -1
            for title, video_uid in self.videos_with_yt_restriction:
                nb_video +=1
                video_editor = VideoEditor(title, "https://www.youtube.com/watch?v="+video_uid, str(0), str(60),
                                           'non')
                path_video_edited = video_editor.editor()
                if "C:\\" in path_video_edited:
                    self.videos_with_format_tiktok.append((path_video_edited, title))
                    del self.videos_with_yt_restriction[nb_video]
                else:
                    RuntimeError("YoutubeForTiktok: Aucun chemin de vidéo trouvé.")
                    del self.videos_with_yt_restriction[nb_video]
        except Exception as e:
            print(f"YoutubeForTiktok: Une erreur est survenue dans le vidéo editor :")
            print(e)
            if 'age restricted' in str(e) or 'WinError' in str(e):
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