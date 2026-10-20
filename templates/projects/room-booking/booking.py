"""Check a booking against the room's closing time."""


def can_book(start, duration, closes_at):
    return start + duration < closes_at


if __name__ == "__main__":
    print(can_book(start=16, duration=2, closes_at=18))
