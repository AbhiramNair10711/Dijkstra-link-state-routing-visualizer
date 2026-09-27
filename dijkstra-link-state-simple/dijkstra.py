
from math import inf


def dijkstra(graph, source):
    """
    Simple Dijkstra implementation.

    graph format:
    {
        "A": {"B": 4, "C": 2},
        "B": {"A": 4, "C": 1},
        ...
    }

    Returns every step so the UI can animate the algorithm.
    """
    distance = {node: inf for node in graph}
    previous = {node: None for node in graph}
    visited = set()

    distance[source] = 0

    steps = [{
        "current": None,
        "distance": distance.copy(),
        "previous": previous.copy(),
        "visited": set(),
        "updates": [],
        "relaxed": [],
        "message": f"Start at source {source}. Set distance({source}) = 0."
    }]

    while len(visited) < len(graph):

        # Find the unvisited node with the smallest distance.
        current = None
        best_distance = inf

        for node in graph:
            if node not in visited and distance[node] < best_distance:
                best_distance = distance[node]
                current = node

        # No more reachable nodes.
        if current is None:
            break

        visited.add(current)
        updates = []
        relaxed = []

        # Relax all active links connected to current.
        for neighbor, cost in graph[current].items():
            new_distance = distance[current] + cost

            if neighbor not in visited and new_distance < distance[neighbor]:
                old_distance = distance[neighbor]

                distance[neighbor] = new_distance
                previous[neighbor] = current

                updates.append({
                    "node": neighbor,
                    "old": old_distance,
                    "new": new_distance,
                    "via": current
                })
                relaxed.append((current, neighbor))

        if updates:
            changes = ", ".join(
                f"{u['node']}: "
                f"{'∞' if u['old'] == inf else u['old']} → {u['new']}"
                for u in updates
            )
            message = f"Visit {current}. Update distances: {changes}."
        else:
            message = f"Visit {current}. No distance needs updating."

        steps.append({
            "current": current,
            "distance": distance.copy(),
            "previous": previous.copy(),
            "visited": visited.copy(),
            "updates": updates,
            "relaxed": relaxed,
            "message": message
        })

    return distance, previous, steps


def get_path(previous, source, destination):
    """Build the path by following previous[] backwards."""
    path = []
    current = destination

    while current is not None:
        path.append(current)

        if current == source:
            return path[::-1]

        current = previous.get(current)

    return []


def get_next_hop(previous, source, destination):
    path = get_path(previous, source, destination)

    if len(path) < 2:
        return "-"

    return path[1]


def make_routing_table(graph, source, distance, previous):
    table = []

    for destination in sorted(graph):
        if distance[destination] == inf:
            path = "Unreachable"
            next_hop = "-"
            cost = "∞"
        else:
            path_list = get_path(previous, source, destination)
            path = " → ".join(path_list)
            next_hop = get_next_hop(previous, source, destination)
            cost = distance[destination]

        table.append({
            "Destination": destination,
            "Next Hop": next_hop,
            "Cost": cost,
            "Path": path
        })

    return table
