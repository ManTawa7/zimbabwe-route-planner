import pytest

from src.graph import RoadGraph
from src.search import search_route


@pytest.fixture(scope="module")
def zimbabwe_graph() -> RoadGraph:
    return RoadGraph.from_json("data/zimbabwe_graph.json")


def test_same_start_and_goal(zimbabwe_graph: RoadGraph) -> None:
    res = search_route(zimbabwe_graph, "Harare", "Harare", mode="distance", use_heuristic=True)
    assert res is not None
    assert res.path == ["Harare"]
    assert res.total_distance_km == 0.0
    assert res.total_stops == 0
    assert res.nodes_expanded == 1


def test_astar_matches_ucs_optimal_distance(zimbabwe_graph: RoadGraph) -> None:
    astar = search_route(zimbabwe_graph, "Harare", "Victoria Falls", mode="distance", use_heuristic=True)
    ucs = search_route(zimbabwe_graph, "Harare", "Victoria Falls", mode="distance", use_heuristic=False)

    assert astar is not None and ucs is not None
    assert astar.path == ucs.path
    assert astar.total_distance_km == ucs.total_distance_km
    assert astar.nodes_expanded <= ucs.nodes_expanded


def test_stops_mode_returns_valid_path(zimbabwe_graph: RoadGraph) -> None:
    stops_res = search_route(zimbabwe_graph, "Harare", "Mutare", mode="stops", use_heuristic=False)
    assert stops_res is not None
    assert stops_res.path[0] == "Harare"
    assert stops_res.path[-1] == "Mutare"
    assert stops_res.total_stops == len(stops_res.path) - 1


def test_invalid_town_raises(zimbabwe_graph: RoadGraph) -> None:
    with pytest.raises(ValueError):
        search_route(zimbabwe_graph, "Atlantis", "Harare")
