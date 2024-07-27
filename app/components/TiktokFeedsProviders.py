import time
import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager as CM
from app.configuration import *


class TiktokFeedsProviders:
    def __init__(self, tiktok_link, len=10):
        self.driver = self.getChromeDriver()
        self.tiktok_link = tiktok_link
        self.len = len
        self.videos_link_feeds = []
        self.extra_video_links = []

    def getChromeDriver(self):
        print("TikTokFeedsProviders : Ajout d'une chrome windows")
        os.system(
            f'cd "{CHROME_PATH_EXE}" && start chrome.exe --remote-debugging-port={CHROME_PORT} --user-data-dir="{CHROME_PATH_USER}"')
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "localhost:" + str(CHROME_PORT))
        options.add_argument('--remote-debugging-port=' + str(CHROME_PORT))
        options.add_argument('--user-data-dir=' + CHROME_PATH_USER)
        service = Service(executable_path=CM().install())
        driver = webdriver.Chrome(options=options, service=service)
        driver.switch_to.window(driver.current_window_handle)
        print("TikTokFeedsProviders : Ajout d'une chrome windows terminé.")
        return driver

    def getProvideTiktokFeeds(self):
        # Charger le fichier contenant les liens TikTok et YouTube
        with open(self.tiktok_link, 'r') as file:
            liens = file.readlines()

        if len(liens) == 0:
            print('TikTokFeedsProviders : file provided is empty')
            return None

        tiktok_links = []
        youtube_links = []

        # Séparer les liens TikTok et YouTube
        for lien in liens:
            lien = lien.strip()
            print(lien)
            if lien == "":
                break
            if "tiktok.com" in lien:
                tiktok_links.append(lien)
            elif "youtube.com" in lien:
                youtube_links.append(lien)

        print(tiktok_links)

        if len(tiktok_links) == 0 and len(youtube_links) == 0:
            print('TikTokFeedsProviders : No TikTok/Youtube links found')
            return None

        # Mélanger les liens TikTok/Youtube
        random.shuffle(tiktok_links)
        random.shuffle(youtube_links)

        # Traiter les liens TikTok mélangés
        for lien in tiktok_links:
            try:
                self.driver.get(lien)

                # Attendre que les vidéos soient chargées
                time.sleep(2)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/video/']"))
                )

                # Trouver les liens vidéo
                video_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/video/']")
                for video_link in video_links:
                    if len(self.videos_link_feeds) >= self.len:
                        break
                    href = video_link.get_attribute('href')
                    self.videos_link_feeds.append(href)
                    print(
                        f"TikTokFeedsProviders: Nouveau lien video trouvé ({href}) [{len(self.videos_link_feeds)}/{self.len}]")

            except Exception as e:
                print(f"Erreur lors de la récupération des vidéos pour le lien {lien}: {e}")

        # Vous pouvez ajouter une logique pour traiter les liens YouTube ici, si nécessaire
        # TODO: Implémenter le traitement des liens YouTube

        try:
            self.driver.close()
            self.driver.quit()
            print("TiktokUploader : Driver quit")
            return self.videos_link_feeds if len(self.videos_link_feeds) > 0 else None
        except Exception as e:
            if len(self.videos_link_feeds) > 0:
                return self.videos_link_feeds
            if "disconnected" not in str(e):
                print(f"Erreur lors de la suppression du driver : {e}")
                return None
    def getVideosLinkFeeds(self):
        with open(self.tiktok_link, 'r') as file:
            liens = file.readlines()

        start_collecting = False

        if len(liens) == 0:
            print('TikTokFeedsProviders : No link provided')

        for lien in liens:
            lien = lien.strip()
            if start_collecting:
                if "tiktok.com" in lien or "youtube.com" in lien:
                    self.extra_video_links.append(lien)
            elif lien == "":  # Commence à collecter après la ligne vide
                start_collecting = True

        return self.extra_video_links if len(self.extra_video_links) > 0 else None

"""
trending = TiktokFeedsProviders(TRENDING_FILE_PATH, 10) première option lien du fichier, deuxième nombre de vidéo récupérer
videos = trending.getProvideTiktokFeeds() #Récupérer les vidéos des tiktok des gens avec uniquement leur lien de profil
downloadVideo2part = trending.getVideosLinkFeeds() #récupérer les vidéos des tiktok / youtube de lien dans la deuxième partie du fichier pour download
print(videos)
print(downloadVideo2part)
"""
trending = TiktokFeedsProviders(TRENDING_FILE_PATH, 10)
print(trending.getProvideTiktokFeeds())