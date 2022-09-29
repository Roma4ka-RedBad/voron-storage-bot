from copy import copy
from models import FileObject, ZIPObject

available_formats = {
    '3D': ['scw', 'glb', 'dae', 'obj', 'fbx'],
    '2D': ['ktx', 'pvr', 'png', 'jpg', 'sc'],
    'CSV': ['compress', 'decompress', 'csv'],
    '2D_ANIM': ['sc', 'fla']
}


async def get_task_for_format(file: FileObject):
    if file.is_archive():
        formats = {}
        zip_archive = ZIPObject(file, 'r')
        if zip_archive.count() <= 100:
            for zip_file in zip_archive.get_files():
                formats[zip_file.origin.filename] = [copy(available_formats[group]) for group in available_formats if
                                                     zip_file.get_format() in available_formats[group]]

                if formats[zip_file.origin.filename]:
                    formats[zip_file.origin.filename] = formats[zip_file.origin.filename][0]
                    formats[zip_file.origin.filename].remove(zip_file.get_format())
        return formats

    formats = [copy(available_formats[group]) for group in available_formats if
               file.get_format() in available_formats[group]]
    formats[0].remove(file.get_format())
    return formats[0]


async def create_response(status: bool, content=None, error_msg: str = None):
    response = {
        "status": status
    }

    if status:
        response['content'] = content
    else:
        response['error_msg'] = error_msg

    return response
