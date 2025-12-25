import os
from typing import cast

import eyed3
import eyed3.mp3
from pydub import AudioSegment

from timecodes_generator.core.generate_timecodes import Timecode
from timecodes_generator.core.utils.errors import AudioProcessingError


def prepare_mp3_file_for_tagging(source_audio_file_path: str):
    file_path_without_extension, _ = os.path.splitext(source_audio_file_path)
    mp3_file_path = file_path_without_extension + " (with timecodes).mp3"

    audio_segment: AudioSegment = AudioSegment.from_file(source_audio_file_path)
    audio_segment.export(mp3_file_path, format="mp3")

    return mp3_file_path


def export_tagged_audio_file(source_file_path: str, timecodes: list[Timecode]):
    mp3_file_path = prepare_mp3_file_for_tagging(source_file_path)

    audio = cast(eyed3.mp3.Mp3AudioFile, eyed3.load(mp3_file_path))

    if audio is None:
        raise AudioProcessingError(f"Failed to read {mp3_file_path}")

    tags = audio.initTag()
    if tags.table_of_contents is None or tags.chapters is None:
        raise AudioProcessingError(
            "Failed to initialize tags. table_of_contents or chapters variable is None"
        )

    tags.table_of_contents.set(
        "table-of-contents".encode(),
        toplevel=True,
        child_ids=[timecode.title.encode() for timecode in timecodes],
    )

    for timecode in timecodes:
        tags.chapters.set(
            element_id=timecode.title.encode(),
            times=(timecode.start_seconds * 1000, timecode.end_seconds * 1000),
        )

    tags.save()

    return mp3_file_path
