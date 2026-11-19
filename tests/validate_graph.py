import json
import math
from collections import deque
from pathlib import Path


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def validate_graph(path: str = "data/zimbabwe_graph.json") -> None:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    nodes = data["nodes"]
    edges = data["edges"]

    assert len(nodes) == 35, f"Expected 35 nodes, got {len(nodes)}"

    adj = {town: [] for town in nodes}
    for edge in edges:
        u, v, dist = edge["from"], edge["to"], edge["distance_km"]
        assert u in nodes and v in nodes, f"Unknown town in edge: {u} -> {v}"
        assert u != v, f"Self-loop found at {u}"
        assert dist > 0, f"Non-positive distance on {u} -> {v}"

        straight_line = haversine_km(
            nodes[u]["lat"], nodes[u]["lon"], nodes[v]["lat"], nodes[v]["lon"]
        )
        if dist < straight_line:
            print(
                f"Warning: {u} <-> {v} road ({dist} km) < straight-line ({straight_line:.1f} km)"
            )

        adj[u].append((v, dist))
        adj[v].append((u, dist))

    # BFS reachability check from Harare
    visited = {"Harare"}
    queue = deque(["Harare"])
    while queue:
        curr = queue.popleft()
        for nbr, _ in adj[curr]:
            if nbr not in visited:
                visited.add(nbr)
                queue.append(nbr)

    unreachable = set(nodes.keys()) - visited
    assert not unreachable, f"Unreachable towns from Harare: {unreachable}"
    print(f"Success: {len(nodes)} nodes and {len(edges)} edges validated; graph is connected.")


if __name__ == "__main__":
    validate_graph()
