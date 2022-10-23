from logic_objects import FileObject


async def get_converts_by_file(file: FileObject):
    if archive := file.get_archive():
        archive_converts = {
            "archive_files": [
                {
                    "name": file.origin.filename,
                    "short_name": file.get_shortname(),
                    "converts": file.get_available_converts()
                }
                for file in archive.get_files() if file.get_available_converts()
            ],
            "archive_converts": archive.get_available_converts()
        }

        if len(archive_converts['archive_files']):
            return archive_converts
    else:
        return file.get_available_converts()


async def create_response(status: bool, content=None, error_msg: str = None):
    response = {
        "status": status
    }

    if status:
        response['content'] = content
    else:
        response['error_msg'] = error_msg

    return response

