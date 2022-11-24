import os
import platform
from pathlib import Path
from subprocess import run, STDOUT, PIPE
from random import randint
from utils import compress_to_archive

from logic_objects.file import FileObject
from managers.instruments.base import Base


class Textures(Base):
    def __init__(self, file: FileObject, result_dir: str):
        super().__init__(file, result_dir)
        self.pvrtextool = Path("managers/instruments/pvrtextools/" + 'pvrtextool.exe'
                               if platform.system() == 'Windows' else 'pvrtextool').absolute()
        self.xcoder = Path("managers/instruments/xcoder/index.js").absolute()

    async def convert_to(self, to_format: str):
        methods = {
            'png': '{pvrtextool} -i {file_name} -f R8G8B8A8 -d {out_file} -o {temp_pvr_file}',
            'jpg': '{pvrtextool} -i {file_name} -f R8G8B8 -d {out_file} -o {temp_pvr_file}',
            'pvr': '{pvrtextool} -i {file_name} -f PVRTC2_4,UBN,lRGB -q pvrtcnormal -pot + -o {out_file}',
            'ktx': '{pvrtextool} -i {file_name} -f ETC1,UBN,lRGB -q etcfast -o {out_file}',
            'sc_png': 'node {xcoder} decode {input_name} {output_path}',
            'png_sc': 'node {xcoder} encode {input_path} {output_name}'
        }
        '''if 'sc' in self.file.path.suffix:
            work_dir = self.file.path.parent / f'work{randint(1234, 56789)}/'
            work_dir.mkdir(parents=True, exist_ok=True)
            input_name = self.file.path.replace(
                work_dir / ('input' + self.file.path.suffix)).absolute()
            output = run(
                methods['sc_png'].format(
                    xcoder=self.xcoder,
                    input_name=input_name,
                    output_path=work_dir
                ).split(), stdout=PIPE, stderr=STDOUT, text=True
            )

            if output.returncode == 0:
                archive = await compress_to_archive(self.result_dir + self.file.path.name + '.zip',
                                                    file_paths=[file for file in os.listdir(work_dir / )])
                return {'converted': True, 'path': archive}
            else:
                return {'converted': False, 'error': output.stdout, 'TID': "TID_ERROR"}'''
        if to_format in ['png', 'jpg', 'ktx', 'pvr']:
            work_dir = self.file.path.parent / f'work{randint(1234, 56789)}/'
            work_dir.mkdir(parents=True, exist_ok=True)
            input_name = self.file.path.replace(
                work_dir / ('input' + self.file.path.suffix)).absolute()
            output_name = work_dir / ('output.' + to_format)
            output = run(
                methods[to_format].format(
                    pvrtextool=str(self.pvrtextool),
                    file_name=input_name,
                    out_file=output_name,
                    temp_pvr_file=str(self.file.path.absolute().parent / 'temp.pvr')
                ).split(), stdout=PIPE, stderr=STDOUT, text=True
            )

            if output.returncode == 0:
                output_name.replace(self.get_new_filename(to_format))
                return {'converted': True, 'path': self.get_new_filename(to_format)}
            else:
                return {'converted': False, 'error': output.stdout, 'TID': "TID_ERROR"}
        elif to_format == 'sc':
            return {'converted': False, 'error': '', 'TID': "TID_SNACKBAR_METHOD_IS_UNAVAILABLE"}
