from ._source_file import SourceFile


# The seek information for our encode
class Seek:
    def __init__(self, source_file: SourceFile, ss, to, output_name, new_audio_filter):
        self.source_file = source_file
        self.ss = ss
        self.to = to
        self.output_name = output_name
        self.new_audio_filter = new_audio_filter

    # The seek string arguments for our encode
    def get_seek_string(self) -> str:
        # Slow seek for m2ts files
        if self.source_file.file.endswith(".m2ts"):
            if len(self.ss) > 0 and len(self.to) > 0:
                return f'-i "{self.source_file.file}" -ss {self.ss} -to {self.to}'
            elif len(self.ss) > 0:
                return f'-i "{self.source_file.file}" -ss {self.ss}'
        # Fast seek for all other files
        elif len(self.ss) > 0 and len(self.to) > 0:
            return f'-ss {self.ss} -to {self.to} -i "{self.source_file.file}"'
        elif len(self.ss) > 0:
            return f'-ss {self.ss} -i "{self.source_file.file}"'
        elif len(self.to) > 0:
            return f'-i "{self.source_file.file}" -to {self.to}'
        else:
            return f'-i "{self.source_file.file}"'
