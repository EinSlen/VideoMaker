import os

file_config = os.path.abspath(__file__)
PATH_PARENT = os.path.dirname(os.path.dirname(file_config))
PROJET_NAME = os.path.basename(PATH_PARENT)

PATH_TEMP = os.path.join(PATH_PARENT, 'app', 'TEMP/')
VIDEOS_DIRECTORY = os.path.join(PATH_PARENT, 'videos/')
EDITED_PATH = os.path.join(PATH_PARENT, 'edited/')

LIBRARY_PATH = os.path.join(PATH_PARENT, 'app', 'lib/')
SOUND_DIRECTORY = os.path.join(PATH_PARENT, 'sounds/')

LANGUAGE = "fr-FR"

RESOLUTION_TIKTOK = (1080, 1920)
FPS_TIKTOK = 60
TIKTOK_TEMPS_VIDEO = 60 #60 secondes correspond à 1 minute
FONT_TEXT = 'Arial-Bold-Italic'
FONT_PATH = os.path.join(PATH_PARENT, 'app', 'highlight', 'Arial.ttf')
COLOR_TEXT = ('yellow', 'orange')
STROKE_SIZE = 2

#PATH FOR THE NEW TIKTOK UPLOADER SUBMODULE
# lien du submodule : https://github.com/makiisthenes/TiktokAutoUploader
OUPUT_FOR_THE_NEW_UPLOAD = os.path.join(LIBRARY_PATH, 'TiktokAutoUploader/VideosDirPath')
COOKIE_SESSION_DIRECTORY = os.path.join(LIBRARY_PATH, 'TiktokAutoUploader/CookiesDir')
TiktokAutoUploader_DIR = os.path.join(LIBRARY_PATH, 'TiktokAutoUploader')
USER_CONFIG_NAME_1 = 'dvlad'
TAGS = "#humour #fyp #foryou #foryoupage #fy #viral #funnyvideos"
HOUR_LIST = ["07:00", "11:00", "17:00"]

MODEL_PATH = os.path.join(LIBRARY_PATH, 'vosk-model-small-fr-0.22')
MODEL = "medium"

CHROME_PORT = 9222

CAPTION = os.path.join(PATH_PARENT, 'app', 'highlight', 'caption.txt')
VIDEOS_ID = os.path.join(PATH_PARENT, 'app', 'highlight', 'videos_id.txt')

CHROME_PATH_USER = os.path.join(PATH_PARENT, 'app', 'localhost/')
CHROME_PATH_EXE = "C:\\Program Files\\Google\\Chrome\\Application"

#RESET GIT ADD : git gc --prune=now

VIDEOS_LIMIT_FOR_YT_TO_TK = 2
TEMPS_UPLOAD = 1440 #en minute
TENTATIVE_UPLOAD = 5

TRENDING_FILE_PATH = os.path.join(PATH_PARENT, 'trending_feeds.txt')
