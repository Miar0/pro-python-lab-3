from collections.abc import Iterable, Iterator

from .models import RoomRecord

VALID_ROOM_TYPES = {"Standard", "Deluxe", "Suite", "Single", "Family"}
VALID_STATUSES = {"available", "booked"}


def validate_rooms(rows: Iterable[dict[str, str]]) -> Iterator[RoomRecord]:
    """
    Потокова валідація сирих даних CSV:
    - перевірка типу даних room_number та price;
    - ціна має бути строго додатною;
    - коректність типу кімнати та статусу бронювання.
    """
    for row in rows:
        try:
            room_number = int(row["room_number"])
            room_type = row["type"].strip()
            price = float(row["price"])
            status = row["status"].strip().lower()
            client = row["client"].strip()
        except (ValueError, TypeError, KeyError):
            continue

        if room_number <= 0 or price <= 0:
            continue

        if room_type not in VALID_ROOM_TYPES or status not in VALID_STATUSES:
            continue

        # Якщо номер заброньований, клієнт не може бути порожнім
        if status == "booked" and not client:
            continue

        yield RoomRecord(
            room_number=room_number,
            room_type=room_type,
            price=price,
            status=status,
            client=client,
        )


def filter_by_status(
    rooms: Iterable[RoomRecord], status: str
) -> Iterator[RoomRecord]:
    """Фільтрація за статусом: 'available' або 'booked'."""
    target_status = status.lower()
    for room in rooms:
        if room.status == target_status:
            yield room


def filter_by_type(
    rooms: Iterable[RoomRecord], room_type: str
) -> Iterator[RoomRecord]:
    """Lazy filter за типом номера (Standard, Deluxe тощо)."""
    target_type = room_type.strip().lower()
    for room in rooms:
        if room.room_type.lower() == target_type:
            yield room


def filter_by_max_price(
    rooms: Iterable[RoomRecord], max_price: float
) -> Iterator[RoomRecord]:
    """Lazy filter номерів за граничною ціною."""
    for room in rooms:
        if room.price <= max_price:
            yield room