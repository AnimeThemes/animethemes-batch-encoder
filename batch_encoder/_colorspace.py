import enum
import logging


# The Colorspace Enumerated List
# Parse color data from file to provide arguments for the encoded file
class Colorspace(enum.Enum):
    def __new__(cls, colorspace, color_primaries, color_trc):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        obj.colorspace = colorspace
        obj.color_primaries = color_primaries
        obj.color_trc = color_trc
        return obj

    HD = ('bt709', 'bt709', 'bt709')
    NTSC = ('smpte170m', 'smpte170m', 'smpte170m')
    PAL = ('bt470bg', 'bt470bg', 'gamma28')

    # The color data arguments for our encode
    def get_args(self):
        return f'-colorspace {self.colorspace} -color_primaries {self.color_primaries} -color_trc {self.color_trc}'

    @staticmethod
    def value_of(source_file):
        # Method 1: Carry over color data from source if specified
        source_colorspace = source_file.video_format['streams'][0].get('color_space', '')
        source_color_primaries = source_file.video_format['streams'][0].get('color_primaries', '')
        source_color_trc = source_file.video_format['streams'][0].get('color_transfer', '')
        logging.debug(
            f'[Colorspace.value_of] source_colorspace: {source_colorspace}, '
            f'source_color_primaries: {source_color_primaries}, '
            f'source_color_trc: {source_color_trc}')

        for colorspace_candidate in Colorspace:
            if (
                    source_colorspace == colorspace_candidate.colorspace
                    or source_color_primaries == colorspace_candidate.color_primaries
                    or source_color_trc == colorspace_candidate.color_trc
            ):
                logging.debug(f'[Colorspace.value_of] carryover colorspace \'{colorspace_candidate.name}\' from source')
                return colorspace_candidate

        # Method 2: Infer color date from source file resolution
        resolution = int(source_file.video_format['streams'][0]['height'])

        if resolution >= 720:
            logging.debug(f'[Colorspace.value_of] colorspace: \'{Colorspace.HD.name}\', resolution: \'{resolution}\'')
            return Colorspace.HD
        elif resolution >= 576:
            logging.debug(f'[Colorspace.value_of] colorspace: \'{Colorspace.PAL.name}\', resolution: \'{resolution}\'')
            return Colorspace.PAL
        else:
            logging.debug(f'[Colorspace.value_of] colorspace: \'{Colorspace.NTSC.name}\', resolution: \'{resolution}\'')
            return Colorspace.NTSC
