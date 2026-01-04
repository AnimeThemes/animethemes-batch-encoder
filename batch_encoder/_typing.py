from typing import NamedTuple, Dict


class Args(NamedTuple):
    generate: bool
    execute: bool
    custom: bool
    file: str
    configfile: str
    inputfile: str
    loglevel: str


class EncodingConfigType(NamedTuple):
    allowed_filetypes: list[str]
    encoding_modes: list[str]
    crfs: list[int]
    cbr_bitrates: list[str]
    cbr_max_bitrates: list[str]
    threads: int
    limit_size_enable: bool
    alternate_source_files: bool
    create_preview: bool
    include_unfiltered: bool
    video_filters: Dict[str, str]
    default_video_stream: str
    default_audio_stream: str
