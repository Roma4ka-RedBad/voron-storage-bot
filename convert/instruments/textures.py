import platform
from pathlib import Path
from subprocess import run, STDOUT, PIPE

from logic_objects.file import FileObject
from .base import Base


class Textures(Base):
    def __init__(self, file: FileObject, result_dir: str):
        super().__init__(file, result_dir)
        self.pvrtextool = Path("convert/instruments/pvrtextools/" +'pvrtextool.exe'
                               if platform.system() == 'Windows' else 'pvrtextool').absolute()

    async def convert_to(self, to_format: str):
        methods = {
            'png': '{pvrtextool} -i {file_name} -f R8G8B8A8 -d {out_file} -o {temp_pvr_file}',
            'jpg': '{pvrtextool} -i {file_name} -f R8G8B8 -d {out_file} -o {temp_pvr_file}',
            'pvr': '{pvrtextool} -i {file_name} -f PVRTC2_4,UBN,lRGB -q pvrtcnormal -pot + -o {out_file}',
            'ktx': '{pvrtextool} -i {file_name} -f ETC1,UBN,lRGB -q etcfast -o {out_file}',
            }

        if to_format in ['png', 'jpg', 'ktx', 'pvr']:
            output = run(
                methods[to_format]
                .format(
                    pvrtextool=str(self.pvrtextool),
                    file_name=str(self.file.path.absolute()),
                    out_file=str(self.get_new_filename(to_format).absolute()),
                    temp_pvr_file=str(self.file.path.absolute().parent / 'temp.pvr'))
                .split(),
                stdout=PIPE, stderr=STDOUT, text=True)

            if output.returncode == 0:
                return {'converted': True, 'path': self.get_new_filename(to_format)}
            else:
                return {'converted': False, 'error': output.stdout}
        elif to_format == 'sc':
            return {'converted': False, 'error': 'Method is unavailable'}

        return {'converted': False, 'error': 'Unsupported convert method'}
