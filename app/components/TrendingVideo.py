import re

import requests
from bs4 import BeautifulSoup
import json

class TrendingVideo:
    def __init__(self):
        self.trending_videos = []
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
                                if 'expandedShelfContentsRenderer' in content['shelfRenderer']['content']:
                                    items = content['shelfRenderer']['content']['expandedShelfContentsRenderer']['items']
                                elif 'horizontalListRenderer' in content['shelfRenderer']['content']:
                                    items = content['shelfRenderer']['content']['horizontalListRenderer']['items']
                                else:
                                    print("Trending video not available")
                                for item in items:
                                    video_renderer = item.get('videoRenderer')
                                    if video_renderer:
                                        video_id = video_renderer['videoId']
                                        title = video_renderer['title']['runs'][0]['text']
                                        channel_name = video_renderer['shortBylineText']['runs'][0]['text']
                                        self.trending_videos.append((title, video_id, channel_name))
                                        print(f"Trending Video : Ajout video ({video_id}) : " + title + " Par " + channel_name)
        else:
            print("Erreur lors de la requête")

        return self.trending_videos

def get_video_length(video_url):
    response = requests.get(video_url)
    if response.status_code == 200:
        html_content = response.text
        # Utilisation d'expressions régulières pour extraire la durée de la vidéo
        match = re.search(r'lengthSeconds\":\"(\d+)', html_content)
        if match:
            length_seconds = int(match.group(1))
            minutes = length_seconds // 60
            seconds = length_seconds % 60
            return f"{minutes}:{seconds:02}"
        else:
            return "Erreur : durée non disponible"
    else:
        return "Erreur lors de la requête"



"""
trending = TrendingVideo()
videos = trending.get_trending_videos()

#Récupérer les vidéos id et les titles
for title, video_id in videos:
    print("Titre:", title)
    print("Video ID:", video_id)
    print()
"""