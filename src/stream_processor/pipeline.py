from collections.abc import Iterator
from pathlib import Path
from typing import Optional

from .filters import (
    filter_by_max_price,
    filter_by_status,
    filter_by_type,
    validate_rooms,
)
from .models import RoomRecord
from .parsers import parse_csv_rows
from .readers import read_lines
from .transformations import normalize_records


def build_pipeline(
    path: Path,
    status: Optional[str] = None,
    room_type: Optional[str] = None,
    max_price: Optional[float] = None,
) -> Iterator[RoomRecord]:
    """
    Побудова ледачого потокового конвеєра:
    1. Потокове читання з диску (read_lines).
    2. Порядковий CSV-парсинг (parse_csv_rows).
    3. Валідація коректності даних (validate_rooms).
    4. Нормалізація полів (normalize_records).
    5. Опціональна фільтрація за статусом, типом та ціною.
    """
    lines = read_lines(path)
    rows = parse_csv_rows(lines)
    valid_rooms = validate_rooms(rows)
    normalized = normalize_records(valid_rooms)

    stream = normalized

    if status is not None:
        stream = filter_by_status(stream, status)

    if room_type is not None:
        stream = filter_by_type(stream, room_type)

    if max_price is not None:
        stream = filter_by_max_price(stream, max_price)

    return stream