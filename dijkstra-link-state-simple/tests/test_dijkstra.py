
from dijkstra import dijkstra, get_path, make_routing_table
from network import Network


def test_dijkstra():
    graph = {
        "A": {"B": 4, "C": 2},
        "B": {"A": 4, "C": 1, "D": 5},
        "C": {"A": 2, "B": 1, "D": 8},
        "D": {"B": 5, "C": 8}
    }

    distance, previous, steps = dijkstra(graph, "A")

    assert distance["A"] == 0
    assert distance["C"] == 2
    assert distance["B"] == 3
    assert distance["D"] == 8

    assert get_path(previous, "A", "D") == ["A", "C", "B", "D"]
    assert len(steps) > 1


def test_failure_changes_routes():
    network = Network()
    network.demo()

    before = network.adjacency()
    distance_before, _, _ = dijkstra(before, "A")

    network.fail_link("B", "C")

    after = network.adjacency()
    distance_after, _, _ = dijkstra(after, "A")

    assert distance_before["B"] == 3
    assert distance_after["B"] == 4


def test_routing_table():
    graph = {
        "A": {"B": 2},
        "B": {"A": 2}
    }

    distance, previous, _ = dijkstra(graph, "A")
    table = make_routing_table(
        graph,
        "A",
        distance,
        previous
    )

    row = next(
        row for row in table
        if row["Destination"] == "B"
    )

    assert row["Cost"] == 2
    assert row["Next Hop"] == "B"
