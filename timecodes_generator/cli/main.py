import logging
import re

import click

from timecodes_generator.core.export import export_tagged_audio_file
from timecodes_generator.core.generate_timecodes import generate_timecodes
from timecodes_generator.core.load import ModelName, load_whisper_model
from timecodes_generator.core.utils.datetime_formatting import (
    format_timestamp_from_seconds,
)

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

log_level_names_mapping = logging.getLevelNamesMapping()


@click.command()
@click.argument("file-path", required=True)
@click.option(
    "--log-level", "-l", type=click.Choice(log_level_names_mapping), default="ERROR"
)
@click.option(
    "--model",
    "-m",
    "model_name",
    type=click.Choice([model_name_type.value for model_name_type in ModelName]),
    default="small",
)
@click.option(
    "--tagged-mp3",
    "save_tagged_mp3_file",
    default=None,
    required=False,
    help="Encode timecodes in a new MP3 file with chapters",
)
def start_cli(
    file_path: str, log_level: str, model_name: str, save_tagged_mp3_file: bool | None
):
    logging.basicConfig(
        level=log_level_names_mapping[log_level],
        format="%(asctime)s: [%(levelname)s] %(name)s - %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    click.secho(f"\n- Loading a model - Whisper {model_name}\n", dim=True)
    model = load_whisper_model(ModelName(model_name))

    click.secho("- Transcribing ...\n", dim=True)
    timecodes = generate_timecodes(model, file_path, TIMECODE_SEARCH_PATTERNS)

    click.secho("\n★ Timecodes:", bold=True)

    for timecode in timecodes:
        click.echo(
            click.style(format_timestamp_from_seconds(timecode.start_seconds))
            + " - "
            + timecode.title
        )

    if save_tagged_mp3_file is None:
        save_tagged_mp3_file = click.confirm(
            "\n(?) Would you like to save timecodes in a tagged MP3 file?"
        )

    if save_tagged_mp3_file:
        mp3_file_path = export_tagged_audio_file(file_path, timecodes)

        click.secho(f'\n✓ Saved at {mp3_file_path}', fg='green')


if __name__ == "__main__":
    start_cli()
