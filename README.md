# Food Pantry Project

A web application to manage food pantry inventory, donations, and distributions.

## Installation

Clone the repository and install dependencies:
<!-- 
Printing the entire dictionary before iterating allows us to see the full contents at once, 
while iterating provides a detailed view of each key-value pair. 
Both outputs are useful for debugging and understanding the data structure.
-->
ohio_pantries = {
    "Akron-Canton Regional Foodbank": "350 Opportunity Parkway Akron, OH 44307",
    "Freestore Foodbank": "3401 Rosenthal Way Cincinnati, OH 45204",
    "Greater Cleveland Food Bank": "13815 Coit Rd Cleveland, OH 44110",
    "Mid-Ohio Food Collective": "3960 Brookham Drive Grove City, OH 43123",
    "Second Harvest Food Bank of Clark, Champaign, and Logan": "20 N Murray Street Springfield, OH 45503",
    "Second Harvest Food Bank of North Central Ohio": "5510 Baumhart Road Lorain, OH 44053",
    "Second Harvest Food Bank of the Mahoning Valley": "2805 Salt Springs Road Youngstown, OH 44509",
    "Shared Harvest Foodbank": "5901 Dixie Highway Fairfield, OH 45014",
    "Southeast Ohio Foodbank & Kitchen (a division of Hocking Athens Perry Community Action)": "1005 CIC Drive Logan, OH 43138",
    "The Foodbank, Inc.": "56 Armor Place Dayton, OH 45417",
    "Toledo Northwestern Ohio Food Bank": "24 East Woodruff Avenue Toledo, OH 43604"
}
print(ohio_pantries)
for pantry, address in ohio_pantries.items():
    print(f"{pantry} is located at {address}.")
# This dictionary contains food pantries in Ohio and their addresses.  
# The code prints the entire dictionary and then iterates through it to print each pantry's name and address in a formatted string.
# Each pantry's name is printed alongside its address for clarity.

## Command-line helper: find nearest pantry

A simple Python script is included to locate the nearest pantry from a small local dataset.

Files added:
- `scripts/find_pantry.py` — CLI that prompts for an address (or accepts `--address`) and finds the nearest pantry from `data/pantries.csv`.
- `data/pantries.csv` — sample pantry locations (name, address, lat, lon).
- `requirements.txt` — lists `requests` for geocoding.

Quickstart (Windows PowerShell):

```powershell
python -m pip install -r requirements.txt
python scripts/find_pantry.py --address "40.7128,-74.0060"
```

Notes:
- The script uses OpenStreetMap's Nominatim to geocode free-text addresses; it's rate-limited and requires a User-Agent. For production, consider a geocoding API with an API key.
- If you don't have network access, run the script and enter coordinates manually as `lat,lon` (for example `40.7128,-74.0060`).

Additional options

- Return top N results: `--top N` or `-n N` (default 1). Example:

```powershell
python scripts/find_pantry.py --address "40.7580,-73.9855" --top 3
```

- Limit search by radius (in km): `--radius R` or `-r R`. Example:

```powershell
python scripts/find_pantry.py --address "40.7580,-73.9855" --radius 2
```

- Autolocate by IP (best-effort): `--autolocate`. This attempts to approximate your location via an IP geolocation service, then searches nearby pantries.

```powershell
python scripts/find_pantry.py --autolocate
```

- Interactive selection: when multiple results are returned, the script will show a simple numbered menu to pick one.

Notes on data and testing
- Unit tests were added for core utilities (`tests/test_find_pantry.py`). Install `pytest` from `requirements.txt` and run `python -m pytest` to execute them.

