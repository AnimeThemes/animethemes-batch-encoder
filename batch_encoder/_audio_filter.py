import enum


# The Audio Filter Enumerated List
# Convert filter values to their strings
class AudioFilter(enum.Enum):
    def __new__(cls, name, toText):
        obj = object.__new__(cls)
        obj.toText = toText
        return obj

    FADE_IN = ("Fade In", lambda value: f"afade=d={value}:curve=exp")
    FADE_OUT = ("Fade Out", lambda start, value: f"afade=t=out:st={start}:d={value}")
    MUTE = (
        "Mute",
        lambda start, end: f"volume=enable='between(t,{start},{end})':volume=0",
    )
    CUSTOM = ("Custom", lambda text: text)

    # Get the object to prompt to the user
    @classmethod
    def get_obj(self):
        return {
            "Exit": False,
            self.CUSTOM._value_[0]: "",
            self.FADE_IN._value_[0]: 0,
            self.FADE_OUT._value_[0]: {"Start Time": 0, "Exp": 0},
            self.MUTE._value_[0]: {"Start Time": 0, "End Time": 0},
        }
