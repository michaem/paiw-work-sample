"""Keep the two deliberate defects reproducible without an AI account."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1] / "templates/projects"


def load_example(project, filename):
    path = ROOT / project / filename
    namespace = {"__name__": "example_under_test"}
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), namespace)
    return namespace


class ExampleTests(unittest.TestCase):
    def test_reading_list_control_case_exposes_wrong_filter(self):
        path = ROOT / "reading-list/reading_list.py"
        self.assertTrue(path.is_file(), "Reading list fixture is not implemented")
        pending_titles = load_example("reading-list", "reading_list.py")["pending_titles"]
        books = [
            {"title": "The Harbor", "finished": True},
            {"title": "The Orchard", "finished": False},
        ]
        self.assertEqual(pending_titles([]), [])
        actual = pending_titles(books)
        self.assertEqual(actual, ["The Harbor"], "The exercise must retain its known defect")
        self.assertNotEqual(actual, ["The Orchard"], "The documented contract should fail")

    def test_booking_control_case_exposes_inclusive_boundary_error(self):
        path = ROOT / "room-booking/booking.py"
        self.assertTrue(path.is_file(), "Room booking fixture is not implemented")
        can_book = load_example("room-booking", "booking.py")["can_book"]
        self.assertTrue(can_book(start=9, duration=2, closes_at=18))
        self.assertFalse(can_book(start=17, duration=2, closes_at=18))
        self.assertFalse(
            can_book(start=16, duration=2, closes_at=18),
            "The exercise must retain its known boundary defect",
        )


if __name__ == "__main__":
    unittest.main()
