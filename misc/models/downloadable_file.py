from pydantic import BaseModel


class FileModel(BaseModel):
    name: str
    main_dir: str
    user_dir: str
    url: str
    ext: str
    size: int
