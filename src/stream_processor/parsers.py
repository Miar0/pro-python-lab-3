import csv
from collections.abc import Iterable, Iterator


def parse_csv_rows(lines: Iterable[str]) -> Iterator[dict[str, str]]:
    """Потоковий парсинг рядків CSV у словники."""
    reader = csv.DictReader(lines)
    yield from reader