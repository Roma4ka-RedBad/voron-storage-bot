from blueprints import documents
from blueprints.only_same_files import audio, compressed_photos
from blueprints.public import common, profile, get_server_files

labelers = [common.labeler,
            profile.labeler,
            audio.convert_labeler,
            compressed_photos.convert_labeler,
            documents.labeler
            ]

__all__ = [
    'common',
    'profile',
    'audio',
    'compressed_photos',
    'documents',
    'get_server_files'
]
