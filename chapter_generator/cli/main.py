import argparse

from chapter_generator.core.load import load_whisper_model


class CliError(Exception):
    pass


def main():
    parser = argparse.ArgumentParser(prog="chapter_generator")
    parser.add_argument("file_path", help="Path to an audio file to process")

    args = parser.parse_args()

    print('Loading a model')
    model = load_whisper_model("small.en")

    print('Transcribing')


if __name__ == "__main__":
    main()
