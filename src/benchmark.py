import csv
from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt

from src.graph import RoadGraph
from src.search import search_route


TEST_ROUTES: List[Tuple[str, str]] = [
    ("Harare", "Bulawayo"),
    ("Harare", "Mutare"),
    ("Harare", "Masvingo"),
    ("Harare", "Victoria Falls"),
    ("Harare", "Kariba"),
    ("Bulawayo", "Mutare"),
    ("Bulawayo", "Beitbridge"),
    ("Gweru", "Chiredzi"),
    ("Plumtree", "Nyanga"),
    ("Chipinge", "Kariba"),
    ("Bindura", "Gwanda"),
    ("Kwekwe", "Chimanimani"),
]


def run_benchmarks(
    graph: RoadGraph,
    routes: List[Tuple[str, str]] = TEST_ROUTES,
    output_dir: str = "docs",
) -> None:
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    rows = []
    labels = []
    astar_nodes = []
    ucs_nodes = []
    stops_counts = []
    astar_distances = []
    stops_distances = []

    print(
        f"{'Route':<26} | {'A* Nodes':>8} | {'UCS Nodes':>9} | "
        f"{'A* km':>8} | {'Stops Mode (km / stops)'}"
    )
    print("-" * 86)

    for start, goal in routes:
        astar = search_route(graph, start, goal, mode="distance", use_heuristic=True)
        ucs = search_route(graph, start, goal, mode="distance", use_heuristic=False)
        fewest = search_route(graph, start, goal, mode="stops", use_heuristic=False)

        if not (astar and ucs and fewest):
            continue

        route_label = f"{start} -> {goal}"
        labels.append(f"{start[:4]}->{goal[:4]}")
        astar_nodes.append(astar.nodes_expanded)
        ucs_nodes.append(ucs.nodes_expanded)
        stops_counts.append(fewest.total_stops)
        astar_distances.append(astar.total_distance_km)
        stops_distances.append(fewest.total_distance_km)

        print(
            f"{route_label:<26} | {astar.nodes_expanded:>8} | {ucs.nodes_expanded:>9} | "
            f"{astar.total_distance_km:>8.1f} | "
            f"{fewest.total_distance_km:.1f} km / {fewest.total_stops} stops"
        )

        rows.append(
            {
                "origin": start,
                "destination": goal,
                "astar_nodes_expanded": astar.nodes_expanded,
                "ucs_nodes_expanded": ucs.nodes_expanded,
                "nodes_saved_by_astar": ucs.nodes_expanded - astar.nodes_expanded,
                "astar_runtime_ms": astar.execution_time_ms,
                "ucs_runtime_ms": ucs.execution_time_ms,
                "astar_distance_km": astar.total_distance_km,
                "astar_stops": astar.total_stops,
                "fewest_stops_count": fewest.total_stops,
                "fewest_stops_distance_km": fewest.total_distance_km,
                "astar_path": " -> ".join(astar.path),
                "fewest_stops_path": " -> ".join(fewest.path),
            }
        )

    csv_file = out_path / "benchmark_results.csv"
    with csv_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # Chart 1: Nodes Expanded (A* vs. Uniform-Cost Search)
    x = range(len(labels))
    width = 0.38

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar([i - width / 2 for i in x], astar_nodes, width=width, label="A* (Haversine)")
    ax.bar([i + width / 2 for i in x], ucs_nodes, width=width, label="UCS (No Heuristic)")
    ax.set_title("Nodes Expanded: A* vs. Uniform-Cost Search Across Zimbabwe Routes")
    ax.set_xlabel("Route (Origin -> Destination)")
    ax.set_ylabel("Nodes Expanded")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(out_path / "nodes_expanded_comparison.png", dpi=200)
    plt.close(fig)

    # Chart 2: Total Distance (km) — Shortest Distance (A*) vs. Fewest Stops
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(
        [i - width / 2 for i in x],
        astar_distances,
        width=width,
        label="Shortest Distance Mode (A*)",
    )
    ax.bar(
        [i + width / 2 for i in x],
        stops_distances,
        width=width,
        label="Fewest Stops Mode",
    )
    ax.set_title("Route Distance (km): Shortest Distance vs. Fewest Stops")
    ax.set_xlabel("Route (Origin -> Destination)")
    ax.set_ylabel("Total Road Distance (km)")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(out_path / "distance_vs_stops_tradeoff.png", dpi=200)
    plt.close(fig)

    print(f"\nSaved CSV and charts to '{output_dir}/'.")


def main() -> None:
    graph = RoadGraph.from_json("data/zimbabwe_graph.json")
    run_benchmarks(graph)


if __name__ == "__main__":
    main()
