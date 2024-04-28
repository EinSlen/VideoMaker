import numpy as np
import whisper
import os
import shutil
import cv2
from PIL import ImageDraw, Image, ImageFont
from moviepy.editor import ImageSequenceClip, AudioFileClip, VideoFileClip
from app.configuration import *
from tqdm import tqdm

FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.8
FONT_THICKNESS = 2


class VideoTranscriber:
    def __init__(self, model_path, video_path):
        self.model = whisper.load_model(model_path)
        self.video_path = video_path
        self.video_title = os.path.splitext(os.path.basename(video_path))[0]
        self.audio_path = ''
        self.text_array = []
        self.fps = 0
        self.char_width = 0

    def transcribe_video(self):
        print('Transcribing video')
        result = self.model.transcribe(self.audio_path)
        print(result)
        text = result["text"]
        textsize = cv2.getTextSize(text, FONT, FONT_SCALE, FONT_THICKNESS)[0]
        cap = cv2.VideoCapture(self.video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        asp = 16 / 9
        ret, frame = cap.read()
        width = frame[:, int(int(width - 1 / asp * height) / 2):width - int((width - 1 / asp * height) / 2)].shape[1]
        width = width - (width * 0.1)
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.char_width = int(textsize[0] / len(text))

        for j in tqdm(result["segments"]):
            lines = []
            text = j["text"]
            end = j["end"]
            start = j["start"]
            total_frames = int((end - start) * self.fps)
            start = start * self.fps
            total_chars = len(text)
            words = text.split(" ")
            i = 0

            while i < len(words):
                words[i] = words[i].strip()
                if words[i] == "":
                    i += 1
                    continue
                length_in_pixels = (len(words[i]) + 1) * self.char_width
                remaining_pixels = width - length_in_pixels
                line = words[i]

                while remaining_pixels > 0:
                    i += 1
                    if i >= len(words):
                        break
                    length_in_pixels = (len(words[i]) + 1) * self.char_width
                    remaining_pixels -= length_in_pixels
                    if remaining_pixels < 0:
                        continue
                    else:
                        line += " " + words[i]

                line_array = [line, int(start) + 15, int(len(line) / total_chars * total_frames) + int(start) + 15]
                start = int(len(line) / total_chars * total_frames) + int(start)
                lines.append(line_array)
                self.text_array.append(line_array)

        cap.release()
        print('Transcription complete')

    def extract_audio(self):
        print('Extracting audio')
        audio_path = os.path.join(os.path.dirname(self.video_path), self.video_title+"_audio.mp3")
        video = VideoFileClip(self.video_path)
        audio = video.audio
        audio.write_audiofile(audio_path)
        self.audio_path = audio_path
        print('Audio extracted')

    def extract_frames(self, output_folder):
        print('Extracting frames')
        cap = cv2.VideoCapture(self.video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        asp = width / height
        N_frames = 0

        font_path = FONT_PATH
        font_size = 45
        font = ImageFont.truetype(font_path, font_size)

        def approximate_text_size(text, font):
            num_chars = len(text)
            text_width = num_chars * font_size * 0.6  # Ajustez ce coefficient selon vos besoins
            text_height = font_size
            return (text_width, text_height)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = frame[:, int(int(width - 1 / asp * height) / 2):width - int((width - 1 / asp * height) / 2)]

            for i in self.text_array:
                if N_frames >= i[1] and N_frames <= i[2]:
                    text = i[0]

                    pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    draw = ImageDraw.Draw(pil_frame)

                    # Obtenir la taille approximative du texte
                    text_size = approximate_text_size(text, font)

                    # Calculer les coordonnées de départ du texte pour le placer au centre
                    text_x = (frame.shape[1] - width)
                    text_y = (frame.shape[0] - text_size[1]) // 1.5

                    # Dessiner du texte en blanc
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            if abs(dx) + abs(dy) < 2:
                                draw.text((text_x + dx, text_y + dy), text, font=font, fill=(0, 0, 255))

                        # Dessiner le texte principal
                    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))

                    frame = cv2.cvtColor(np.array(pil_frame), cv2.COLOR_RGB2BGR)

                    break

            cv2.imwrite(os.path.join(output_folder, str(N_frames) + ".jpg"), frame)
            N_frames += 1

        cap.release()
        print('Frames extracted')

    def create_video(self, output_video_path):
        print('Creating video')
        image_folder = os.path.join(os.path.dirname(self.video_path), "frames")
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)

        self.extract_frames(image_folder)

        images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
        images.sort(key=lambda x: int(x.split(".")[0]))

        frame = cv2.imread(os.path.join(image_folder, images[0]))
        height, width, layers = frame.shape

        clip = ImageSequenceClip([os.path.join(image_folder, image) for image in images], fps=self.fps)
        audio = AudioFileClip(self.audio_path)
        clip = clip.set_audio(audio)
        clip.write_videofile(output_video_path)
        shutil.rmtree(image_folder)
        os.remove(os.path.join(os.path.dirname(self.video_path), self.video_title+"_audio.mp3"))

"""
# Example usage
model_path = "base"
# video_path = "test_videos/videoplayback.mp4"
video_path = "TEST (4).mp4"
# output_audio_path = "test_videos/audio.mp3"
output_video_path = "outputtest.mp4"
trannscriber = VideoTranscriber(model_path, video_path)
trannscriber.extract_audio()
trannscriber.transcribe_video()
trannscriber.create_video(video_path)
"""