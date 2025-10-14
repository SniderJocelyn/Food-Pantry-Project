import math
from pathlib import Path

from scripts.find_pantry import haversine, load_pantries, parse_latlon


def test_haversine_known_distance():
    # distance between two same points should be ~0
    d = haversine(40.7580, -73.9855, 40.7580, -73.9855)
    assert math.isclose(d, 0.0, abs_tol=1e-6)


def test_parse_latlon_valid():
    assert parse_latlon("40.7128,-74.0060") == (40.7128, -74.006)


def test_load_pantries_exists(tmp_path, monkeypatch):
    # create a temporary CSV
    csv = tmp_path / "pantries.csv"
    csv.write_text("name,address,lat,lon\nA,Addr,10.0,20.0\n")
    # monkeypatch the DATA_FILE path by setting Path to that file (import inside function uses DATA_FILE variable)
    # Instead, call load_pantries directly
    pantries = load_pantries(csv)
    assert len(pantries) == 1
    assert pantries[0][0] == "A"
    assert pantries[0][2] == 10.0
