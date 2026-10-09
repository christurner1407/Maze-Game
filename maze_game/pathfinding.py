"""Breadth-first search helpers."""
from collections import deque


def distances(start, get_neighbors):
    """Return a dict of how many steps it takes to reach each tile."""
    dist = {start: 0}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for nxt in get_neighbors(current):
            if nxt not in dist:
                dist[nxt] = dist[current] + 1
                queue.append(nxt)
    return dist


def shortest_path(start, is_target, get_neighbors):
    """Return the shortest path as a list of tiles, or None if there
    is no path."""
    came_from = {start: None}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        if is_target(current):
            path = []
            while current is not None:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        for nxt in get_neighbors(current):
            if nxt not in came_from:
                came_from[nxt] = current
                queue.append(nxt)
    return None
