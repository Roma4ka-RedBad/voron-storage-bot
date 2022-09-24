import zipfile
from copy import copy

available_formats = {
    '3D': ['scw', 'glb', 'dae', 'obj', 'fbx'],
    '2D': ['ktx', 'pvr', 'png', 'jpg', 'sc'],
    'CSV': ['compress', 'decompress', 'csv'],
    '2D_ANIM': ['sc', 'fla']
}


async def get_task_for_format(file_format: str, file_name: str = None):
    if file_format == 'zip':
        formats = {}
        files = zipfile.ZipFile(file_name, 'r').infolist()
        if len(files) <= 100:
            for file in files:
                file_format = file.filename.split('.')[-1]
                formats[file.filename] = [copy(available_formats[group]) for group in available_formats if file_format in available_formats[group]]
                formats[file.filename][0].remove(file_format)
            return formats
        else:
            return []

    formats = [copy(available_formats[group]) for group in available_formats if file_format in available_formats[group]]
    formats[0].remove(file_format)
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
