from ._bitrate_mode import BitrateMode


class EncodingConfig:
    # Config keys
    config_allowed_filetypes = 'AllowedFileTypes'
    config_encoding_modes = 'EncodingModes'
    config_crfs = 'CRFs'
    config_include_unfiltered = 'IncludeUnfiltered'

    # Default Config keys
    config_default_video_stream = 'DefaultVideoStream'
    config_default_audio_stream = 'DefaultAudioStream'

    # Default config values
    default_allowed_filetypes = '.avi,.m2ts,.mkv,.mp4,.wmv'
    default_encoding_modes = f'{BitrateMode.VBR.name},{BitrateMode.CBR.name}'
    default_crfs = '12,15,18,21,24'
    default_include_unfiltered = True
    default_video_filters = {'filtered': 'hqdn3d=0:0:3:3,gradfun,unsharp',
                             'lightdenoise': 'hqdn3d=0:0:3:3',
                             'heavydenoise': 'hqdn3d=1.5:1.5:6:6',
                             'unsharp': 'unsharp'}

    def __init__(self, allowed_filetypes, encoding_modes, crfs, include_unfiltered, video_filters, default_video_stream,
                 default_audio_stream):
        self.allowed_filetypes = allowed_filetypes
        self.encoding_modes = encoding_modes
        self.crfs = crfs
        self.include_unfiltered = include_unfiltered
        self.video_filters = video_filters
        self.default_video_stream = default_video_stream
        self.default_audio_stream = default_audio_stream

    @classmethod
    def from_config(cls, config):
        allowed_filetypes = config['Encoding'].get(EncodingConfig.config_allowed_filetypes,
                                                   EncodingConfig.default_allowed_filetypes).split(',')
        encoding_modes = config['Encoding'].get(EncodingConfig.config_encoding_modes,
                                                EncodingConfig.default_encoding_modes).split(',')
        crfs = config['Encoding'].get(EncodingConfig.config_crfs, EncodingConfig.default_crfs).split(',')
        include_unfiltered = config.getboolean('Encoding', EncodingConfig.config_include_unfiltered,
                                               fallback=EncodingConfig.default_include_unfiltered)
        video_filters = config.items('VideoFilters', EncodingConfig.default_video_filters)

        default_video_stream = config['Encoding'].get(EncodingConfig.config_default_video_stream)
        default_audio_stream = config['Encoding'].get(EncodingConfig.config_default_audio_stream)

        return cls(allowed_filetypes, encoding_modes, crfs, include_unfiltered, video_filters, default_video_stream,
                   default_audio_stream)

    def get_default_stream(self, stream_type):
        if stream_type == 'video':
            return self.default_video_stream
        elif stream_type == 'audio':
            return self.default_audio_stream
        return None