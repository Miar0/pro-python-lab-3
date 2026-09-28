import csv
import random
from pathlib import Path

ROOM_TYPES = ("Standard", "Deluxe", "Suite", "Single", "Family")
STATUSES = ("available", "booked")
LAST_NAMES = (
    "Shevchenko",
    "Bondar",
    "Melnyk",
    "Koval",
    "Boyko",
    "Tkachenko",
    "Kravets",
)


def generate_dataset(path: Path, count: int = 100_000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["room_number", "type", "price", "status", "client"])

        for i in range(1, count + 1):
            if random.random() < 0.02:
                writer.writerow(
                    [
                        f"ERR_{i}",
                        "Unknown",
                        "-50.0",
                        "invalid_status",
                        "Corrupted Data",
                    ]
                )
                continue

            status = random.choice(STATUSES)
            client = random.choice(LAST_NAMES) if status == "booked" else ""
            price = round(random.uniform(500.0, 5000.0), 2)
            room_type = random.choice(ROOM_TYPES)

            writer.writerow([i, room_type, price, status, client])

    print(f"Згенеровано {count} записів у {path}")


if __name__ == "__main__":
    generate_dataset(Path("data/bookings.csv"), count=100_000)