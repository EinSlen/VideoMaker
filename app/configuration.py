import os


file_config = os.path.abspath(__file__)
PATH_PARENT = os.path.dirname(os.path.dirname(file_config))
PROJET_NAME = os.path.basename(PATH_PARENT)

PATH_TEMP = os.path.join(PATH_PARENT, 'app', 'TEMP/')
VIDEOS_DIRECTORY = os.path.join(PATH_PARENT, 'videos/')
EDITED_PATH = os.path.join(PATH_PARENT, 'edited/')
LIB_PATH = os.path.join(PATH_PARENT, 'lib/')

LIBRARY_PATH = os.path.join(PATH_PARENT, 'app', 'lib/')

LANGUAGE = "fr-FR"

RESOLUTION_TIKTOK = (720, 720)
FPS_TIKTOK = 60

MODEL_PATH = "medium"

#RESET GIT ADD : git gc --prune=now
