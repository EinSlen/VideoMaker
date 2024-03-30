import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager as CM
from selenium.webdriver.chrome.service import Service
from app.configuration import *
from selenium.common.exceptions import NoSuchWindowException
import subprocess

#cd C:\Program Files\Google\Chrome\Application
#chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\Users\Valentin\Desktop\VideoMaker\app\localhost"

"""
driver.get('https://www.tiktok.com/login')
ActionChains(driver).key_down(Keys.CONTROL).send_keys(
    '-').key_up(Keys.CONTROL).perform()
ActionChains(driver).key_down(Keys.CONTROL).send_keys(
    '-').key_up(Keys.CONTROL).perform()
print('Waiting 50s for manual login...')
time.sleep(5)
driver.get('https://www.tiktok.com/creator-center/upload?lang=fr')
time.sleep(5)
"""

class TiktokUploader:
    def __init__(self, list_video):
        self.driver = None
        self.video_path_list = list_video
        self.addChrome()

        for video_path, title in self.video_path_list:
            self.upload(video_path, title)

    def login(self):
        print("TiktokUploader : Tu dois te connecter !")
        self.driver.get('https://www.tiktok.com/login')
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys(
            '-').key_up(Keys.CONTROL).perform()
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys(
            '-').key_up(Keys.CONTROL).perform()
        print('TiktokUploader : Attente de 50s pour une connection manuel...')
        time.sleep(50)
    def check_exists_by_xpath(self, xpath):
        try:
            self.driver.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return False

        return True

    def addChrome(self):
        print("TiktokUploader : Ajout d'une chrome windows")
        options = webdriver.ChromeOptions()
        options.add_argument('--remote-debugging-port=' + str(CHROME_PORT))
        options.add_argument('--user-data-dir='+CHROME_PATH_USER)
        service = Service(executable_path=CM().install())
        self.driver = webdriver.Chrome(options=options, service=service)


    def upload(self, video_path, title):
            try:
                """
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                    (By.XPATH, "//input[@type='file']"))).send_keys(
                    video_path)
                """

                self.driver.get('https://www.tiktok.com/creator-center/upload?lang=fr')
                self.driver.implicitly_wait(5)

                iframe = self.driver.find_element(By.XPATH, "//iframe[@data-tt='Upload_index_iframe']")
                self.driver.switch_to.frame(iframe)

                file_uploader = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
                file_uploader.send_keys(video_path)

                self.driver.switch_to.default_content()

                iframe_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//iframe[@data-tt='Upload_index_iframe']"))
                )

                self.driver.switch_to.frame(iframe_element)

                caption = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-friends"))
                )

                self.driver.implicitly_wait(10)
                ActionChains(self.driver).move_to_element(caption).click(
                    caption).perform()

                ActionChains(self.driver).click()
                #ActionChains(self.driver).key_down(Keys.CONTROL).send_keys(
                #    'v').key_up(Keys.CONTROL).perform()

                time.sleep(0.5)

                ActionChains(self.driver).send_keys(title + " - ").perform()

                with open(CAPTION, "r") as f:
                    tags = [line.strip() for line in f]
                for tag in tags:
                    ActionChains(self.driver).send_keys(tag).perform()
                    time.sleep(1.5)
                    ActionChains(self.driver).send_keys(Keys.RETURN).perform()
                    time.sleep(0.5)

                time.sleep(2)
                self.driver.execute_script("window.scrollTo(150, 300);")

                post = WebDriverWait(self.driver, 100).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, 'button.css-y1m958')))

                post.click()
                print("TiktokUploader : La vidéo de " + title + " à été upload.")
                #self.driver.get('https://www.tiktok.com/creator-center/upload?lang=fr')

                """
                if check_exists_by_xpath(driver, '//*[@id="portal-container"]/div/div/div[1]/div[2]'):
                    reupload = WebDriverWait(driver, 100).until(EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="portal-container"]/div/div/div[1]/div[2]')))
        
                    reupload.click()
                else:
                    print('Unknown error cooldown')
                    while True:
                        time.sleep(600)
                        post.click()
                        time.sleep(15)
                        if check_exists_by_xpath(driver, '//*[@id="portal-container"]/div/div/div[1]/div[2]'):
                            break
        
                if check_exists_by_xpath(driver, '//*[@id="portal-container"]/div/div/div[1]/div[2]'):
                    reupload = WebDriverWait(driver, 100).until(EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="portal-container"]/div/div/div[1]/div[2]')))
                    reupload.click()
        
                time.sleep(1)
                """
            except NoSuchWindowException as e:
                print("TiktokUpload : " + e)
                self.addChrome()

path_video = """C:\\Users\Valentin\Desktop\VideoMaker\\app\components\TEST (3).mp4"""
tiktokuploader = TiktokUploader([(path_video, "TEST")])
# ================================================================
# Here is the path of the video that you want to upload in tiktok.
# Plese edit the path because this is different to everyone.
#upload(r"C:\Users\Valentin\Desktop\VideoMaker\app\components\TEST (3).mp4")
# ================================================================
