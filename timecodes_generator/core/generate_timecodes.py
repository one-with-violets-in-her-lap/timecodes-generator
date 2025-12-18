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
    title: str

    def __str__(self):
        return f"{format_timestamp_from_seconds(self.start_seconds)} - {self.title}"


def generate_timecodes(
    whisper_model: Whisper, file_path: str, search_patterns: list[Pattern]
) -> list[Timecode]:
    transcription_result = whisper_model.transcribe(file_path)
    segments = cast(list[Segment], transcription_result["segments"])

    _logger.debug("Segments: %s", segments)

    timecodes: list[Timecode] = []

    segment_start_index = 0

    while segment_start_index < len(segments):
        starting_segment = segments[segment_start_index]

        text = "".join(
            [
                segment["text"]
                for segment in segments[segment_start_index : segment_start_index + 4]
            ]
        )

        _logger.debug('Merged segments: %s', text.strip())

        for pattern in search_patterns:
            match = pattern.match(text.strip())

            if match is not None:
                _logger.info('Match: %s', match.group())
                timecodes.append(
                    Timecode(
                        id=starting_segment["id"],
                        start_seconds=starting_segment["start"],
                        title=match.group(),
                    )
                )
                segment_start_index = segment_start_index + 4
                continue

        segment_start_index = segment_start_index + 1

    return timecodes
