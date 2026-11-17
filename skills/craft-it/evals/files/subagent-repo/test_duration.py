from duration import parse

assert parse("90s") == 90
assert parse("5m") == 300
for bad in ["", "5", "m", "-5m", "5x"]:
    try:
        parse(bad)
    except ValueError:
        continue
    raise AssertionError(f"accepted {bad!r}")
print("PASS duration")
