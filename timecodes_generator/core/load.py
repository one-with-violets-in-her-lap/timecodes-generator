from enum import Enum

import whisper


class ModelName(Enum):
    TINY = "tiny"
    TINY_EN = "tiny.en"
    BASE = "base"
    BASE_EN = "base.en"
    SMALL = "small"
    SMALL_EN = "small.en"
    MEDIUM = "medium"
    MEDIUM_EN = "medium.en"
    LARGE = "large"
    TURBO = "turbo"


def load_whisper_model(model_name: ModelName):
    return whisper.load_model(model_name.value)
