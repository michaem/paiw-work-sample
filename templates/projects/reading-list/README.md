# Reading list

A community library keeps a reading list. `pending_titles(books)` returns the
titles that still need to be read, in their original order.

Inputs are already validated by the caller. Each book has a string `title` and
a boolean `finished`. A finished book must not appear in the pending list.
An empty list produces an empty list.

The command-line example is available with `python3 reading_list.py`.
This is a deliberately small review exercise. Review against the contract above.
