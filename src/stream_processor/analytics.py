from collections import Counter
from collections.abc import Iterable
from typing import Optional

from .models import RoomRecord


def calculate_hotel_statistics(rooms: Iterable[RoomRecord]) -> dict:
    """
    Потокове обчислення ключових метрик готелю:
    - загальна кількість кімнат;
    - кількість заброньованих та вільних;
    - загальна потенційна виручка (сума всіх цін);
    - виручка від поточних бронювань;
    - середня ціна номера;
    - розподіл номерів за типами.
    """
    total_rooms = 0
    booked_count = 0
    available_count = 0
    total_potential_revenue = 0.0
    current_booked_revenue = 0.0
    type_counts = Counter()

    for room in rooms:
        total_rooms += 1
        total_potential_revenue += room.price
        type_counts[room.room_type] += 1

        if room.status == "booked":
            booked_count += 1
            current_booked_revenue += room.price
        elif room.status == "available":
            available_count += 1

    average_price = (total_potential_revenue / total_rooms) if total_rooms else 0.0

    return {
        "total_rooms": total_rooms,
        "booked_count": booked_count,
        "available_count": available_count,
        "total_potential_revenue": round(total_potential_revenue, 2),
        "current_booked_revenue": round(current_booked_revenue, 2),
        "average_price": round(average_price, 2),
        "room_types": dict(type_counts),
    }


def find_cheapest_available_room(
    rooms: Iterable[RoomRecord],
) -> Optional[RoomRecord]:
    """
    Потоковий пошук найдешевшого вільного номера без завантаження всіх номерів у пам'ять.
    """
    cheapest: Optional[RoomRecord] = None

    for room in rooms:
        if room.status == "available":
            if cheapest is None or room.price < cheapest.price:
                cheapest = room

    return cheapest