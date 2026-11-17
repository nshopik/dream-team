# Duration format

A duration is a whole number followed by one unit letter, with no space.

| Unit | Meaning | Largest value |
|---|---|---|
| `s` | seconds | no limit |
| `m` | minutes | no limit |
| `h` | hours | 24 |

An hours value above 24 is invalid: `parse("25h")` raises `ValueError`.
