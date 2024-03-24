import os
import sys
import argparse
import logging
import warnings

warnings.filterwarnings("ignore")

from pathlib import Path
from hydra import compose, initialize
from omegaconf import DictConfig
from app.configuration import *

from app.lib.subtitle_str.src.subtitles_generator.core import Model

from app.lib.subtitle_str.src.subtitles_generator.utils import create_srt, extract_audio

logger = logging.getLogger(__name__)
logging_handler = logging.StreamHandler(sys.stdout)
logging_handler.setLevel(logging.INFO)
logger.addHandler(logging_handler)
class SubtitlesGenerator:

    def __init__(self, input_file, output_file, model="medium", lang="french"):
        self.args = {
            'model_size': model,
            'lang': lang,
            'input_file': input_file,
            'output_file': output_file
        }

        with initialize(version_base=None, config_path="../lib/subtitle_str/src/subtitles_generator/conf"):
            cfg = compose(config_name="config")
        self.app(cfg)


    def parse_args(self, cfg: DictConfig, args):
        parser = argparse.ArgumentParser(
            description='It creates subtitles from a video or an audio'
        )

        parser.add_argument('--model_size', type=str, default='medium',
                            help='model size')
        parser.add_argument('--lang', type=str, default='french',
                            help='language of speech in an audio or video: english, french')
        parser.add_argument('--input_file', type=str, required=True,
                            help='path to an audio or video file')
        parser.add_argument('--output_file', type=str,
                            help='path to a result file with subtitles')

        #args = parser.parse_args()
        lang = args['lang']
        input_file = Path(args['input_file'])
        model_size = args['model_size']

        # Sanity checks
        try:
            output_file = Path(args['output_file'])
        except:
            output_file = input_file.parents[0] / (input_file.stem + '.srt')

        if lang not in cfg.supported_languages:
            raise ValueError(
                f"Language {lang} is not supported."\
                    "Supported languages are {cfg.supported_languages}"
            )

        if model_size not in cfg.model_names.keys():
            raise ValueError(
                f"Model size {model_size} is not supported."\
                    f"Supported model sizes are {cfg.model_names.keys()}"
            )

        if not input_file.is_file():
            raise (OSError(f"Input file {input_file} does not exists"))
        if input_file.suffix not in cfg.supported_media_formats.video and \
                input_file.suffix not in cfg.supported_media_formats.audio:
            raise ValueError(
                f"""A file must be a video: {cfg.supported_media_formats.video}
              or an audio {cfg.supported_media_formats.audio}"""
            )
        return input_file, output_file, lang, model_size


    def app(self, cfg: DictConfig) -> None:
        input_file, output_file, lang, model_size = self.parse_args(cfg, self.args)
        # if an input is video then we extract the audio from it
        if input_file.suffix in cfg.supported_media_formats.video:
            logger.info("Extracting audio ...")
            input_file = extract_audio(input_file)

        model = Model(cfg.model_names[model_size], lang)
        logger.info("Generating subtitles ...")
        predicted_texts = model.transcribe(
            audio_path=input_file,
            sampling_rate=cfg.processing.sampling_rate,
            chunk_size=cfg.processing.chunk_size
        )

        logger.info(f"Writing subtitles into {output_file} ...")
        create_srt(
            output_file, predicted_texts, cfg.processing.chunk_size
        )
        os.remove(input_file)