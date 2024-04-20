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
    def __init__(self, list_video, tags=None):
        self.driver = self.getChromeDriver()
        self.video_path_list = list_video
        self.tentative_upload = 0
        self.tags = tags

        for video_path, title in self.video_path_list:
            print("TiktokUploader : Vidéo trouvé. ", video_path, title)
            self.upload(video_path, title)
            print("TiktokUploader : Video upload complete")
            self.video_path_list.pop()
            self.tentative_upload = 0

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

    def delete_file(self, file_path):
        if os.path.exists(file_path) and file_path != '':
            os.remove(file_path)
            print(f"Fichier supprimé : {file_path}")
        else:
            print(f"VideoMaker : Le fichier n'existe pas : {file_path}")

    def getChromeDriver(self):
        print("TiktokUploader : Ajout d'une chrome windows")
        os.system(
            f'cd "{CHROME_PATH_EXE}" && start chrome.exe --remote-debugging-port={CHROME_PORT} --user-data-dir="{CHROME_PATH_USER}"')
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "localhost:" + str(CHROME_PORT))
        options.add_argument('--remote-debugging-port=' + str(CHROME_PORT))
        options.add_argument('--user-data-dir=' + CHROME_PATH_USER)
        service = Service(executable_path=CM().install())
        driver = webdriver.Chrome(options=options, service=service)
        driver.switch_to.window(driver.current_window_handle)
        print("TiktokUploader : Ajout d'une chrome windows terminé.")
        return driver

    def upload(self, video_path, title):
        try:
            """
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, "//input[@type='file']"))).send_keys(
                video_path)
            """
            print("TiktokUpload : Redirection -> creator-center/upload")
            self.driver.get('https://www.tiktok.com/creator-center/upload?lang=fr')
            self.driver.switch_to.window(self.driver.current_window_handle)
            time.sleep(5)

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

            #afficher la page en cours
            #print(self.driver.page_source)

            description_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".public-DraftEditor-content"))
            )

            description_element.click()

            description_element.send_keys(title + " - ")

            """
            caption = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-friends"))
            )
      
            #WebDriverWait(self.driver, 15).until(
            #    EC.presence_of_element_located((By.CSS_SELECTOR, "div.videoInfo"))
            #)
            
            self.driver.implicitly_wait(10)
            ActionChains(self.driver).move_to_element(caption).click(
                caption).perform()

            ActionChains(self.driver).move_to_element(caption).click()
            # ActionChains(self.driver).key_down(Keys.CONTROL).send_keys(
            #    'v').key_up(Keys.CONTROL).perform()
            """

            time.sleep(0.5)

            print("TiktokUpload : Ajout du titre : " + title)
            """
            ActionChains(self.driver).send_keys(title + " - ").perform()
            """

            if self.tags is None:
                with open(CAPTION, "r") as f:
                    tags = [line.strip() for line in f]
                    print("TiktokUpload : Récupération des tags : " + str(tags))
                self.tags = tags

            for tag in self.tags:
                print("TiktokUpload : Ajout du tag : " + tag)
                """
                ActionChains(self.driver).move_to_element(caption).click(
                    caption).perform()
                """
                ActionChains(self.driver).move_to_element(description_element).click(
                    description_element).perform()
                ActionChains(self.driver).send_keys(tag).perform()
                time.sleep(1.5)
                ActionChains(self.driver).send_keys(Keys.RETURN).perform()
                time.sleep(0.5)

            time.sleep(2)
            self.driver.execute_script("window.scrollTo(150, 300);")

            post = WebDriverWait(self.driver, 100).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'button.css-y1m958')))

            while post.value_of_css_property("background-color") != 'rgba(254, 44, 85, 1)':
                print("TiktokUpload : La vidéo n'est pas encore chargé...")
                time.sleep(1)

            post.click()
            print("TiktokUploader : La vidéo de " + title + " à été upload.")
            print("TiktokUploader : Suppression de " + title + " en cours...")
            self.delete_file(video_path)
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
            self.tentative_upload += 1
            print('Tentative upload : ', self.tentative_upload)
            if self.tentative_upload > TENTATIVE_UPLOAD:
                print(f'Upload à échouée à {self.tentative_upload} tentatives. Arrêt complet pour cause :')
                print(e)
                self.driver.close()
                self.driver.quit()
                sys.exit()
            if isinstance(e, NoSuchWindowException):
                print("TiktokUpload : Aucune chrome window, relancement !")
                self.driver.close()
                self.driver.quit()
                self.driver = self.getChromeDriver()
                self.upload(video_path, title)
            elif isinstance(e, NoSuchElementException):
                print("TiktokUpload : Aucun Element... Vous devez vous relogin...")
                self.login()
                self.upload(video_path, title)
            elif isinstance(e, TimeoutException) or isinstance(e, ConnectionError):
                print("TiktokUpload : Timeout or Connection Error... Reupload..")
                self.upload(video_path, title)
            else:
                print("TiktokUpload : Une autre exception a été levée, fermeture ! Erreur :")
                print(e)
                self.driver.close()
                self.driver.quit()
                sys.exit()


"""
Utilisation : 
path_video = "C:\\Users\\Valentin\\Desktop\\VideoMaker\\videos\\Je suis onze nations – vidéo courte.mp4"
tiktokuploader = TiktokUploader([(path_video, "TEST")])
Options feature : Ajouter des tags autre que de base (prédéfini dans CAPTION.txt)
tiktokuploader = TiktokUploader([(path_video, "TEST")], ["#humour", "#fyp"])
"""