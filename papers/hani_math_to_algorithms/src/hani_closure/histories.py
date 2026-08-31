"""Temporal interaction-history primitives for hard-sphere pilot data.

The event graph is a computable proxy derived from physical trajectories. It is
not identical to an abstract molecule after the proof's cutting operations.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass


@dataclass(frozen=True)
class CollisionEvent:
    event_id: int
    time: float
    particle_i: int
    particle_j: int
    layer: int

    @property
    def particles(self) -> tuple[int, int]:
        return (self.particle_i, self.particle_j)


class InteractionHistory:
    """A time-ordered collection of binary collision events."""

    def __init__(self, events: list[CollisionEvent] | None = None) -> None:
        self._events: dict[int, CollisionEvent] = {}
        for event in events or []:
            self.add(event)

    def add(self, event: CollisionEvent) -> None:
        if event.event_id in self._events:
            raise ValueError(f"duplicate event_id {event.event_id}")
        if event.particle_i == event.particle_j:
            raise ValueError("a collision requires two distinct particles")
        self._events[event.event_id] = event

    @property
    def events(self) -> tuple[CollisionEvent, ...]:
        return tuple(sorted(self._events.values(), key=lambda item: (item.time, item.event_id)))

    def particle_timelines(self) -> dict[int, tuple[int, ...]]:
        timelines: dict[int, list[CollisionEvent]] = defaultdict(list)
        for event in self.events:
            for particle in event.particles:
                timelines[particle].append(event)
        return {
            particle: tuple(event.event_id for event in timeline)
            for particle, timeline in timelines.items()
        }

    def event_edges(self) -> tuple[tuple[int, int, int], ...]:
        """Edges ``(earlier_event, later_event, particle)`` with multiplicity."""

        edges: list[tuple[int, int, int]] = []
        for particle, timeline in self.particle_timelines().items():
            edges.extend((left, right, particle) for left, right in zip(timeline, timeline[1:]))
        return tuple(edges)

    def _adjacency(self) -> dict[int, set[int]]:
        adjacency = {event_id: set() for event_id in self._events}
        for left, right, _particle in self.event_edges():
            adjacency[left].add(right)
            adjacency[right].add(left)
        return adjacency

    def component_count(self) -> int:
        adjacency = self._adjacency()
        unseen = set(adjacency)
        count = 0
        while unseen:
            count += 1
            start = unseen.pop()
            queue = deque([start])
            while queue:
                current = queue.popleft()
                for neighbor in adjacency[current]:
                    if neighbor in unseen:
                        unseen.remove(neighbor)
                        queue.append(neighbor)
        return count

    def circuit_rank(self) -> int:
        """First Betti number of the event multigraph."""

        if not self._events:
            return 0
        return len(self.event_edges()) - len(self._events) + self.component_count()

    def repeated_pair_recollisions(self) -> int:
        pair_counts = Counter(tuple(sorted(event.particles)) for event in self.events)
        return sum(max(count - 1, 0) for count in pair_counts.values())

    def long_bond_count(self, threshold: float) -> int:
        if threshold < 0:
            raise ValueError("threshold must be non-negative")
        return sum(
            self._events[right].time - self._events[left].time >= threshold
            for left, right, _particle in self.event_edges()
        )

    def feature_dict(self, long_bond_threshold: float) -> dict[str, int]:
        particles = {particle for event in self.events for particle in event.particles}
        layers = {event.layer for event in self.events}
        return {
            "events": len(self._events),
            "particles": len(particles),
            "layers": len(layers),
            "components": self.component_count(),
            "circuit_rank": self.circuit_rank(),
            "repeated_pair_recollisions": self.repeated_pair_recollisions(),
            "long_bonds": self.long_bond_count(long_bond_threshold),
        }
