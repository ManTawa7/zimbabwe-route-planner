import heapq
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from src.graph import RoadGraph


@dataclass
class SearchOutcome:
    algorithm: str
    mode: str
    path: List[str]
    total_distance_km: float
    total_stops: int
    nodes_expanded: int
    max_frontier_size: int
    explored_nodes: List[str]
    execution_time_ms: float


def search_route(
    graph: RoadGraph,
    start: str,
    goal: str,
    mode: str = "distance",       # "distance" or "stops"
    use_heuristic: bool = True,   # True -> A* (when mode="distance"), False -> UCS
) -> Optional[SearchOutcome]:
    if start not in graph.towns or goal not in graph.towns:
        raise ValueError(f"Start ('{start}') or goal ('{goal}') not found in graph.")

    if mode not in {"distance", "stops"}:
        raise ValueError(f"Unsupported mode '{mode}'. Use 'distance' or 'stops'.")

    t0 = time.perf_counter()

    def h(town: str) -> float:
        if mode == "stops" or not use_heuristic:
            return 0.0
        return graph.haversine_km(town, goal)

    # Priority queue tuple: (f_score, tie_breaker, g_score, current_town)
    tie_breaker = 0
    frontier: List[Tuple[float, int, float, str]] = [(h(start), tie_breaker, 0.0, start)]
    came_from: Dict[str, Optional[str]] = {start: None}
    g_score: Dict[str, float] = {start: 0.0}
    closed_set: Set[str] = set()
    explored_nodes: List[str] = []
    max_frontier = 1

    while frontier:
        if len(frontier) > max_frontier:
            max_frontier = len(frontier)

        _, _, g_curr, current = heapq.heappop(frontier)

        if current in closed_set:
            continue

        closed_set.add(current)
        explored_nodes.append(current)

        if current == goal:
            path: List[str] = []
            node: Optional[str] = goal
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()

            total_km = sum(
                graph.get_edge_distance(path[i], path[i + 1])
                for i in range(len(path) - 1)
            )
            elapsed_ms = (time.perf_counter() - t0) * 1000.0

            if mode == "distance":
                algo_label = "A* (Haversine)" if use_heuristic else "Uniform-Cost Search"
            else:
                algo_label = "UCS / BFS (Fewest Stops)"

            return SearchOutcome(
                algorithm=algo_label,
                mode=mode,
                path=path,
                total_distance_km=round(total_km, 2),
                total_stops=max(0, len(path) - 1),
                nodes_expanded=len(explored_nodes),
                max_frontier_size=max_frontier,
                explored_nodes=explored_nodes,
                execution_time_ms=round(elapsed_ms, 4),
            )

        for edge in graph.adj.get(current, []):
            neighbor = edge.to
            if neighbor in closed_set:
                continue

            step_cost = edge.distance_km if mode == "distance" else 1.0
            tentative_g = g_curr + step_cost

            if tentative_g < g_score.get(neighbor, float("inf")):
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current
                tie_breaker += 1
                f_val = tentative_g + h(neighbor)
                heapq.heappush(frontier, (f_val, tie_breaker, tentative_g, neighbor))

    return None
