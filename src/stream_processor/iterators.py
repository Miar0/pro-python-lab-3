from collections.abc import Iterable, Iterator
from itertools import accumulate, chain, pairwise

from .models import RoomRecord


class RoomPriceRangeIterator:
    """
    Власний Iterator-клас (реалізує __iter__ та __next__).
    Ітерується по списку номерів, повертаючи лише ті, які потрапляють у заданий ціновий діапазон.
    """

    def __init__(self, rooms: list[RoomRecord], min_price: float, max_price: float) -> None:
        self._rooms = rooms
        self._min_price = min_price
        self._max_price = max_price
        self._index = 0

    def __iter__(self) -> "RoomPriceRangeIterator":
        return self

    def __next__(self) -> RoomRecord:
        while self._index < len(self._rooms):
            current_room = self._rooms[self._index]
            self._index += 1
            if self._min_price <= current_room.price <= self._max_price:
                return current_room

        raise StopIteration


class HotelRoomCatalog:
    """
    Власний Iterable-контейнер.
    Розділяє логіку збереження колекції та створення незалежного ітератора.
    """

    def __init__(self, rooms: list[RoomRecord]) -> None:
        self.rooms = rooms

    def filter_by_price(self, min_price: float, max_price: float) -> RoomPriceRangeIterator:
        return RoomPriceRangeIterator(self.rooms, min_price, max_price)

    def __iter__(self) -> Iterator[RoomRecord]:
        return iter(self.rooms)


def calculate_cumulative_revenue(rooms: Iterable[RoomRecord]) -> Iterator[float]:
    """
    Демонстрація itertools.accumulate:
    Потокове обчислення накопичувальної виручки від заброньованих номерів.
    """
    booked_prices = (room.price for room in rooms if room.status == "booked")
    return accumulate(booked_prices)


def calculate_price_deltas(rooms: Iterable[RoomRecord]) -> Iterator[tuple[int, int, float]]:
    """
    Демонстрація itertools.pairwise:
    Потоковий розрахунок різниці в ціні між сусідніми номерами у потоці.
    Повертає кортеж: (номер_1, номер_2, delta_ціни).
    """
    return (
        (prev_room.room_number, curr_room.room_number, round(curr_room.price - prev_room.price, 2))
        for prev_room, curr_room in pairwise(rooms)
    )


def combine_room_sources(*sources: Iterable[RoomRecord]) -> Iterator[RoomRecord]:
    """
    Демонстрація itertools.chain:
    Об'єднання декількох незалежних потоків даних або конвеєрів в один.
    """
    return chain(*sources)