from pathlib import Path
from subprocess import run, STDOUT, PIPE

from managers.instruments.base import Base
from logic_objects.file import FileObject


class Models(Base):
    def __init__(self, file: FileObject, result_dir: str):
        super().__init__(file, result_dir)
        self.daniilnull = Path("managers/instruments/modeltools/SCW.jar").absolute()

    async def convert_to(self, to_format: str):
        methods = {
            'scw': 'java -jar {daniilnull} dae2scw {file_name} {animation_file}',
            'dae': 'java -jar {daniilnull} scw2dae {file_name} {animation_file}'
        }

        if to_format in ['scw', 'dae']:
            output = run(
                methods[to_format].format(
                    daniilnull=str(self.daniilnull),
                    file_name=str(self.file.path),
                    animation_file=''
                ).split(),
                stdout=PIPE, stderr=STDOUT, text=True)

            if output.returncode == 0:
                return {'converted': True, 'path': self.get_new_filename(to_format, use_any_dir=self.file.path.parent)}
            else:
                return {'converted': False, 'error': output.stdout, 'TID': "TID_ERROR"}
