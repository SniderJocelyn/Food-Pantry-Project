#!/usr/bin/env python3
"""
Simple CLI to find the nearest food pantry by address.

Usage:
  python scripts/find_pantry.py --address "1600 Amphitheatre Parkway, Mountain View, CA"

This script loads pantry locations from data/pantries.csv (name, address, lat, lon),
geocodes the user's address using Nominatim (OpenStreetMap), computes distances,
and prints the nearest pantry.

Notes:
- Nominatim has rate limits; for production use consider an API key service.
- If offline, enter latitude and longitude directly when prompted ("lat,lon").
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path
from typing import List, Tuple, Optional

try:
    import requests
except ImportError:
    requests = None  # we'll fail with a helpful message


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "pantries.csv"


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in kilometers between two points."""
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def load_pantries(csv_path: Path) -> List[Tuple[str, str, float, float]]:
    pantries: List[Tuple[str, str, float, float]] = []
    if not csv_path.exists():
        raise FileNotFoundError(f"Pantry data file not found: {csv_path}")
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                name = row.get("name") or "Unnamed"
                addr = row.get("address") or ""
                lat = float(row["lat"])
                lon = float(row["lon"])
                pantries.append((name, addr, lat, lon))
            except Exception as e:
                print(f"Skipping invalid row: {row} -> {e}")
    return pantries


def geocode_address(address: str) -> Optional[Tuple[float, float]]:
    """Use Nominatim to geocode address. Returns (lat, lon) or None on failure."""
    if requests is None:
        print("The 'requests' package is required for geocoding. Install with: pip install requests")
        return None
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 5}
    headers = {"User-Agent": "FoodPantryProject/1.0 (contact: example@example.com)"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            print("Address not found by geocoder.")
            return None
        # return the top result (latitude, longitude)
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return lat, lon
    except Exception as e:
        print(f"Geocoding failed: {e}")
        return None


def ip_autolocate() -> Optional[Tuple[float, float]]:
    """Best-effort IP geolocation using a free service. Returns (lat, lon) or None."""
    if requests is None:
        return None
    try:
        resp = requests.get("https://ipinfo.io/json", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        loc = data.get("loc")
        if not loc:
            return None
        lat_str, lon_str = loc.split(",")
        return float(lat_str), float(lon_str)
    except Exception:
        return None


def find_nearest(pantries, lat, lon, top=1, radius_km: Optional[float] = None):
    results = []
    for name, addr, plat, plon in pantries:
        d = haversine(lat, lon, plat, plon)
        if radius_km is not None and d > radius_km:
            continue
        results.append((d, name, addr, plat, plon))
    results.sort(key=lambda x: x[0])
    return results[:top]


def parse_latlon(text: str) -> Optional[Tuple[float, float]]:
    try:
        parts = [p.strip() for p in text.split(",")]
        if len(parts) != 2:
            return None
        lat = float(parts[0])
        lon = float(parts[1])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return None
        return lat, lon
    except Exception:
        return None


def interactive_select(results):
    """If multiple results present, show a simple numbered menu and return the chosen index or None."""
    if not results:
        return None
    if len(results) == 1:
        return 0
    print("Multiple matches found:")
    for i, (d, name, addr, plat, plon) in enumerate(results, start=1):
        print(f"{i}. {name} — {addr} ({d:.2f} km)")
    while True:
        choice = input(f"Select 1-{len(results)} (or Enter to pick 1): ").strip()
        if choice == "":
            return 0
        if choice.isdigit():
            n = int(choice)
            if 1 <= n <= len(results):
                return n - 1
        print("Invalid choice; try again.")


def is_postal_code(text: str) -> bool:
    # naive postal code check: short numeric or alphanumeric tokens
    t = text.strip()
    return (len(t) <= 10) and any(c.isdigit() for c in t)


def main(argv=None):
    p = argparse.ArgumentParser(description="Find nearest food pantry by address.")
    p.add_argument("--address", "-a", help="Address to search for (or 'lat,lon' or postal code)")
    p.add_argument("--top", "-n", type=int, default=1, help="Return top N nearest results")
    p.add_argument("--radius", "-r", type=float, default=None, help="Maximum search radius in km")
    p.add_argument("--autolocate", action="store_true", help="Try to approximate user location via IP")
    args = p.parse_args(argv)

    try:
        pantries = load_pantries(DATA_FILE)
    except FileNotFoundError as e:
        print(e)
        print(f"Expected sample data at: {DATA_FILE}")
        return 1

    address = args.address
    if not address and args.autolocate:
        latlon = ip_autolocate()
        if latlon:
            print(f"Autolocated to: {latlon[0]:.6f},{latlon[1]:.6f}")
        else:
            print("Autolocate failed; please enter an address or coordinates.")
            address = input("Enter your address (or 'lat,lon'): ").strip()
    if not address:
        address = input("Enter your address (or 'lat,lon'): ").strip()

    latlon = None
    # try parsing lat,lon first
    if "," in address:
        latlon = parse_latlon(address)
        if latlon is None:
            print("Couldn't parse lat,lon. Will try geocoding the text as an address.")

    # if looks like a short postal code, try geocoding that too (Nominatim can often handle postal codes)
    if latlon is None and is_postal_code(address):
        print("Detected postal code-like input; attempting geocoding.")
        latlon = geocode_address(address)

    if latlon is None:
        latlon = geocode_address(address)

    if latlon is None:
        print("Please enter coordinates directly as 'lat,lon', or check your network.")
        return 1

    lat, lon = latlon
    results = find_nearest(pantries, lat, lon, top=args.top, radius_km=args.radius)
    if not results:
        print("No pantries found within the given radius or dataset.")
        return 0

    # if multiple results and interactive terminal, allow selection
    chosen_idx = interactive_select(results)
    if chosen_idx is None:
        print("No selection made.")
        return 0
    d, name, addr, plat, plon = results[chosen_idx]
    # show top-N summary
    if args.top > 1:
        print("Top results:")
        for i, (d0, name0, addr0, plat0, plon0) in enumerate(results, start=1):
            print(f"{i}. {name0} — {addr0} ({d0:.2f} km) @ {plat0},{plon0}")
        print()

    print(f"Selected pantry: {name}\nAddress: {addr}\nDistance: {d:.2f} km\nLocation: {plat},{plon}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
