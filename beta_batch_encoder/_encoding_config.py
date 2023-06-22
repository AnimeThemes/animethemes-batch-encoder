from ._bitrate_mode import BitrateMode


class EncodingConfig:
    # Config keys
    config_allowed_filetypes = 'AllowedFileTypes'
    config_encoding_modes = 'EncodingModes'
    config_crfs = 'CRFs'
    config_threads = 'Threads'
    config_limit_size_enable = 'LimitSizeEnable'
    config_alternate_source_files = 'AlternateSourceFiles'
    config_create_preview = 'CreatePreview'
    config_include_unfiltered = 'IncludeUnfiltered'

    # Default Config keys
    config_default_video_stream = 'DefaultVideoStream'
    config_default_audio_stream = 'DefaultAudioStream'

    # Default config values
    default_allowed_filetypes = '.avi,.m2ts,.mkv,.mp4,.wmv'
    default_encoding_modes = f'{BitrateMode.VBR.name},{BitrateMode.CBR.name}'
    default_crfs = '12,15,18,21,24'
    default_threads = '4'
    default_limit_size_enable = True
    default_alternate_source_files = False
    default_create_preview = False
    default_include_unfiltered = True
    default_video_filters = {'filtered': 'hqdn3d=0:0:3:3,gradfun,unsharp',
                             'lightdenoise': 'hqdn3d=0:0:3:3',
                             'heavydenoise': 'hqdn3d=1.5:1.5:6:6',
                             'unsharp': 'unsharp'}

    def __init__(self, allowed_filetypes, encoding_modes, crfs, threads, limit_size_enable, alternate_source_files, create_preview, include_unfiltered, video_filters, default_video_stream,
                 default_audio_stream):
        self.allowed_filetypes = allowed_filetypes
        self.encoding_modes = encoding_modes
        self.crfs = crfs
        self.threads = threads
        self.limit_size_enable = limit_size_enable
        self.alternate_source_files = alternate_source_files
        self.create_preview = create_preview
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
        threads = config['Encoding'].get(EncodingConfig.config_threads,
                                         EncodingConfig.default_threads)
        limit_size_enable = config.getboolean('Encoding', EncodingConfig.config_limit_size_enable, fallback=EncodingConfig.default_limit_size_enable)
        alternate_source_files = config.getboolean('Encoding', EncodingConfig.config_alternate_source_files, fallback=EncodingConfig.default_alternate_source_files)
        create_preview = config.getboolean('Encoding', EncodingConfig.config_create_preview, fallback=EncodingConfig.default_create_preview)
        include_unfiltered = config.getboolean('Encoding', EncodingConfig.config_include_unfiltered,
                                               fallback=EncodingConfig.default_include_unfiltered)
        video_filters = config.items('VideoFilters', EncodingConfig.default_video_filters)

        default_video_stream = config['Encoding'].get(EncodingConfig.config_default_video_stream)
        default_audio_stream = config['Encoding'].get(EncodingConfig.config_default_audio_stream)

        return cls(allowed_filetypes, encoding_modes, crfs, threads, limit_size_enable, alternate_source_files, create_preview, include_unfiltered, video_filters, default_video_stream,
                   default_audio_stream)

    def get_default_stream(self, stream_type):
        if stream_type == 'video':
            return self.default_video_stream
        elif stream_type == 'audio':
            return self.default_audio_stream
        return None