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

print('=====================================================================================================')
print('Heyy, you have to login manully on tiktok, so the bot will wait you 1 minute for loging in manually!')
print('=====================================================================================================')
time.sleep(4)
print('Running bot now, get ready and login manually...')

#cd C:\Program Files\Google\Chrome\Application
#chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\Users\Valentin\Desktop\VideoMaker\app\localhost"

options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "localhost:9222")
service = Service(executable_path=CM().install())
bot = webdriver.Chrome(options=options, service=service)
bot.set_window_size(1680, 900)

bot.get('https://www.tiktok.com/login')
ActionChains(bot).key_down(Keys.CONTROL).send_keys(
    '-').key_up(Keys.CONTROL).perform()
ActionChains(bot).key_down(Keys.CONTROL).send_keys(
    '-').key_up(Keys.CONTROL).perform()
print('Waiting 50s for manual login...')
time.sleep(5)
bot.get('https://www.tiktok.com/creator-center/upload?lang=fr')
time.sleep(5)


def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False

    return True


def upload(video_path):
    while True:
        """
        WebDriverWait(bot, 20).until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@type='file']"))).send_keys(
            video_path)
        """

        iframe = bot.find_element(By.XPATH, "//iframe[@data-tt='Upload_index_iframe']")
        bot.switch_to.frame(iframe)

        file_uploader = WebDriverWait(bot, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
        file_uploader.send_keys(video_path)

        
        caption = bot.find_element_by_xpath(
            '//*[@id="main"]/div[2]/div/div[2]/div[3]/div[1]/div[1]/div[2]/div/div[1]/div/div/div/div/div/div/span')

        bot.implicitly_wait(10)
        ActionChains(bot).move_to_element(caption).click(
            caption).perform()
        # ActionChains(bot).key_down(Keys.CONTROL).send_keys(
        #     'v').key_up(Keys.CONTROL).perform()

        with open(r"caption.txt", "r") as f:
            tags = [line.strip() for line in f]

        for tag in tags:
            ActionChains(bot).send_keys(tag).perform()
            time.sleep(2)
            ActionChains(bot).send_keys(Keys.RETURN).perform()
            time.sleep(1)

        time.sleep(5)
        bot.execute_script("window.scrollTo(150, 300);")
        time.sleep(5)

        post = WebDriverWait(bot, 100).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="main"]/div[2]/div/div[2]/div[3]/div[5]/button[2]')))

        post.click()
        time.sleep(30)

        if check_exists_by_xpath(bot, '//*[@id="portal-container"]/div/div/div[1]/div[2]'):
            reupload = WebDriverWait(bot, 100).until(EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="portal-container"]/div/div/div[1]/div[2]')))

            reupload.click()
        else:
            print('Unknown error cooldown')
            while True:
                time.sleep(600)
                post.click()
                time.sleep(15)
                if check_exists_by_xpath(bot, '//*[@id="portal-container"]/div/div/div[1]/div[2]'):
                    break

        if check_exists_by_xpath(bot, '//*[@id="portal-container"]/div/div/div[1]/div[2]'):
            reupload = WebDriverWait(bot, 100).until(EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="portal-container"]/div/div/div[1]/div[2]')))
            reupload.click()

        time.sleep(1)


# ================================================================
# Here is the path of the video that you want to upload in tiktok.
# Plese edit the path because this is different to everyone.
upload(r"C:\Users\Valentin\Desktop\VideoMaker\app\components\TEST (3).mp4")
# ================================================================
