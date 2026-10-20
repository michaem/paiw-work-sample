"""Prepare the pending reading list from validated book records."""


def pending_titles(books):
    return [book["title"] for book in books if book["finished"]]


if __name__ == "__main__":
    books = [
        {"title": "The Harbor", "finished": True},
        {"title": "The Orchard", "finished": False},
    ]
    print(pending_titles(books))
