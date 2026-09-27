
import random


class Network:
    """
    Stores routers and links.

    A link has:
        cost   -> Dijkstra metric
        active -> True normally, False after failure simulation
    """

    def __init__(self):
        self.routers = set()
        self.links = {}
        self.failed_links = set()

    def add_router(self, name):
        self.routers.add(name)

    def remove_router(self, name):
        self.routers.discard(name)

        for link in list(self.links):
            if name in link:
                del self.links[link]

        self.failed_links = {
            link for link in self.failed_links if name not in link
        }

    def add_link(self, a, b, cost):
        if a == b:
            raise ValueError("A router cannot connect to itself.")

        if a not in self.routers or b not in self.routers:
            raise ValueError("Both routers must exist.")

        if cost <= 0:
            raise ValueError("Cost must be positive.")

        link = tuple(sorted((a, b)))
        self.links[link] = int(cost)
        self.failed_links.discard(link)

    def remove_link(self, a, b):
        link = tuple(sorted((a, b)))
        self.links.pop(link, None)
        self.failed_links.discard(link)

    def fail_link(self, a, b):
        link = tuple(sorted((a, b)))

        if link in self.links:
            self.failed_links.add(link)

    def restore_link(self, a, b):
        link = tuple(sorted((a, b)))
        self.failed_links.discard(link)

    def active_edges(self):
        return [
            (a, b, cost)
            for (a, b), cost in self.links.items()
            if (a, b) not in self.failed_links
        ]

    def all_edges(self):
        return [
            (a, b, cost, (a, b) in self.failed_links)
            for (a, b), cost in self.links.items()
        ]

    def adjacency(self):
        """Return only active links in Dijkstra-friendly format."""
        graph = {router: {} for router in self.routers}

        for a, b, cost in self.active_edges():
            graph[a][b] = cost
            graph[b][a] = cost

        return graph

    def clear(self):
        self.routers.clear()
        self.links.clear()
        self.failed_links.clear()

    def demo(self):
        self.clear()

        for router in ["A", "B", "C", "D", "E"]:
            self.add_router(router)

        links = [
            ("A", "B", 4),
            ("A", "C", 2),
            ("B", "C", 1),
            ("B", "D", 5),
            ("C", "D", 8),
            ("C", "E", 10),
            ("D", "E", 2),
        ]

        for a, b, cost in links:
            self.add_link(a, b, cost)

    def random_network(self, count, min_cost, max_cost):
        """Create a connected random network."""
        self.clear()

        names = [chr(ord("A") + i) for i in range(count)]

        for name in names:
            self.add_router(name)

        # First create a tree so every router is reachable.
        shuffled = names[:]
        random.shuffle(shuffled)

        for i in range(1, len(shuffled)):
            a = shuffled[i]
            b = random.choice(shuffled[:i])
            self.add_link(a, b, random.randint(min_cost, max_cost))

        # Add some extra links.
        possible = []

        for i, a in enumerate(names):
            for b in names[i + 1:]:
                link = tuple(sorted((a, b)))
                if link not in self.links:
                    possible.append((a, b))

        random.shuffle(possible)

        extra = min(len(possible), max(1, count // 2))

        for a, b in possible[:extra]:
            self.add_link(a, b, random.randint(min_cost, max_cost))
