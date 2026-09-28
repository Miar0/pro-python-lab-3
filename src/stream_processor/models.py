from typing import NamedTuple


class RoomRecord(NamedTuple):
    room_number: int
    room_type: str
    price: float
    status: str
    client: str