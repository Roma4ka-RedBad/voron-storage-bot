from copy import copy
from models import FileObject, ArchiveObject

available_converts = {
    '3D': ['scw', 'glb', 'dae', 'obj', 'fbx'],
    '2D': ['ktx', 'pvr', 'png', 'jpg', 'sc'],
    'CSV': ['compress', 'decompress', 'csv'],
    '2D_ANIM': ['sc', 'fla']
}


async def get_converts_for_format(file: FileObject):
    if file.is_archive():
        converts = []
        zip_archive = ArchiveObject(file, 'r')
        if zip_archive.count() <= 100:
            for zip_file in zip_archive.get_files():
                if not zip_file.is_dir():
                    zip_file_object = {
                        'name': zip_file.origin.filename,
                        'short_name': zip_file.get_shortname(),
                        'converts': [copy(available_converts[group]) for group in
                                     available_converts if
                                     zip_file.get_format() in available_converts[group]]
                    }
                    if zip_file_object['converts']:
                        zip_file_object['converts'] = zip_file_object['converts'][0]
                        zip_file_object['converts'].remove(zip_file.get_format())
                        converts.append(zip_file_object)
        return converts

    converts = [copy(available_converts[group]) for group in available_converts if
                file.get_format() in available_converts[group]]
    if converts:
        converts = converts[0]
        converts.remove(file.get_format())
    return converts


async def create_response(status: bool, content=None, error_msg: str = None):
    response = {
        "status": status
    }

    if status:
        response['content'] = content
    else:
        response['error_msg'] = error_msg

    return response
