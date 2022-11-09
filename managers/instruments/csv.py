from sc_compression import decompress, compress, signatures
from managers.instruments.base import Base
from logic_objects.file import FileObject


class Csv(Base):
    def __init__(self, file: FileObject, result_dir: str):
        super().__init__(file, result_dir)

    async def convert_to(self, to_format: str):
        if to_format == 'compress':
            buffer = compress(self.file.open('rb').read(), signatures.Signatures.LZMA)
            file = FileObject.create(self.get_new_filename('csv', '_compressed'), self.file.config, buffer)
        else:
            buffer = decompress(self.file.open('rb').read())
            file = FileObject.create(self.get_new_filename('csv', '_decompressed'), self.file.config, buffer[0])

        return {'converted': True, 'path': str(file.path)}
