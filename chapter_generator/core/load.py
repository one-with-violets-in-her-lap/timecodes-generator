from typing import Literal

import whisper

ModelName = Literal["tiny.en", "tiny", "small.en", "small"]


def load_whisper_model(model_name: ModelName):
    return whisper.load_model(model_name)
