import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class Town:
    name: str
    lat: float
    lon: float
    province: str


@dataclass
class RoadEdge:
    to: str
    distance_km: float
    road: str


class RoadGraph:
    def __init__(self, towns: Dict[str, Town], adj: Dict[str, List[RoadEdge]]) -> None:
        self.towns = towns
        self.adj = adj

    @classmethod
    def from_json(cls, path: str = "data/zimbabwe_graph.json") -> "RoadGraph":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        towns: Dict[str, Town] = {}
        for name, info in raw["nodes"].items():
            towns[name] = Town(
                name=name,
                lat=float(info["lat"]),
                lon=float(info["lon"]),
                province=info.get("province", ""),
            )

        adj: Dict[str, List[RoadEdge]] = {name: [] for name in towns}
        for edge in raw["edges"]:
            u = edge["from"]
            v = edge["to"]
            dist = float(edge["distance_km"])
            road_name = edge.get("road", "")

            if u not in towns or v not in towns:
                raise ValueError(f"Invalid edge endpoint in {u} -> {v}")

            adj[u].append(RoadEdge(to=v, distance_km=dist, road=road_name))
            adj[v].append(RoadEdge(to=u, distance_km=dist, road=road_name))

        return cls(towns=towns, adj=adj)

    def haversine_km(self, origin: str, destination: str) -> float:
        """Straight-line great-circle distance in km (admissible for road networks)."""
        t1 = self.towns[origin]
        t2 = self.towns[destination]

        radius_km = 6371.0
        phi1, phi2 = math.radians(t1.lat), math.radians(t2.lat)
        dphi = math.radians(t2.lat - t1.lat)
        dlambda = math.radians(t2.lon - t1.lon)

        a = (
            math.sin(dphi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        )
        return 2 * radius_km * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def get_edge_distance(self, u: str, v: str) -> float:
        for edge in self.adj.get(u, []):
            if edge.to == v:
                return edge.distance_km
        raise KeyError(f"No direct edge between {u} and {v}")
