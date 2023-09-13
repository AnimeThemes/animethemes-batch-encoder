from ._interface import Interface
from ._seek import Seek
from ._utils import string_to_seconds

import logging
import re


# The collection of positions that we will use to seek within the source file
# These are the validated sets of cuts for our encodes
class SeekCollector:
    # Time Duration Specification: https://ffmpeg.org/ffmpeg-utils.html#time-duration-syntax
    time_pattern = re.compile('^([0-5]?\d:){1,2}[0-5]?\d(?=\.\d+$|$)|\d+(?=\.\d+$|$)')

    # AnimeThemes File Name Convention: '[Title]-{OP|ED}#v#'
    # Examples: Tamayura-OP1, PlanetWith-ED1v2
    filename_pattern = re.compile('^[a-zA-Z0-9\-]+$')

    # Lists for integrity tests
    all_output_names = []
    start_positions = 0

    # Validations for our prompts
    validate_seek = lambda _, x: \
        len(x.strip()) == 0 \
        or all(SeekCollector.time_pattern.match(y) for y in x.split(',')) \
        and SeekCollector.start_positions in [len(x.split(',')), 0]

    validate_output_name = lambda _, x: \
        len(x.strip()) > 0 \
        and all(SeekCollector.filename_pattern.match(y) and not y.strip() in SeekCollector.all_output_names for y in x.split(',')) \
        and SeekCollector.start_positions == len(x.split(',')) 

    def __init__(self, source_file):
        self.source_file = source_file
        self.start_positions = SeekCollector.prompt_time('Start time(s)')
        self.end_positions = SeekCollector.prompt_time('End time(s)')
        self.output_names = SeekCollector.prompt_output_name()
        self.new_audio_filters = SeekCollector.prompt_new_audio_filters(self)

    # Prompt the user for our list of starting/ending positions of our WebMs
    # For starting positions, a blank input value is the 0 position of the source file
    # For ending positions, a blank input value is the end position of the source file
    @staticmethod
    def prompt_time(prompt_text):
        positions = Interface.prompt_time(prompt_text, validate=SeekCollector.validate_seek).split(',')
        if prompt_text == 'Start time(s)':
            SeekCollector.start_positions = len(positions)

        return positions

    # Prompt the user for our list of name for our passlog/WebMs
    @staticmethod
    def prompt_output_name():
        filenames = Interface.prompt_text(message='Output file name(s)', validate=SeekCollector.validate_output_name).split(',')
        SeekCollector.all_output_names.extend(filenames)
        SeekCollector.start_positions = 0
         
        return filenames
          
    # Prompt the user for ours list of audio filters of ours WebMs
    @staticmethod
    def prompt_new_audio_filters(self):
        new_audio_filters = []
        for output_name in self.output_names:
            new_audio_filters.append(Interface.audio_filters_options(output_name))

        return new_audio_filters       

    # Integrity Test 1: Positions should be within source file duration
    def is_within_source_duration(self):
        source_file_duration = float(self.source_file.file_format['format']['duration'])

        for start_position, end_position in zip(self.start_positions, self.end_positions):
            start_time = string_to_seconds(start_position) if start_position else 0
            end_time = string_to_seconds(end_position) if end_position else source_file_duration

            logging.debug(
                f'[SeekCollector.is_within_source_duration] start_time: \'{start_time}\', '
                f'end_time: \'{end_time}\', '
                f'source_file_duration: \'{source_file_duration}\'')

            if start_time > source_file_duration or end_time > source_file_duration:
                return False

        return True

    # Integrity Test 2: Start position is before end position
    def is_start_before_end(self):
        source_file_duration = float(self.source_file.file_format['format']['duration'])
        for start_position, end_position in zip(self.start_positions, self.end_positions):
            start_time = string_to_seconds(start_position) if start_position else 0
            end_time = string_to_seconds(end_position) if end_position else source_file_duration

            logging.debug(
                f'[SeekCollector.is_start_before_end] start_time: \'{start_time}\', '
                f'end_time: \'{end_time}\', '
                f'source_file_duration: \'{source_file_duration}\'')

            if start_time >= end_time:
                return False

        return True

    # Integrity Tests with feedback
    def is_valid(self):
        is_valid = True

        if not self.is_within_source_duration():
            is_valid = False
            logging.error('Position greater than file duration')

        if not self.is_start_before_end():
            is_valid = False
            logging.error('Start Position is not before End Position')

        if not is_valid:
            SeekCollector.all_output_names.clear()
            SeekCollector.start_positions = 0

        return is_valid

    # Our list of positions, validated if called after is_valid
    def get_seek_list(self):
        seek_list = []

        for start_position, end_position, output_name, new_audio_filter in zip(self.start_positions, self.end_positions,
                                                             self.output_names, self.new_audio_filters):
            seek = Seek(self.source_file, start_position, end_position, output_name, new_audio_filter)
            seek_list.append(seek)

        return seek_list