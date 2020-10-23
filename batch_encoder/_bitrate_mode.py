import enum


# The Bitrate Mode Enumerated List
# Bitrate Mode determines the rate control argument values for our commands
# Further Reading: https://developers.google.com/media/vp9/bitrate-modes
class BitrateMode(enum.Enum):
    def __new__(cls, value, first_pass_rate_control, second_pass_rate_control):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.first_pass_rate_control = first_pass_rate_control
        obj.second_pass_rate_control = second_pass_rate_control
        return obj

    # Constant Bitrate Mode
    CBR = (0, lambda cbr_bitrate, cbr_max_bitrate, crf: f'-b:v {cbr_bitrate} -maxrate {cbr_max_bitrate} -qcomp 0.3',
           lambda cbr_bitrate, cbr_max_bitrate,
           crf: f'-b:v {cbr_bitrate} -maxrate {cbr_max_bitrate} -bufsize 6000k -qcomp 0.3')
    # Variable Bitrate Mode / Constant Quality Mode
    VBR = (1, lambda cbr_bitrate, cbr_max_bitrate, crf: f'-crf {crf} -b:v 0 -qcomp 0.7',
           lambda cbr_bitrate, cbr_max_bitrate, crf: f'-crf {crf} -b:v 0 -qcomp 0.7')
    # Constrained Quality Mode
    CQ = (2, lambda cbr_bitrate, cbr_max_bitrate, crf: f'-crf {crf} -b:v {cbr_bitrate} -qcomp 0.7',
          lambda cbr_bitrate, cbr_max_bitrate, crf: f'-crf {crf} -b:v {cbr_bitrate} -qcomp 0.7')
