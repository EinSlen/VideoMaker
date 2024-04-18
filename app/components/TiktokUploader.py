import sys
import time
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
from selenium.common.exceptions import NoSuchWindowException, TimeoutException
from requests.exceptions import ConnectionError

# cd C:\Program Files\Google\Chrome\Application
# chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\Users\Valentin\Desktop\VideoMaker\app\localhost"

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
        self.driver = self.addChrome()
        self.video_path_list = list_video

        for video_path, title in self.video_path_list:
            print("TiktokUploader : ", video_path, title)
            self.upload(video_path, title)
            self.video_path_list.pop(0)
            if len(self.video_path_list) >= 1:
                self.driver.get('https://www.tiktok.com/creator-center/upload?lang=fr')

        self.driver.close()
        self.driver.quit()
        print("TiktokUploader : Driver quit")

    def login(self):
        print("TiktokUploader : Tu dois te connecter !")
        print("TiktokUpload : Redirection -> creator-center/login")
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
        os.system(
            f'cd "{CHROME_PATH_EXE}" && start chrome.exe --remote-debugging-port={CHROME_PORT} --user-data-dir="{CHROME_PATH_USER}"')
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "localhost:" + str(CHROME_PORT))
        options.add_argument('--remote-debugging-port=' + str(CHROME_PORT))
        options.add_argument('--user-data-dir=' + CHROME_PATH_USER)
        service = Service(executable_path=CM().install())
        self.driver = webdriver.Chrome(options=options, service=service)
        print("TiktokUploader : Ajout d'une chrome windows terminé.")
        return self.driver

    def upload(self, video_path, title):
        try:
            """
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, "//input[@type='file']"))).send_keys(
                video_path)
            """
            print("TiktokUpload : Redirection -> creator-center/upload")
            self.driver.get('https://www.tiktok.com/creator-center/upload?lang=fr')
            self.driver.implicitly_wait(5)

            iframe = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//iframe[@data-tt='Upload_index_iframe']")))
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

            """
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.videoInfo"))
            )
            """
            self.driver.implicitly_wait(10)
            ActionChains(self.driver).move_to_element(caption).click(
                caption).perform()

            ActionChains(self.driver).move_to_element(caption).click()
            # ActionChains(self.driver).key_down(Keys.CONTROL).send_keys(
            #    'v').key_up(Keys.CONTROL).perform()

            time.sleep(0.5)

            print("TiktokUpload : Ajout du titre : " + title)
            ActionChains(self.driver).send_keys(title + " - ").perform()

            with open(CAPTION, "r") as f:
                tags = [line.strip() for line in f]
                print("TiktokUpload : Récupération des tags : " + str(tags))

            for tag in tags:
                print("TiktokUpload : Ajout du tag : " + tag)
                ActionChains(self.driver).move_to_element(caption).click(
                    caption).perform()
                ActionChains(self.driver).send_keys(tag).perform()
                time.sleep(1.5)
                ActionChains(self.driver).send_keys(Keys.RETURN).perform()
                time.sleep(0.5)

            self.driver.implicitly_wait(2)
            self.driver.execute_script("window.scrollTo(150, 300);")

            post = WebDriverWait(self.driver, 100).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'button.css-y1m958')))

            while post.value_of_css_property("background-color") != 'rgba(254, 44, 85, 1)':
                print("TiktokUpload : La vidéo n'est pas encore chargé...")
                time.sleep(1)

            post.click()
            print("TiktokUploader : La vidéo de " + title + " à été upload.")
            time.sleep(0.5)

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
        except (NoSuchWindowException, NoSuchElementException, TimeoutException, ConnectionError, Exception) as e:
            if isinstance(e, NoSuchWindowException):
                self.driver.close()
                self.driver.quit()
                self.addChrome()
                print("TiktokUpload : Aucune chrome window, relancement !")
            elif isinstance(e, NoSuchElementException):
                self.login()
                print("TiktokUpload : Aucun Element...")
            elif isinstance(e, TimeoutException) or isinstance(e, ConnectionError):
                self.upload(video_path, title)
            else:
                print("TiktokUpload : Une autre exception a été levée, fermeture...")
                print(e)
                self.driver.close()
                self.driver.quit()
                sys.exit()
            self.upload(video_path, title)


"""
Utilisation : 
path_video = "C:\\Users\\Valentin\\Desktop\\VideoMaker\\app\\components\\TEST (3).mp4"
tiktokuploader = TiktokUploader([(path_video, "TEST")])
"""