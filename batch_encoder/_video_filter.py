from enum import Enum


# The Video Filter Enumerated List
# Set video filters
class VideoFilter(Enum):
    def __new__(cls, value, name):
        obj = object.__new__(cls)
        return obj

    NO_FILTERS = ("No Filters", None)
    R720P = ("scale=-1:720", "720p")
    FILTERED_720P = ("scale=-1:720,hqdn3d=0:0:3:3,gradfun,unsharp", "filtered-720p")
    FILTERED = ("hqdn3d=0:0:3:3,gradfun,unsharp", "filtered")
    LIGHTDENOISE = ("hqdn3d=0:0:3:3", "lightdenoise")
    HEAVYDENOISE = ("hqdn3d=1.5:1.5:6:6", "heavydenoise")
    UNSHARP = ("unsharp", "unsharp")
    CUSTOM = ("custom", "Custom")

    # Get the object to prompt to the user
    @classmethod
    def get_obj(self):
        return {
            self.NO_FILTERS._value_[0]: self.NO_FILTERS._value_[1],
            self.R720P._value_[0]: self.R720P._value_[1],
            self.FILTERED_720P._value_[0]: self.FILTERED_720P._value_[1],
            self.FILTERED._value_[0]: self.FILTERED._value_[1],
            self.LIGHTDENOISE._value_[0]: self.LIGHTDENOISE._value_[1],
            self.HEAVYDENOISE._value_[0]: self.HEAVYDENOISE._value_[1],
            self.UNSHARP._value_[0]: self.UNSHARP._value_[1],
            self.CUSTOM._value_[0]: self.CUSTOM._value_[1],
        }
