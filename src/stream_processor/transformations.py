from collections.abc import Iterable, Iterator

from .models import RoomRecord


def normalize_records(rooms: Iterable[RoomRecord]) -> Iterator[RoomRecord]:
    """
    Потокова нормалізація даних:
    - очищення та форматування прізвища клієнта.
    """
    for room in rooms:
        cleaned_client = room.client.strip().title() if room.client else ""
        yield room._replace(client=cleaned_client)