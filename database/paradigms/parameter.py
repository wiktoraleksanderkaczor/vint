from database.models.database import Database
from storage.models.client import StorageClient
from storage.models.objects import ObjectID


class Parameter(Database):
    def __init__(self, storage: StorageClient, name: ObjectID) -> None:
        super().__init__(storage, name)
