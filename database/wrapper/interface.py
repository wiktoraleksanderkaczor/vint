"""
Interface for database wrapper.
"""
from typing import Any, List, Optional

from typing_extensions import Self

from database.models.query import Query
from database.superclass.client import DatabaseClient
from datamodel.data.model import Data
from network.superclass.wrapping import DistributedObjectProxy
from storage.interface.client import StorageClientInterface

# Text can be stored with a binary (k-tree?) tree and a number of binary values for which path to go
# Each text can then be reconstructed from the binary values
# Also, one can attach a counter to each binary value to determine how many times it is used


# Might need a huffman coding wrapper for text database
# It could be in the StorageClient for text MIME types ^
class DatabaseWrapper(DistributedObjectProxy, StorageClientInterface):
    def __init__(self, wrapped: DatabaseClient):
        super().__init__(wrapped)
        self.__wrapped__: DatabaseClient = wrapped  # typing fix

    def insert(self, key: str, value: Data) -> None:
        return self.__wrapped__.insert(key, value)

    def get(self, key: str, default: Any = None) -> Optional[Data]:
        return self.__wrapped__.get(key, default)

    def merge(self, key: str, head: Data, schema: Optional[Data]) -> None:
        return self.__wrapped__.merge(key, head, schema)

    def __contains__(self, key: str) -> bool:
        return key in self.__wrapped__

    def delete(self, key: str) -> None:
        return self.__wrapped__.delete(key)

    def items(self, prefix: Optional[str] = None) -> List[str]:
        return self.__wrapped__.items(prefix)

    def query(self, query: Query) -> List[Data]:
        return self.__wrapped__.query(query)

    def namespace(self, name: str) -> Self:
        return self.__class__(self.__wrapped__.namespace(name))

    @property
    def __dict__(self):
        # Might be needed for more correct behavior later, unknown if properly writable
        # merged = {}
        # merged.update(super().__dict__)
        # merged.update(self.__wrapped__.__dict__)
        return self.__wrapped__.__dict__
