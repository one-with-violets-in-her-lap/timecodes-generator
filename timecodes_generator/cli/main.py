import argparse
import logging
import re

from timecodes_generator.core.generate_timecodes import generate_timecodes
from timecodes_generator.core.load import load_whisper_model


class CliError(Exception):
    pass


LOG_LEVELS = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}

# TODO: make a cli argument + simpler custom pattern system for the future
TIMECODE_SEARCH_PATTERNS = [
    re.compile(
        r"(?:Unit \d+.? )?Activity [a-zA-Z].+?(?=\.|$)", flags=re.IGNORECASE
    ),  # Unit {number}. Activity {letter}. {...remaining sentence}
    re.compile(
        r"(?:Unit \d+.? )?Practice \d.+?(?=\.|$)", flags=re.IGNORECASE
    ),  # Unit {number}. Practice {number}. {...remaining sentence}
    re.compile(
        r"Unit \d+.? (?![^.]*\bActivity|Practice\b)[^.]*(\.|$)", flags=re.IGNORECASE
    ),  # Unit {number}. {...remaining sentence}
]


def main():
    parser = argparse.ArgumentParser(prog="Timecodes generator")
    parser.add_argument("file_path", help="Path to an audio file to process")
    parser.add_argument("--log-level", default="critical")

    args = parser.parse_args()
    log_level = LOG_LEVELS[args.log_level]

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s: [%(levelname)s] %(name)s - %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    print("Loading a model")
    model = load_whisper_model("small")

    print("Transcribing", "\n")
    timecodes = generate_timecodes(model, args.file_path, TIMECODE_SEARCH_PATTERNS)

    for timecode in timecodes:
        print(timecode)


if __name__ == "__main__":
    main()
