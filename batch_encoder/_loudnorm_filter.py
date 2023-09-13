import json
import logging
import re
import shlex
import subprocess


# The audio normalization filter for our encode
class LoudnormFilter:
    first_pass_filter = 'loudnorm=I=-16:LRA=20:TP=-1:dual_mono=true:linear=true:print_format=json'

    def __init__(self, input_i, input_lra, input_tp, input_thresh, target_offset):
        self.input_i = input_i
        self.input_lra = input_lra
        self.input_tp = input_tp
        self.input_thresh = input_thresh
        self.target_offset = target_offset

    @classmethod
    def from_seek(cls, seek):
        logging.info('Retrieving loudness data...')
        loudnorm_cmd = f'ffmpeg {seek.get_seek_string()} ' \
                       f'-map 0:a:{seek.source_file.selected_audio_stream} ' \
                       f'-af {LoudnormFilter.get_first_pass_filters(seek)} ' \
                       f'-vn -sn -dn -f null /dev/null'
        loudnorm_args = shlex.split(loudnorm_cmd)
        loudnorm_output = subprocess.check_output(loudnorm_args, stderr=subprocess.STDOUT).decode('utf-8').strip()
        loudnorm_stats = re.search('^{[^}]*}$', loudnorm_output, re.MULTILINE)
        loudnorm_stats = json.loads(loudnorm_stats.group(0))

        logging.debug(
            f'[Loudnorm.__init__] input_i: \'{loudnorm_stats["input_i"]}\', '
            f'input_lra: \'{loudnorm_stats["input_lra"]}\', '
            f'input_tp: \'{loudnorm_stats["input_tp"]}\', '
            f'input_thresh: \'{loudnorm_stats["input_thresh"]}\', '
            f'target_offset: \'{loudnorm_stats["target_offset"]}\'')

        return cls(loudnorm_stats['input_i'],
                   loudnorm_stats['input_lra'],
                   loudnorm_stats['input_tp'],
                   loudnorm_stats['input_thresh'],
                   loudnorm_stats['target_offset'])

    # The audio normalization filter argument for our encode
    def get_normalization_filter(self):
        return f'loudnorm=I=-16:LRA=20:TP=-1:dual_mono=true:linear=true:' \
               f'measured_I={self.input_i}:' \
               f'measured_LRA={self.input_lra}:' \
               f'measured_TP={self.input_tp}:' \
               f'measured_thresh={self.input_thresh}:' \
               f'offset={self.target_offset}'

    @staticmethod
    def get_first_pass_filters(seek):
        audio_filters = []
        seek.source_file.apply_audio_resampling(audio_filters)
        audio_filters.append(LoudnormFilter.first_pass_filter)
        return ','.join(audio_filters)
