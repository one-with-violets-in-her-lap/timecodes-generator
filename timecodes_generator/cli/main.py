import logging
import re

import click

from timecodes_generator.core.export import EXPORTERS, ExportFormat
from timecodes_generator.core.generate_timecodes import generate_timecodes
from timecodes_generator.core.load import ModelName, load_whisper_model
from timecodes_generator.core.utils.datetime_formatting import (
    format_timestamp_from_seconds,
)
from timecodes_generator.core.utils.regex import join_and_compile_regex_patterns

log_level_names_mapping = logging.getLevelNamesMapping()

export_format_click_type = click.Choice(
    [model_name_type.value for model_name_type in ExportFormat]
)


@click.command()
@click.argument("file-path", required=True)
@click.option(
    "--search",
    "-s",
    "search_patterns",
    required=True,
    multiple=True,
    help="Pattern in regular expression format to match word markers. "
    + "Example: Unit \\d (matches Unit {number}). "
    + "You can provide multiple patterns by using "
    + "this option multiple times (-s Pattern -s Pattern ...)",
)
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
    "--export",
    "export_format",
    default=None,
    required=False,
    type=export_format_click_type,
    help="Export timecodes in one of the following formats:\n"
    + "- id3: Encode timecodes in a new MP3 file with chapters\n"
    + "- folder: Split original file in multiple files based on the timecodes",
)
def start_cli(
    file_path: str,
    search_patterns: list[str],
    log_level: str,
    model_name: str,
    export_format: str | None,
):
    logging.basicConfig(
        level=log_level_names_mapping[log_level],
        format="%(asctime)s: [%(levelname)s] %(name)s - %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    click.secho(f"\n- Loading a model - Whisper {model_name}\n", dim=True)
    model = load_whisper_model(ModelName(model_name))

    click.secho("- Transcribing ...\n", dim=True)
    timecodes = generate_timecodes(
        model,
        file_path,
        join_and_compile_regex_patterns(search_patterns, flags=re.IGNORECASE),
        verbose=False,
    )

    click.secho("\n★ Timecodes:", bold=True)

    for timecode in timecodes:
        click.echo(
            click.style(format_timestamp_from_seconds(timecode.start_seconds))
            + " - "
            + timecode.title
        )

    if export_format is None:
        is_export_allowed = click.confirm(
            click.style("\n(?) ", dim=True) + "Would you like to save the timecodes?"
        )

        if is_export_allowed:
            export_format = click.prompt(
                click.style("\t(?) ", dim=True)
                + "In what format would you like to export?",
                type=export_format_click_type,
                show_choices=True,
            )

    if export_format is not None:
        exporter = EXPORTERS[ExportFormat(export_format)]
        export_result_path = exporter(file_path, timecodes)

        click.secho(f"\n✓ Saved at {export_result_path}", fg="green")


if __name__ == "__main__":
    start_cli()
