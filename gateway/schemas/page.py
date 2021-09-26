from typing import Generic, TypeVar, List

from pydantic.generics import GenericModel

DataT = TypeVar("DataT")


class Page(GenericModel, Generic[DataT]):
    results: List[DataT]
    total_count: int
    offset: int
