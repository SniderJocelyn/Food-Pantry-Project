#!/usr/bin/env python3
"""
Create an interactive map of pantries (centered on Cincinnati, OH) using folium.
Saves output to scripts/map_pantries.html
"""
from pathlib import Path
import csv

import folium
from folium.plugins import MarkerCluster

# Cincinnati center
CINCINNATI_LAT, CINCINNATI_LON = 39.1031, -84.5120

# Locate data file relative to project root
DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "pantries.csv"
OUT_FILE = Path(__file__).resolve().parent / "map_pantries.html"


def load_from_csv(csv_path: Path):
    pantries = []
    if not csv_path.exists():
        raise FileNotFoundError(f"Pantry data file not found: {csv_path}")
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                name = row.get("name", "Unnamed")
                address = row.get("address", "")
                lat = float(row["lat"])
                lon = float(row["lon"])
                pantries.append({"name": name, "address": address, "lat": lat, "lon": lon})
            except Exception:
                # skip rows with missing/invalid coordinates
                continue
    return pantries


def build_map(pantries, center=(CINCINNATI_LAT, CINCINNATI_LON), zoom_start=11):
    m = folium.Map(location=center, zoom_start=zoom_start)
    marker_cluster = MarkerCluster().add_to(m)

    for p in pantries:
        popup = folium.Popup(f"<b>{p['name']}</b><br>{p['address']}", max_width=300)
        folium.Marker(
            location=(p["lat"], p["lon"]),
            popup=popup,
            tooltip=p["name"],
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(marker_cluster)

    # circle for Cincinnati center
    folium.Circle(location=center, radius=5000, color="green", fill=False).add_to(m)
    return m


def main():
    try:
        pantries = load_from_csv(DATA_FILE)
    except FileNotFoundError as e:
        print(e)
        print(f"Expected sample data at: {DATA_FILE}")
        return 1

    if not pantries:
        print("No pantries found in data file.")
        return 1

    m = build_map(pantries)
    m.save(str(OUT_FILE))
    print(f"Map saved to: {OUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
