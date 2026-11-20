import heapq
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from src.graph import RoadGraph


@dataclass
class SearchResult:
    algorithm: str
    mode: str
    path: List[str]
    distance_km: float
    stops: int
    nodes_expanded: int
    max_frontier: int
    explored: List[str]
    runtime_ms: float


def find_route(
    graph: RoadGraph,
    start: str,
    goal: str,
    mode: str = "distance",
    use_heuristic: bool = True,
) -> Optional[SearchResult]:
    if start not in graph.towns or goal not in graph.towns:
        raise ValueError(f"Invalid start ('{start}') or goal ('{goal}') town.")
    if mode not in {"distance", "stops"}:
        raise ValueError(f"Mode must be 'distance' or 'stops', got '{mode}'.")

    t_start = time.perf_counter()

    def heuristic(town: str) -> float:
        if mode == "stops" or not use_heuristic:
            return 0.0
        return graph.haversine_km(town, goal)

    counter = 0
    frontier: List[Tuple[float, int, float, str]] = [(heuristic(start), counter, 0.0, start)]
    came_from: Dict[str, Optional[str]] = {start: None}
    g_cost: Dict[str, float] = {start: 0.0}
    closed: Set[str] = set()
    explored: List[str] = []
    max_frontier = 1

    while frontier:
        if len(frontier) > max_frontier:
            max_frontier = len(frontier)

        _, _, g_curr, current = heapq.heappop(frontier)

        if current in closed:
            continue

        closed.add(current)
        explored.append(current)

        if current == goal:
            path: List[str] = []
            node: Optional[str] = goal
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()

            total_km = sum(
                graph.edge_distance(path[i], path[i + 1])
                for i in range(len(path) - 1)
            )
            elapsed_ms = (time.perf_counter() - t_start) * 1000.0

            if mode == "distance":
                algo_name = "A* (Haversine)" if use_heuristic else "Uniform-Cost Search"
            else:
                algo_name = "Fewest Stops (UCS / BFS)"

            return SearchResult(
                algorithm=algo_name,
                mode=mode,
                path=path,
                distance_km=round(total_km, 2),
                stops=max(0, len(path) - 1),
                nodes_expanded=len(explored),
                max_frontier=max_frontier,
                explored=explored,
                runtime_ms=round(elapsed_ms, 4),
            )

        for edge in graph.adj.get(current, []):
            neighbor = edge.to
            if neighbor in closed:
                continue

            step_cost = edge.distance_km if mode == "distance" else 1.0
            tentative_g = g_curr + step_cost

            if tentative_g < g_cost.get(neighbor, float("inf")):
                g_cost[neighbor] = tentative_g
                came_from[neighbor] = current
                counter += 1
                f_score = tentative_g + heuristic(neighbor)
                heapq.heappush(frontier, (f_score, counter, tentative_g, neighbor))

    return None