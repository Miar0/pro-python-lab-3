from itertools import islice
from pathlib import Path

from .analytics import calculate_hotel_statistics, find_cheapest_available_room
from .batches import batched_rooms
from .pipeline import build_pipeline


def main() -> None:
    data_path = Path("data/bookings.csv")

    if not data_path.exists():
        print(f"Помилка: файл {data_path} не знайдено.")
        print("Будь ласка, спочатку згенеруйте його за допомогою generate_data.py")
        return

    print("=" * 60)
    print("ДЕМОНСТРАЦІЯ ПОТОКОВОГО КОНВЕЄРА (ВАРІАНТ 8)")
    print("=" * 60)

    # 1. Отримання перших 5 вільних номерів через islice
    print("\n1. Перші 5 вільних номерів (через itertools.islice):")
    available_pipeline = build_pipeline(data_path, status="available")
    first_5_available = list(islice(available_pipeline, 5))
    for room in first_5_available:
        print(f"   Кімната #{room.room_number:04d} | {room.room_type:<8} | Ціна: {room.price:>7.2f} грн")

    # 2. Пошук найдешевшого вільного номера (однопрохідний lazy search)
    print("\n2. Пошук найдешевшого вільного номера:")
    cheapest_room = find_cheapest_available_room(build_pipeline(data_path))
    if cheapest_room:
        print(f"   Знайдено: Кімната #{cheapest_room.room_number} ({cheapest_room.room_type}) "
              f"за ціною {cheapest_room.price:.2f} грн")

    # 3. Розрахунок потенційної та поточної виручки, кількості бронювань
    print("\n3. Потокова аналітика готелю:")
    stats = calculate_hotel_statistics(build_pipeline(data_path))
    print(f"   Всього валідних номерів : {stats['total_rooms']}")
    print(f"   Заброньовано             : {stats['booked_count']}")
    print(f"   Вільних номерів          : {stats['available_count']}")
    print(f"   Поточна виручка          : {stats['current_booked_revenue']:,.2f} грн")
    print(f"   Потенційна виручка       : {stats['total_potential_revenue']:,.2f} грн")
    print(f"   Середня вартість доби    : {stats['average_price']:.2f} грн")
    print("   Розподіл за типами:")
    for room_type, count in stats["room_types"].items():
        print(f"     - {room_type:<8}: {count} кімнат")

    # 4. Демонстрація генераторного виразу (Generator Expression)
    print("\n4. Обчислення виручки заброньованих люксів (Deluxe) через generator expression:")
    deluxe_pipeline = build_pipeline(data_path, status="booked", room_type="Deluxe")
    deluxe_prices = (room.price for room in deluxe_pipeline)
    total_deluxe_revenue = sum(deluxe_prices)
    print(f"   Виручка від номерів Deluxe: {total_deluxe_revenue:,.2f} грн")

    # 5. Демонстрація пакетної обробки (Batch Processing)
    print("\n5. Демонстрація батчингу (перші 2 батчі по 3 елементи):")
    batch_pipeline = build_pipeline(data_path, status="available")
    for batch_idx, batch in enumerate(islice(batched_rooms(batch_pipeline, batch_size=3), 2), start=1):
        print(f"   [Батч #{batch_idx}] Кількість елементів: {len(batch)}")
        for r in batch:
            print(f"     -> Кімната #{r.room_number} ({r.room_type}) - {r.price} грн")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()