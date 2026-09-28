from collections.abc import Iterator
from pathlib import Path


def read_lines(path: Path) -> Iterator[str]:
    """Потокове читання рядків файлу за допомогою yield from."""
    with path.open("r", encoding="utf-8") as file:
        yield from file