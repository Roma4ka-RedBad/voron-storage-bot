from pydub import AudioSegment

from logic_objects.file import FileObject
from .base import Base

DEFAULT_SAMPLE_RATE = 22050
DEFAULT_BITRATE = 90


class Audios(Base):
    def __init__(
                self,
                file: FileObject,
                process_dir: str,
                result_dir: str,
                compress: bool = False,
                bitrate: int = DEFAULT_BITRATE,
                sample_rate: int = DEFAULT_BITRATE):

        super().__init__(file, process_dir, result_dir)
        self.bitrate = bitrate
        self.compress = compress
        self.sample_rate = sample_rate

    async def convert_to(self, to_format: str):
        audio = AudioSegment().from_file(
            self.process_dir + self.file.get_destination(
                only_shortname=True))
        if self.compress:
            audio = audio.set_frame_rate(self.sample_rate)
            audio.export(self.get_new_filename(to_format), format=to_format, bitrate=self.bitrate)
        else:
            audio.export(self.get_new_filename(to_format), format=to_format)

        return self.get_new_filename(to_format)
