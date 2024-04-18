from app.components.TiktokUploader import TiktokUploader
from app.components.TrendingVideo import TrendingVideo
from app.components.VideoEditor import VideoEditor
from app.configuration import VIDEOS_LIMIT_FOR_YT_TO_TK


class YoutubeForTiktok:
    def __init__(self):
        self.videos_with_title = []
        self.videos_with_format_tiktok = []

    def get_videos_with_title(self):
        trending_videos = TrendingVideo()
        videos = trending_videos.get_trending_videos()
        self.videos_with_title = videos

    def set_videos_to_format_tiktok(self):
        for title, video_uid in self.videos_with_title:
            video_editor = VideoEditor(title.upper(), "https://www.youtube.com/watch?v="+video_uid, str(0), str(60),
                                       'non')
            path_video_edited = video_editor.editor()
            self.videos_with_format_tiktok.append((path_video_edited, title))

    def upload_to_tiktok(self):
        TiktokUploader(self.videos_with_format_tiktok)
        #tiktok_upload.upload()

    def start(self):
        self.get_videos_with_title()
        self.videos_with_title = self.videos_with_title[:VIDEOS_LIMIT_FOR_YT_TO_TK]
        self.set_videos_to_format_tiktok()
        self.upload_to_tiktok()


youtubefortiktok = YoutubeForTiktok()
youtubefortiktok.start()