import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pykit.strings import truncate
from pykit.numbers import clamp


def test_truncate():
    assert truncate("hello world", 8) == "hello..."
    assert truncate("hi", 10) == "hi"


def test_clamp():
    assert clamp(5, 0, 3) == 3
    assert clamp(-1, 0, 3) == 0


def test_ordinal():
    from pykit.numbers import ordinal
    assert ordinal(1) == "1st"
    assert ordinal(11) == "11th"
    assert ordinal(23) == "23rd"


def test_group_by():
    from pykit.collections import group_by
    got = group_by(["ant", "bee", "asp"], key=lambda w: w[0])
    assert got == {"a": ["ant", "asp"], "b": ["bee"]}


def test_human_size():
    from pykit.numbers import human_size
    assert human_size(2048) == "2.0 KB"


def test_chunk():
    from pykit.collections import chunk
    assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]


def test_flatten():
    from pykit.collections import flatten
    assert flatten([[1, 2], [3]]) == [1, 2, 3]


def test_humanize_delta():
    from pykit.dates import humanize_delta
    assert humanize_delta(30) == "30s"
    assert humanize_delta(7200) == "2h"


def test_start_of_day():
    from datetime import datetime
    from pykit.dates import start_of_day
    d = start_of_day(datetime(2024, 3, 5, 14, 30))
    assert (d.hour, d.minute) == (0, 0)


def test_slugify():
    from pykit.strings import slugify
    assert slugify("Hello, World!") == "hello-world"


def test_days_between():
    from datetime import date
    from pykit.dates import days_between
    assert days_between(date(2024, 1, 1), date(2024, 1, 11)) == 10


def test_initials():
    from pykit.strings import initials
    assert initials("john doe") == "JD"
