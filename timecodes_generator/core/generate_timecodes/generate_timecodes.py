import logging
from dataclasses import dataclass
from re import Pattern
from typing import TypedDict, cast

from whisper import Whisper

from timecodes_generator.core.utils.datetime_formatting import (
    format_timestamp_from_seconds,
)

_logger = logging.getLogger(__name__)


class Segment(TypedDict):
    id: int
    start: int
    end: int
    text: str


@dataclass
class Timecode:
    id: int
    start_seconds: int
    end_seconds: int
    title: str

    def __str__(self):
        return f"{format_timestamp_from_seconds(self.start_seconds)} - {self.title}"


SEGMENT_GROUP_SIZE = 3


def find_segment_by_string_position(segment_group: list[Segment], position: int):
    text_end = 0

    for segment in segment_group:
        text_start = text_end - 1
        text_end = text_end + len(segment["text"])

        if position > text_start and position < text_end:
            return segment


def parse_timecodes_from_segment_group(
    text: str, segment_group: list[Segment], search_pattern: Pattern
):
    timecodes: list[Timecode] = []

    for match in search_pattern.finditer(text):
        segment_with_occurrence = find_segment_by_string_position(
            segment_group, match.start()
        )

        if segment_with_occurrence is None:
            _logger.warning(
                "Failed to find segment by string position. Falling back to a starting segment"
            )
            segment_with_occurrence = segment_group[0]

        timecodes.append(
            Timecode(
                id=segment_with_occurrence["id"],
                start_seconds=segment_with_occurrence["start"],
                end_seconds=segment_with_occurrence["end"],
                title=match.group(),
            )
        )

    return timecodes


def add_or_update_timecode(timecodes: list[Timecode], new_timecode: Timecode):
    for timecode in timecodes:
        if timecode.start_seconds == new_timecode.start_seconds:
            timecode.title = new_timecode.title
            _logger.debug("Updating title to more complete one: %s", timecode)
            return

    _logger.info("Adding timecode: %s", new_timecode)
    timecodes.append(new_timecode)


def extract_timecodes(segments: list[Segment], search_pattern: Pattern):
    timecodes: list[Timecode] = []

    for segment_start_index, _ in enumerate(segments):
        segment_group = segments[
            segment_start_index : segment_start_index + SEGMENT_GROUP_SIZE
        ]

        text = "".join([segment["text"] for segment in segment_group])

        _logger.debug("Merged segments: %s", text)

        for found_timecode in parse_timecodes_from_segment_group(
            text, segment_group, search_pattern
        ):
            add_or_update_timecode(timecodes, found_timecode)

    return timecodes


def generate_timecodes(
    whisper_model: Whisper,
    file_path: str,
    search_pattern: Pattern,
    verbose: bool | None = None,
) -> list[Timecode]:
    transcription_result = whisper_model.transcribe(file_path, verbose=verbose)
    segments = cast(list[Segment], transcription_result["segments"])

    _logger.debug("Transcribed: %s", transcription_result["text"])
    _logger.debug(
        "Segments: %s",
        "\n".join([str(segment) for segment in transcription_result["segments"]]),
    )

    return extract_timecodes(segments, search_pattern)
