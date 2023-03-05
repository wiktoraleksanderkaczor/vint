"""Database model for the database service."""
from pathlib import PurePosixPath
from typing import Callable, List

from database.models.objects import JSON
from storage.interface.client import StorageClientInterface
from storage.models.object.content import ObjectContentInfo, ObjectData
from storage.models.object.models import Object
from storage.models.object.path import StorageKey


class Database:
    def insert(self, key: str, value: JSON) -> None:
        path = self.prefix.join(key)
        # obj = Object.from_basemodel(name, value)
        data = ObjectData(__root__=value.to_bytes())
        content = ObjectContentInfo.from_data(data=data)
        obj = Object(name=path, content=content)
        self.storage.put(obj, data)

    def get(self, key: str) -> JSON:
        path = self.prefix.join(key)
        if key not in self:
            raise KeyError(f"Key '{key}' does not exist")
        data = self.storage.get(path).__root__
        return JSON.parse_raw(data)

    def __contains__(self, key: str) -> bool:
        path = self.prefix.join(key)
        return path in self.storage

    def delete(self, key: str) -> None:
        path = self.prefix.join(key)
        if key in self:
            self.storage.remove(path)

    def items(self) -> List[str]:
        return [item.path.stem for item in self.storage.list(self.prefix)]

    def select(self, selector: Callable[[JSON], bool]) -> List[JSON]:
        records = []
        for key in self.items():
            record = self.get(key)
            if selector(record):
                records.append(record)
        return records

    def merge(self, key: str, head: JSON) -> None:
        base = self.get(key)
        new = JSON.merge(base, head)
        self.insert(key, new)

    def __init__(self, storage: StorageClientInterface, name: StorageKey):
        path = PurePosixPath(f"partitions/{name}")
        self.prefix: StorageKey = StorageKey(storage=storage.name, path=path)
        self.storage: StorageClientInterface = storage
        # self.lock: Lock = DatabaseLock(self.storage, self.prefix, ".lock")
