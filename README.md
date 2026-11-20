# Zimbabwe Route Planner

A beginner-friendly guide and codebase for **Project #7: Zimbabwe Route Planner with GUI** in *Introduction to AI & Expert Systems*. It finds routes across **35 towns and cities in Zimbabwe** using a map interface, shortest-distance search, and fewest-stops search.



Imagine you want to travel from **Harare** to **Victoria Falls** or **Mutare** across Zimbabwe:

1. **Shortest Distance (`A*` Search):** Tries to pick the route with the **lowest total kilometers** along the roads. It uses straight-line distance ("as the crow flies", calculated with the Haversine formula) as a smart guide so it doesn't waste time exploring towns in the wrong direction.

2. **Fewest Stops (`Uniform-Cost Search / BFS`):** Tries to pick the route with the **smallest number of towns/junctions passed through**. Every road segment counts as `1` stop.

3. **Interactive Map (`Tkinter` + `tkintermapview`):** Shows Zimbabwe on a map, puts pins on the towns, highlights explored towns, draws the final route line, and displays distance, stops, nodes checked, and runtime.

4. **Benchmark Tool (`src/benchmark.py`):** Runs multiple routes automatically, compares the search methods, saves a table (`benchmark_results.csv`), and creates charts (`PNG` images) for your report and presentation.

## How the Pieces Fit Together (System Diagram)

```
+-----------------------------------------------------------------------+
|                       USER / CLASSROOM DEMO                           |
|  Picks Start Town, Goal Town, and Mode ("Shortest km" or "Fewest stops")|
+-----------------------------------------------------------------------+
                  |                                         |
                  v (Interactive UI)                        v (Automated Tests)
+-----------------------------------+     +-----------------------------+
|            src/gui.py             |     |      src/benchmark.py       |
|  - Dropdowns & radio buttons      |     |  - Runs sample routes       |
|  - Map pins & route line          |     |  - Compares A* vs UCS       |
|  - Live stats readout             |     |  - Saves CSV & PNG charts   |
+-----------------------------------+     +-----------------------------+
                  |                                         |
                  +--------------------+--------------------+
                                       |
                                       v
+-----------------------------------------------------------------------+
|                           src/search.py                               |
|  - Shortest Distance: A* using road km + Haversine straight-line km   |
|  - Baseline Distance: Uniform-Cost Search (road km only, no guide)    |
|  - Fewest Stops: UCS / BFS (1 stop per road hop)                     |
+-----------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------+
|                            src/graph.py                               |
|  - Loads towns, GPS coordinates, and road distances                   |
|  - Calculates straight-line Haversine distance between two towns      |
+-----------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------+
|                     data/zimbabwe_graph.json                          |
|  - 35 Zimbabwean towns/cities + road connections in kilometers       |
+-----------------------------------------------------------------------+

```

## Folder & File Structure Diagram

```
zimbabwe-route-planner/
│
├── .github/workflows/          # Automatic checks when code is pushed to GitHub
│   ├── python-app.yml          # Checks code style (flake8) and runs pytest
│   └── tests.yml               # Runs graph validation and unit tests
│
├── data/
│   └── zimbabwe_graph.json     # The map data: 35 towns (lat/lon) + road distances (km)
│
├── docs/                       # Generated reports, CSV data, and comparison charts
│   ├── benchmark_results.csv
│   ├── distance_vs_stops_tradeoff.png
│   └── nodes_expanded_comparison.png
│
├── src/                        # Main Python source code
│   ├── __init__.py             # Marks 'src' as a Python package
│   ├── graph.py                # Reads JSON data and computes Haversine distances
│   ├── search.py               # Runs A* (shortest distance) and UCS/BFS (fewest stops)
│   ├── gui.py                  # Opens the map window and shows routes/metrics
│   └── benchmark.py            # Runs comparisons and exports CSV + charts to docs/
│
├── tests/                      # Automated tests to make sure nothing is broken
│   ├── __init__.py             # Marks 'tests' as a Python package
│   ├── conftest.py             # Helps pytest find the 'src' folder cleanly
│   ├── test_search.py          # Checks that search returns valid, optimal results
│   └── validate_graph.py       # Checks that all 35 towns are connected and valid
│
└── README.md                   # This guide

```

## Step-by-Step Setup (For Beginners)

### Step 1: Get the Project on Your Computer

Open **PowerShell** (Windows) or **Terminal** (Mac/Linux), go to where you keep projects, and clone the repository:

```
git clone https://github.com/ManTawa7/zimbabwe-route-planner.git
cd zimbabwe-route-planner

```

### Step 2: Create a Virtual Environment (`venv`)

A virtual environment keeps this project's Python packages separate from the rest of your computer.

```
python -m venv venv

```

Turn it on (**activate** it):

* **Windows (PowerShell):**

  ```
  .\venv\Scripts\Activate.ps1
  
  ```

  *(If PowerShell blocks it, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once, then activate again.)*

* **Linux / macOS:**

  ```
  source venv/bin/activate
  
  ```

You should see `(venv)` appear at the start of your terminal line.

### Step 3: Install Required Libraries

```
pip install tkintermapview matplotlib pytest

```

* `tkintermapview` — displays the interactive map inside the window.

* `matplotlib` — draws the comparison bar charts.

* `pytest` — runs automated unit tests.

## How to Run Everything

### 1. Check That Data and Tests Pass

```
python -m tests.validate_graph
pytest -v

```

* `validate_graph` checks that all 35 towns are linked up with valid distances.

* `pytest -v` runs the search tests and prints `passed` if everything works.

### 2. Open the Map App (GUI)

```
python -m src.gui

```

* Requires an internet connection so map tiles can load.

* Pick a **Start Town** and **Destination Town**, choose **Shortest Distance (A* + Haversine)*\* or **Fewest Stops (UCS / BFS)**, and click **Find Route**.

### 3. Generate Benchmark Data & Charts

```
python -m src.benchmark

```

* Prints a comparison table in the terminal and saves `benchmark_results.csv` and two `.png` charts inside `docs/`.

## Saving Your Work Back to GitHub

Whenever you make changes locally and want to upload them to `main` on GitHub:

```
git pull --rebase origin main
git add .
git commit -m "Update project files"
git push origin main

```

## Data & Project Note

* Uses public/synthetic road distance estimates across 35 Zimbabwean towns and cities, with **no personal data** about real people.

* Built as a 6-person group project for *Introduction to AI & Expert Systems*.
