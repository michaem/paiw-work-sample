# Room booking

A community library rents a meeting room. `can_book(start, duration, closes_at)`
decides whether a proposed booking fits before closing time.

Times are integer hours on the same day. The caller already validates
`0 <= start <= 23`, `1 <= duration <= 24`, and `0 <= closes_at <= 24`.
A booking may finish exactly at closing time. It must not finish later.

The command-line example is available with `python3 booking.py`.
This is a deliberately small review exercise. Review against the contract above.
