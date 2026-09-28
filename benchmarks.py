import csv
import time
import tracemalloc
from pathlib import Path
from typing import Any, Callable

from generate_data import generate_dataset
from src.stream_processor.pipeline import build_pipeline


# --- Eager реалізація (матеріалізація списків у пам'яті) ---
def eager_processing(path: Path) -> dict[str, Any]:
    """Жадібна обробка: повне завантаження CSV та проміжних списків у RAM."""
    with path.open("r", encoding="utf-8") as file:
        reader = list(csv.DictReader(file))

    # Фільтрація валідних і вільних у списки
    valid = []
    for r in reader:
        try:
            r_num = int(r["room_number"])
            price = float(r["price"])
            status = r["status"].strip().lower()
            if r_num > 0 and price > 0 and status in ("available", "booked"):
                valid.append(
                    {
                        "room_number": r_num,
                        "type": r["type"],
                        "price": price,
                        "status": status,
                    }
                )
        except (ValueError, TypeError, KeyError):
            continue

    # Фільтрація списку лише вільних
    available = [r for r in valid if r["status"] == "available"]
    total_rev = sum(r["price"] for r in available)
    first_record = available[0] if available else None

    return {
        "count": len(available),
        "total_revenue": total_rev,
        "first": first_record,
    }


# --- Lazy реалізація (потоковий конвеєр) ---
def lazy_processing(path: Path) -> dict[str, Any]:
    """Ледача обробка: потокове проходження даних без великих проміжних колекцій."""
    pipeline = build_pipeline(path, status="available")
    count = 0
    total_rev = 0.0
    first_record = None

    for room in pipeline:
        if first_record is None:
            first_record = room
        count += 1
        total_rev += room.price

    return {
        "count": count,
        "total_revenue": total_rev,
        "first": first_record,
    }


# --- Early Termination дослідження ---
def eager_find_first(path: Path) -> dict | None:
    """Жадібний пошук першого результату: спочатку вантажимо все, потім беремо [0]."""
    with path.open("r", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    for r in rows:
        if r.get("status") == "available" and float(r.get("price", 0)) > 4500:
            return r
    return None


def lazy_find_first(path: Path) -> Any | None:
    """Ледачий пошук: зупиняється на першому ж збігу, не читаючи решту файлу."""
    pipeline = build_pipeline(path, status="available", max_price=5000.0)
    for room in pipeline:
        if room.price > 4500:
            return room
    return None


# --- Утиліта для точного заміру пам'яті та часу ---
def measure_performance(func: Callable, *args) -> tuple[Any, float, float]:
    """Повертає: (результат, час_у_секундах, пікова_пам'ять_у_МБ)."""
    tracemalloc.start()
    start_time = time.perf_counter()

    result = func(*args)

    elapsed_time = time.perf_counter() - start_time
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_mb = peak_memory / (1024 * 1024)
    return result, elapsed_time, peak_mb


def run_benchmarks():
    dataset_sizes = [10_000, 100_000]
    temp_dir = Path("data/benchmarks")
    temp_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("ПОРІВНЯЛЬНИЙ АНАЛІЗ EAGER ТА LAZY EVALUATION (ВАРІАНТ 8)")
    print("=" * 80)
    print(
        f"{'Кількість':<10} | {'Метод':<7} | {'Час (с)':<10} | {'Пікова памʼять (MB)':<20} | {'Перший запис'}"
    )
    print("-" * 80)

    for size in dataset_sizes:
        csv_file = temp_dir / f"test_{size}.csv"
        generate_dataset(csv_file, count=size)

        # 1. Eager замір
        _, eager_time, eager_mem = measure_performance(
            eager_processing, csv_file
        )

        # 2. Lazy замір
        _, lazy_time, lazy_mem = measure_performance(lazy_processing, csv_file)

        print(
            f"{size:<10} | {'Eager':<7} | {eager_time:<10.4f} | {eager_mem:<20.4f} | завантажено все"
        )
        print(
            f"{size:<10} | {'Lazy':<7} | {lazy_time:<10.4f} | {lazy_mem:<20.4f} | потоково"
        )
        print("-" * 80)

    # 3. Порівняння Early Termination
    print("\nДОСЛІДЖЕННЯ EARLY TERMINATION (на датасеті 100 000 записів):")
    sample_csv = temp_dir / "test_100000.csv"
    if sample_csv.exists():
        _, e_time, e_mem = measure_performance(eager_find_first, sample_csv)
        _, l_time, l_mem = measure_performance(lazy_find_first, sample_csv)
        print(
            f"  - Eager find_first: час = {e_time:.5f} с | пам'ять = {e_mem:.4f} MB"
        )
        print(
            f"  - Lazy  find_first: час = {l_time:.5f} с | пам'ять = {l_mem:.4f} MB"
        )
        print(
            f"  -> Прискорення Lazy у ~{e_time / (l_time or 1e-6):.1f} разів завдяки миттєвому перериванню!"
        )

    print("=" * 80)


if __name__ == "__main__":
    run_benchmarks()