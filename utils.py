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
        converts = {
            'files': [],
            'converts': []
        }
        archive = ArchiveObject(file, 'r')
        if archive.count() <= 100:
            for archive_file in archive.get_files():
                if not archive_file.is_dir():
                    archive_file_object = {
                        'name': archive_file.origin.filename,
                        'short_name': archive_file.get_shortname(),
                        'converts': [copy(available_converts[group]) for group in
                                     available_converts if
                                     archive_file.get_format() in available_converts[group]]
                    }
                    if archive_file_object['converts']:
                        archive_file_object['converts'] = archive_file_object['converts'][0]
                        archive_file_object['converts'].remove(archive_file.get_format())
                        converts['files'].append(archive_file_object)
                        converts['converts'] = list(set(converts['converts'] + archive_file_object['converts']))
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
