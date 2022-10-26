from pydub import AudioSegment

from logic_objects import FileObject, Metadata
from .base import Base

DEFAULT_SAMPLE_RATE = 22050
DEFAULT_BITRATE = 90


class Audios(Base):
    def __init__(self, file: FileObject, process_dir: str, result_dir: str, metadata: Metadata):
        super().__init__(file, process_dir, result_dir)
        self.metadata = metadata

    async def convert_to(self, to_format: str):
        audio = AudioSegment().from_file(
            self.process_dir + self.file.get_destination(only_name=True)
        )
        if self.metadata.compress:
            audio = audio.set_frame_rate(self.metadata.sample_rate or DEFAULT_SAMPLE_RATE)
            audio.export(self.get_new_filename(to_format), format=to_format, bitrate=self.metadata.bitrate or DEFAULT_BITRATE)
        else:
            audio.export(self.get_new_filename(to_format), format=to_format)

        return self.get_new_filename(to_format)
