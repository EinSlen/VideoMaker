import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager as CM
from app.configuration import *


class TiktokUploader:
    def __init__(self, tiktok_link, len=10):
        self.driver = self.getChromeDriver()
        self.tiktok_link = tiktok_link
        self.len = len
        self.videos_link_feeds = []

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
        # Charger le fichier contenant les liens TikTok
        with open(self.tiktok_link, 'r') as file:
            liens = file.readlines()

        if len(liens) == 0:
            print('TikTokFeedsProviders : No link provided')

        for lien in liens:
            lien = lien.strip()
            if "tiktok.com" in lien:
                try:
                    self.driver.get(lien)

                    # Attendre que les vidéos soient chargées (ajustez la condition selon la page)
                    time.sleep(2)
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/video/']"))
                    )

                    # Trouver les liens vidéo
                    video_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/video/']")
                    for video_link in video_links:
                        len_video_feed = len(self.videos_link_feeds)
                        if(len_video_feed <= self.len):
                            href = video_link.get_attribute('href')
                            self.videos_link_feeds.append(href)
                            print(f"TikTokFeedsProviders: Nouveau lien video trouvé ({href}) [{len_video_feed}/{self.len}]")

                except Exception as e:
                    print(f"Erreur lors de la récupération des vidéos pour le lien {lien}: {e}")
        #self.videos_link_feeds.pop(-1)
        self.driver.close()
        self.driver.quit()
        print("TiktokUploader : Driver quit")

trending = TiktokUploader(TRENDING_FILE_PATH)
videos = trending.getProvideTiktokFeeds()
print(videos)