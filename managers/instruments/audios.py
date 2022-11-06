from pydub import AudioSegment

from logic_objects import FileObject, Metadata
from managers.instruments.base import Base

DEFAULT_SAMPLE_RATE = 22050
DEFAULT_BITRATE = '90k'


class Audios(Base):
    def __init__(self, file: FileObject, result_dir: str, metadata: Metadata):
        super().__init__(file, result_dir)
        self.metadata = metadata

    async def convert_to(self, to_format: str):
        audio = AudioSegment.from_file(self.file.path)
        if self.metadata.bitrate:
            self.metadata.bitrate = f'{self.metadata.bitrate}k'

        if self.metadata.compress:
            audio = audio.set_frame_rate(self.metadata.sample_rate or DEFAULT_SAMPLE_RATE)
            audio.export(self.get_new_filename(to_format),
                         format=to_format,
                         bitrate=self.metadata.bitrate or DEFAULT_BITRATE)
        else:
            audio.export(self.get_new_filename(to_format), format=to_format)

        return {'converted': True, 'path': self.get_new_filename(to_format)}
