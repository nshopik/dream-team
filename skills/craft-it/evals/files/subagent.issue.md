`duration.parse` has no hours unit: `parse("2h")` raises `ValueError`, so a caller with an
hour-long timeout has to write `120m`.

## Proposal

- Add `"h": 3600` to `UNITS` in `duration.py`.
- Add a test for the new unit to `test_duration.py`.

## Done when

- `parse("2h")` returns `7200`.
- `python3 test_duration.py` passes.
