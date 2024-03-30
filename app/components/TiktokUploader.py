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

#cd C:\Program Files\Google\Chrome\Application
#chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\Users\Valentin\Desktop\VideoMaker\app\localhost"


driver.get('https://www.tiktok.com/login')
ActionChains(driver).key_down(Keys.CONTROL).send_keys(
    '-').key_up(Keys.CONTROL).perform()
ActionChains(driver).key_down(Keys.CONTROL).send_keys(
    '-').key_up(Keys.CONTROL).perform()
print('Waiting 50s for manual login...')
time.sleep(5)
driver.get('https://www.tiktok.com/creator-center/upload?lang=fr')
time.sleep(5)

class TiktokUploader:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "localhost:"+CHROME_PORT)
        service = Service(executable_path=CM().install())
        self.driver = webdriver.Chrome(options=options, service=service)

def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False

    return True


def upload(video_path):
    while True:
        """
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@type='file']"))).send_keys(
            video_path)
        """

        iframe = driver.find_element(By.XPATH, "//iframe[@data-tt='Upload_index_iframe']")
        driver.switch_to.frame(iframe)

        file_uploader = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
        file_uploader.send_keys(video_path)

        driver.switch_to.default_content()

        iframe_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//iframe[@data-tt='Upload_index_iframe']"))
        )

        driver.switch_to.frame(iframe_element)

        caption = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-friends"))
        )

        driver.implicitly_wait(10)
        ActionChains(driver).move_to_element(caption).click(
            caption).perform()
        # ActionChains(driver).key_down(Keys.CONTROL).send_keys(
        #     'v').key_up(Keys.CONTROL).perform()

        ActionChains(driver).send_keys(" - ").perform()

        with open(r"C:\Users\Valentin\Desktop\VideoMaker\app\caption.txt", "r") as f:
            tags = [line.strip() for line in f]
        for tag in tags:
            ActionChains(driver).send_keys(tag).perform()
            time.sleep(2)
            ActionChains(driver).send_keys(Keys.RETURN).perform()
            time.sleep(1)

        time.sleep(5)
        driver.execute_script("window.scrollTo(150, 300);")
        time.sleep(5)

        post = WebDriverWait(driver, 100).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, 'button.css-y1m958')))

        post.click()
        time.sleep(5)
        driver.get('https://www.tiktok.com/creator-center/upload?lang=fr')
        
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


# ================================================================
# Here is the path of the video that you want to upload in tiktok.
# Plese edit the path because this is different to everyone.
upload(r"C:\Users\Valentin\Desktop\VideoMaker\app\components\TEST (3).mp4")
# ================================================================
