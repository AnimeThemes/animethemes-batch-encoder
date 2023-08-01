import json
import logging
import os
import subprocess


# Abstraction of the source file from which we are producing our encodes
# We are prefetching properties of the source file audio/video streams to help determine encoding argument values
class SourceFile:
    format_args = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', '-show_format', '-show_chapters']

    def __init__(self, file, file_format, selected_video_stream, selected_audio_stream, video_format, audio_format):
        self.file = file
        self.file_format = file_format
        self.selected_video_stream = selected_video_stream
        self.selected_audio_stream = selected_audio_stream
        self.video_format = video_format
        self.audio_format = audio_format

    @classmethod
    def from_file(cls, file, encoding_config):
        video_file = None
        audio_file = None
        try:
            file_format = SourceFile.get_file_format(file)

            selected_video_stream = SourceFile.get_default_stream(file_format, 'video', encoding_config)
            if selected_video_stream is None:
                selected_video_stream = SourceFile.get_selected_stream(file_format, 'video')

            selected_audio_stream = SourceFile.get_default_stream(file_format, 'audio', encoding_config)
            if selected_audio_stream is None:
                selected_audio_stream = SourceFile.get_selected_stream(file_format, 'audio')

            logging.info('Retrieving extracted audio/video stream/format data...')

            video_file = '[Video]' + file
            logging.debug(f'[SourceFile.from_file] video_file: \'{video_file}\'')
            audio_file = '[Audio]' + file
            logging.debug(f'[SourceFile.from_file] audio_file: \'{audio_file}\'')

            demux_args = ['ffmpeg', '-i', file, '-v', 'quiet', '-y', '-sn', '-dn', '-map',
                          f'0:v:{selected_video_stream}', '-vcodec', 'copy', video_file, '-map',
                          f'0:a:{selected_audio_stream}', '-acodec', 'copy', audio_file]
            subprocess.call(demux_args)

            video_args = SourceFile.format_args + [video_file]
            video_format = subprocess.check_output(video_args).decode('utf-8')
            video_format = json.loads(video_format)

            os.remove(video_file)
            logging.debug(f'[SourceFile.from_file] video_file deleted: {not os.path.isfile(video_file)}')

            audio_args = SourceFile.format_args + [audio_file]
            audio_format = subprocess.check_output(audio_args).decode('utf-8')
            audio_format = json.loads(audio_format)

            os.remove(audio_file)
            logging.debug(f'[SourceFile.from_file] audio_file deleted: {not os.path.isfile(audio_file)}')

            return cls(file, file_format, selected_video_stream, selected_audio_stream, video_format, audio_format)
        except KeyboardInterrupt:
            logging.info('Attempting to delete temp files after keyboard interrupt')

            if os.path.isfile(video_file):
                os.remove(video_file)

            if os.path.isfile(audio_file):
                os.remove(audio_file)

            raise

    # Source file streams/formats
    @staticmethod
    def get_file_format(file):
        logging.info('Retrieving source file stream/format data...')
        format_args = SourceFile.format_args + [file]

        file_format = subprocess.check_output(format_args).decode('utf-8')

        return json.loads(file_format)

    # Get the number of streams of the codec type (audio/video)
    @staticmethod
    def get_stream_count(file_format, target_codec_type):
        count = 0

        for stream in file_format['streams']:
            if stream['codec_type'] == target_codec_type:
                count += 1

        logging.debug(f'[SourceFile.get_stream_count] target_codec_type: \'{target_codec_type}\', count: \'{count}\'')

        return count

    # Validate default stream selection before prompting the user to specify which stream to use
    @staticmethod
    def get_default_stream(file_format, stream_type, encoding_config):
        # Exit early if default stream is not set
        default_stream = encoding_config.get_default_stream(stream_type)
        if not default_stream:
            return None

        stream_count = SourceFile.get_stream_count(file_format, stream_type)
        try:
            default_stream = int(default_stream)
            if default_stream in range(stream_count):
                return default_stream
            logging.error(f'Default stream selection \'{default_stream}\' is invalid')
        except ValueError:
            logging.error(f'Default stream selection \'{default_stream}\' must be an integer')

        return None

    # If there exists more than one stream for a codec type (audio/video),
    # we want the user to specify which stream to use
    @staticmethod
    def get_selected_stream(file_format, stream_type):
        stream_count = SourceFile.get_stream_count(file_format, stream_type)
        if stream_count <= 1:
            return 0

        streams = range(stream_count)
        prompt_text = f'Select {stream_type} stream [0-{stream_count - 1}]: '
        while True:
            try:
                selected_stream = int(input(prompt_text))
                if selected_stream in streams:
                    return selected_stream
                logging.error('Stream selection is invalid')
            except ValueError:
                logging.error('Stream selection must be an integer')

    # If our source file audio stream is not a 2-channel stereo layout, we need to resample it before normalization
    def apply_audio_resampling(self, audio_filters):
        channels = int(self.audio_format['streams'][0].get('channels', 2))
        channel_layout = self.audio_format['streams'][0].get('channel_layout', 'stereo')
        if channels != 2 or channel_layout != 'stereo':
            audio_filters.append('aresample=ochl=stereo')
