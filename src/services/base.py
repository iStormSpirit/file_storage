from models.models import File as FileModel
from models.models import User as UserModel
from schemas.file import FileCreate
from schemas.user import UserCreate, UserUpdate

from .file import RepositoryDB as FileRepositoryDB
from .user import RepositoryDB as UserRepositoryDB


class RepositoryUser(UserRepositoryDB[UserModel, UserCreate, UserUpdate]):
    pass


user_crud = RepositoryUser(UserModel)


class RepositoryFile(FileRepositoryDB[FileModel, FileCreate]):
    pass


file_crud = RepositoryFile(FileModel)
