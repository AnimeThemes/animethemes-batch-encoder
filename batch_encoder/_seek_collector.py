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

    # List for all output_files
    all_output_names = []

    def __init__(self, source_file):
        self.source_file = source_file
        self.start_positions = SeekCollector.prompt_time('Start time(s): ')
        self.end_positions = SeekCollector.prompt_time('End time(s): ')
        self.output_names = SeekCollector.prompt_output_name()
        self.new_audio_filters = SeekCollector.prompt_new_audio_filters()

    # Prompt the user for our list of starting/ending positions of our WebMs
    # For starting positions, a blank input value is the 0 position of the source file
    # For ending positions, a blank input value is the end position of the source file
    @staticmethod
    def prompt_time(prompt_text):
        while True:
            invalid_time = False
            positions = input(prompt_text).split(',')
            for position in positions:
                if len(position) > 0 and not SeekCollector.time_pattern.match(position):
                    logging.error(f'\'{position}\' is not a valid time duration')
                    invalid_time = True
                    break
            if not invalid_time:
                return positions

    # Prompt the user for our list of name for our passlog/WebMs
    @staticmethod
    def prompt_output_name():
        while True:
            invalid_name = False
            filenames = input('Output file name(s): ').split(',')
            for filename in filenames:
                if not SeekCollector.filename_pattern.match(filename):
                    logging.error(f'\'{filename}\' is not a valid output file name')
                    invalid_name = True
                    break
            if not invalid_name:
                return filenames
          
    # Prompt the user for ours list of audio filters of ours WebMs
    @staticmethod
    def prompt_new_audio_filters():
        new_audio_filters = input('Audio Filter(s): ').split(',,')
        return new_audio_filters

    # Integrity Test 1: Our lists should be of equal length
    def is_length_consistent(self):
        length = len(self.start_positions)
        return all(len(lst) == length for lst in [self.end_positions, self.output_names])

    # Integrity Test 2: Positions should be within source file duration
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

    # Integrity Test 3: Start position is before end position
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

    # Integrity Test 4: Unique output names
    def is_unique_output_names(self):
        logging.debug(
            f'[SeekCollector.is_unique_output_names] len(set): \'{len(set(self.output_names))}\', '
            f'len: \'{len(self.output_names)}\'')

        return len(set(self.output_names)) == len(self.output_names)

    # Integrity Test 5: Unique output names in other source
    def is_unique_output_names_other_source(self):
        self.all_output_names.extend(self.output_names)

        logging.debug(
            f'[SeekCollector.is_unique_output_names_other_source] len(set): \'{len(set(self.all_output_names))}\', '
            f'len: \'{len(self.all_output_names)}\'')
        
        return len(set(self.all_output_names)) == len(self.all_output_names)

    # Integrity Tests with feedback
    def is_valid(self):
        is_valid = True

        if not self.is_length_consistent():
            is_valid = False
            logging.error('Collection not of equal length')

        if not self.is_within_source_duration():
            is_valid = False
            logging.error('Position greater than file duration')

        if not self.is_start_before_end():
            is_valid = False
            logging.error('Start Position is not before End Position')

        if not self.is_unique_output_names():
            is_valid = False
            logging.error('Output Names are not unique')

        if not self.is_unique_output_names_other_source():
            is_valid = False
            logging.error('Output Name is already being used')

        if not is_valid:
            self.all_output_names.pop()

        return is_valid

    # Our list of positions, validated if called after is_valid
    def get_seek_list(self):
        seek_list = []

        for start_position, end_position, output_name, new_audio_filter in zip(self.start_positions, self.end_positions,
                                                             self.output_names, self.new_audio_filters):
            seek = Seek(self.source_file, start_position, end_position, output_name, new_audio_filter)
            seek_list.append(seek)

        return seek_list
