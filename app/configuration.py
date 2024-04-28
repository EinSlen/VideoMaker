import os

file_config = os.path.abspath(__file__)
PATH_PARENT = os.path.dirname(os.path.dirname(file_config))
PROJET_NAME = os.path.basename(PATH_PARENT)

PATH_TEMP = os.path.join(PATH_PARENT, 'app', 'TEMP/')
VIDEOS_DIRECTORY = os.path.join(PATH_PARENT, 'videos/')
EDITED_PATH = os.path.join(PATH_PARENT, 'edited/')

LIBRARY_PATH = os.path.join(PATH_PARENT, 'app', 'lib/')

LANGUAGE = "fr-FR"

RESOLUTION_TIKTOK = (720, 1280)
FPS_TIKTOK = 60
FONT_TEXT = 'Arial-Bold-Italic'
FONT_PATH = os.path.join(PATH_PARENT, 'app', 'highlight', 'Arial.ttf')
COLOR_TEXT = ('yellow', 'orange')
STROKE_SIZE = 2

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
