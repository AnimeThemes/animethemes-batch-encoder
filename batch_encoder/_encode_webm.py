from ._bitrate_mode import BitrateMode
from ._colorspace import Colorspace
from ._loudnorm_filter import LoudnormFilter
from ._utils import string_to_seconds

import logging


# The class that generates FFmpeg commands for the specific cut in the source file
# We generate common argument values that can be determined programmatically and then use our config to produce commands
class EncodeWebM:
    def __init__(self, source_file, seek):
        self.source_file = source_file
        self.seek = seek
        self.loudnorm_filter = LoudnormFilter.from_seek(self.seek)
        self.g = self.get_keyframe_interval()
        self.audio_bitrate = self.get_audio_bitrate()
        self.cbr_bitrate = self.get_cbr_bitrate()
        self.cbr_max_bitrate = self.get_cbr_max_bitrate()
        self.colorspace = Colorspace.value_of(self.source_file)

    # We want at least 10 keyframes in our encode and consistency in our interval
    def get_keyframe_interval(self):
        source_file_duration = float(self.source_file.file_format['format']['duration'])

        start_time = string_to_seconds(self.seek.ss) if self.seek.ss else 0
        end_time = string_to_seconds(self.seek.to) if self.seek.to else source_file_duration
        duration = end_time - start_time

        logging.debug(
            f'[EncodeWebm.get_keyframe_interval] '
            f'duration: \'{duration}\', '
            f'end_time: \'{end_time}\', '
            f'start_time: \'{start_time}\'')

        if duration < 60:
            return 96
        elif duration < 120:
            return 120
        else:
            return 240

    # Audio must use a default bitrate of 192 kbps
    # Audio must use a bitrate of 320 kbps if the source bitrate is > 320 kbps
    def get_audio_bitrate(self):
        audio_bitrate = int(self.source_file.audio_format['format']['bit_rate'])

        logging.debug(f'[EncodeWebm.get_audio_bitrate] audio_bitrate: \'{audio_bitrate}\'')

        if audio_bitrate > 320000:
            return '320k'
        else:
            return '192k'

    # Approximation of target average bitrate near file size limit
    def get_cbr_bitrate(self):
        resolution = int(self.source_file.video_format['streams'][0]['height'])

        logging.debug(f'[EncodeWebm.get_cbr_bitrate] resolution: \'{resolution}\'')

        if resolution >= 1080:
            return '5600k'
        elif resolution >= 720:
            return '3700k'
        elif resolution >= 576:
            return '3200k'
        else:
            return '2400k'

    # Approximation of max overall bitrate near file size limit
    def get_cbr_max_bitrate(self):
        resolution = int(self.source_file.video_format['streams'][0]['height'])

        logging.debug(f'[EncodeWebm.get_cbr_max_bitrate] resolution: \'{resolution}\'')

        if resolution >= 1080:
            return '6400k'
        elif resolution >= 720:
            return '4200k'
        elif resolution >= 576:
            return '3700k'
        else:
            return '3200k'

    # Limiting file size based on resolution and duration
    def get_limit_file_size(self, video_filters=''):
        source_file_duration = float(self.source_file.file_format['format']['duration'])

        start_time = string_to_seconds(self.seek.ss) if self.seek.ss else 0
        end_time = string_to_seconds(self.seek.to) if self.seek.to else source_file_duration
        duration = end_time - start_time

        for filter in video_filters.split(','):
            if 'scale=-1:' in filter:
                resolution = int(filter.split(':')[1])
                break
            else:
                resolution = int(self.source_file.video_format['streams'][0]['height'])
        
        logging.debug(f'[EncodeWebm.get_limit_file_size] resolution: \'{resolution}\'')

        max_allowed_bitrate = resolution * 6100 + 475000
        max_allowed_size = max_allowed_bitrate * duration
        limit_size = max_allowed_size / 8

        return str(round(limit_size))
    
    # Command to preview a seek
    def preview_seek(self, webm_filename=''):
        return f'ffmpeg {self.seek.get_seek_string()} ' \
               f'{self.get_audio_filters()} ' \
               f'-vcodec copy -c:a aac -b:a 128k -sn -f mp4 {webm_filename}.mp4'

    # First-pass encode
    def get_first_pass(self, encoding_mode, crf=None, threads=4):
        return f'ffmpeg {self.seek.get_seek_string()} ' \
               f'-pass 1 -passlogfile {self.seek.output_name} ' \
               f'-map 0:v:{self.source_file.selected_video_stream} ' \
               f'-map 0:a:{self.source_file.selected_audio_stream} ' \
               f'-c:v libvpx-vp9 ' \
               f'{encoding_mode.first_pass_rate_control(self.cbr_bitrate, self.cbr_max_bitrate, crf)} ' \
               f'-cpu-used 4 -g {self.g} -threads {threads} -tile-columns 6 -frame-parallel 0 -auto-alt-ref 1 ' \
               f'-lag-in-frames 25 -row-mt 1 -pix_fmt yuv420p {self.colorspace.get_args()} -an -sn -f webm -y NUL'

    # Second-pass encode
    def get_second_pass(self, encoding_mode, crf=None, threads=4, video_filters='', limit_size_enable=True, webm_filename=''):
        limit_size = '-fs ' + EncodeWebM.get_limit_file_size(self, video_filters=video_filters) + ' ' if limit_size_enable else ''
        return f'ffmpeg {self.seek.get_seek_string()} ' \
               f'-pass 2 -passlogfile {self.seek.output_name} ' \
               f'-map 0:v:{self.source_file.selected_video_stream} ' \
               f'-map 0:a:{self.source_file.selected_audio_stream} ' \
               f'-c:v libvpx-vp9 ' \
               f'{encoding_mode.second_pass_rate_control(self.cbr_bitrate, self.cbr_max_bitrate, crf)} ' \
               f'-cpu-used 0 -g {self.g} -threads {threads} {self.get_audio_filters()}{video_filters} -tile-columns 6 ' \
               f'-frame-parallel 0 -auto-alt-ref 1 -lag-in-frames 25 -row-mt 1 -pix_fmt yuv420p ' \
               f'{self.colorspace.get_args()} ' \
               f'-c:a libopus -b:a {self.audio_bitrate} -ar 48k ' \
               f'{limit_size}' \
               f'-map_metadata:g -1 -map_metadata:s:v -1 -map_metadata:s:a -1 -map_chapters -1 -sn -f webm -y {webm_filename}.webm'

    # Build audio filtergraph for encodes
    def get_audio_filters(self):
        audio_filters = []
        self.source_file.apply_audio_resampling(audio_filters)
        audio_filters.append(self.loudnorm_filter.get_normalization_filter())
        audio_filters.append(self.seek.new_audio_filter) if self.seek.new_audio_filter.strip() != '' else None
        return '-af ' + ','.join(audio_filters)

    # Build video filtergraph for encodes
    @staticmethod
    def get_video_filters(config_filter=None):
        video_filters = []

        if config_filter is not None:
            video_filters.append(config_filter)

        if not video_filters or len(video_filters[0].strip()) == 0 or 'No Filters' in video_filters:
            return ''

        return ' -vf ' + ','.join(video_filters)

    # Build unique WebM filename for encodes
    def get_webm_filename(self, crf=None, cbr_bitrate=None, filter_name=None):
        webm_filename = self.seek.output_name

        if crf is not None:
            webm_filename += f'-{crf}'

        if cbr_bitrate is not None:
            webm_filename += f'-{self.cbr_bitrate}'

        if filter_name is not None:
            webm_filename += f'-{filter_name}'

        return webm_filename

    # Get list of commands in sequence specified by configuration file
    # Sequencing - 1. Encoding Mode, 2: CRF, 3: Filter mapping
    def get_commands(self, encoding_config):
        file_commands = []

        if len(encoding_config.video_filters) == 0:
            encoding_config.video_filters.append((None, 'No Filters'))

        logging.debug(
            f'[EncodeWebm.get_commands] encoding_modes: \'{encoding_config.encoding_modes}\', '
            f'crfs: \'{encoding_config.crfs}\', '
            f'include_unfiltered: \'{encoding_config.include_unfiltered}\', '
            f'video_filters: \'{encoding_config.video_filters}\'')
        
        if encoding_config.create_preview:
            file_commands.append(self.preview_seek(webm_filename=self.get_webm_filename()))

        for encoding_mode in encoding_config.encoding_modes:
            if BitrateMode.CBR.name == encoding_mode.upper():
                file_commands.append(self.get_first_pass(BitrateMode.CBR, threads=encoding_config.threads))
                for filter_name, filter_value in encoding_config.video_filters:
                    file_commands.append(self.get_second_pass(BitrateMode.CBR,
                                                              threads=encoding_config.threads,
                                                              video_filters=EncodeWebM.get_video_filters(
                                                                  config_filter=filter_value),
                                                              limit_size_enable=encoding_config.limit_size_enable,
                                                              webm_filename=self.get_webm_filename(
                                                                  cbr_bitrate=self.cbr_bitrate,
                                                                  filter_name=filter_name)))
            elif BitrateMode.VBR.name == encoding_mode.upper():
                for crf in encoding_config.crfs:
                    file_commands.append(self.get_first_pass(BitrateMode.VBR, crf=crf, threads=encoding_config.threads))
                    for filter_name, filter_value in encoding_config.video_filters:
                        file_commands.append(self.get_second_pass(BitrateMode.VBR, crf=crf,
                                                                  threads=encoding_config.threads,
                                                                  video_filters=EncodeWebM.get_video_filters(
                                                                      config_filter=filter_value),
                                                                  limit_size_enable=encoding_config.limit_size_enable,
                                                                  webm_filename=self.get_webm_filename(
                                                                      crf=crf,
                                                                      filter_name=filter_name)))
            elif BitrateMode.CQ.name == encoding_mode.upper():
                for crf in encoding_config.crfs:
                    file_commands.append(self.get_first_pass(BitrateMode.CQ, crf=crf, threads=encoding_config.threads))
                    for filter_name, filter_value in encoding_config.video_filters:
                        file_commands.append(self.get_second_pass(BitrateMode.CQ, crf=crf,
                                                                  threads=encoding_config.threads,
                                                                  video_filters=EncodeWebM.get_video_filters(
                                                                      config_filter=filter_value),
                                                                  limit_size_enable=encoding_config.limit_size_enable,
                                                                  webm_filename=self.get_webm_filename(
                                                                      crf=crf,
                                                                      cbr_bitrate=self.cbr_bitrate,
                                                                      filter_name=filter_name)))

        logging.debug(f'[EncodeWebm.get_commands] # of file_commands: \'{len(file_commands)}\'')
        
        return file_commands