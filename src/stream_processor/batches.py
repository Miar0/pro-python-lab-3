from collections.abc import Iterable, Iterator
from itertools import islice

from .models import RoomRecord


def batched_rooms(
    rooms: Iterable[RoomRecord], batch_size: int
) -> Iterator[list[RoomRecord]]:
    """
    Потокове розбиття послідовності на батчі фіксованого розміру
    за допомогою itertools.islice.
    """
    iterator = iter(rooms)
    while True:
        batch = list(islice(iterator, batch_size))
        if not batch:
            return
        yield batch