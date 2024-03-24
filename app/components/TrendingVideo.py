import requests
from bs4 import BeautifulSoup
import json

from app.configuration import LIB_PATH


class TrendingVideo:
    def get_trending_videos(self):
        url = "https://www.youtube.com/feed/trending"

        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            scripts = soup.find_all('script')

            for script in scripts:
                if 'var ytInitialData =' in str(script):
                    json_data_str = str(script).split('var ytInitialData =')[1].split(';</script>')[0]
                    json_data = json.loads(json_data_str)

                    # Trouver toutes les sections de la page des vidéos tendances
                    sections = \
                    json_data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content'][
                        'sectionListRenderer']['contents']
                    for section in sections:
                        contents = section.get('itemSectionRenderer', {}).get('contents', [])
                        for content in contents:
                            if 'shelfRenderer' in content:
                                items = content['shelfRenderer']['content']['expandedShelfContentsRenderer']['items']
                                for item in items:
                                    video_renderer = item.get('videoRenderer')
                                    if video_renderer:
                                        video_id = video_renderer['videoId']
                                        title = video_renderer['title']['runs'][0]['text']
                                        print("Titre:", title)
                                        print("Video ID:", video_id)
                                        print()

        else:
            print("Erreur lors de la requête")


trending = TrendingVideo()
trending.get_trending_videos()
