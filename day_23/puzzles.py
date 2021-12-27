import re
import numpy as np
from queue import PriorityQueue


pattern = re.compile('[\W_]+')  # Regex pattern for stripping non-alphanumeric characters from string
type_costs = {
    ord('A'): 1,
    ord('B'): 10,
    ord('C'): 100,
    ord('D'): 1000,
}


class BoardState:
    def __init__(self, n_room=4, room_size=2):
        self.state = np.zeros((room_size + 1, 3 + 2*n_room), dtype=int)
        self.mask = np.zeros_like(self.state, dtype=bool)
        self.mask[0] = True
        for i in range(n_room):
            self.mask[:, 2 + 2*i] = True

    def read(self, p):
        with open(p) as f:
            queue = [pattern.sub('', x) for x in f.readlines()]
            self.__init__(max(map(len, queue)), sum(map(bool, queue)))
            self.state[1:, 2:-2:2] = np.array([list(map(ord, x)) for x in queue if x])

    def __str__(self):
        r = "#" * (self.state.shape[1] + 2)
        for idx1, q in enumerate(zip(self.state, self.mask)):
            r += "\n " if idx1 > 1 else "\n#"
            for idx2, (v, o) in enumerate(zip(*q)):
                out = idx1 > 1 and (idx2 < 1 or idx2 > self.state.shape[1] - 2)  # Are we outside the walls?
                r += " " if out else ((chr(v) if v else '.') if o else "#")
            r += " " if idx1 > 1 else "#"
        r += "\n  " + "#" * (self.state.shape[1] - 2) + "  "
        return r

    def neighbors(self):
        """
        This huge method returns a generator for all the neighboring states and the costs to get to them from this state
        :return: the generator which returns pairs (new state, cost to get there)
        """
        for i in np.argwhere(np.bitwise_and(self.state == 0, self.mask)):  # Iterate over unoccupied positions
            if i[0] == 0 and 1 < i[1] < (self.state.shape[1] - 2) and i[1] % 2 == 0:
                continue  # Skip the positions in front of rooms
            for j in np.argwhere(np.bitwise_and(self.state > 0, self.mask)):  # Iterate over game pieces
                if i[0] == 0 and j[0] == 0:  # If moving in the hallway
                    continue  # Amphipods can't move from hallway to hallway
                if i[1] == j[1]:  # It never makes sense to just travel vertically within a room
                    continue
                if i[0] > 0:  # If we're stopping in a room
                    if (i[1] - 2) // 2 != (self.state[tuple(j)] - ord('A')):
                        continue  # Make sure we only stop in the room right for our type
                    if np.bitwise_and(self.state[1:, i[1]] != 0, self.state[1:, i[1]] != self.state[tuple(j)]).any():
                        continue  # Skip over this state if we'd land in a room with the wrong amphipods
                    if i[0] != (np.max(np.argwhere(self.state[1:, i[1]] == 0)) + 1):
                        continue  # Check that we go into the lowest available open spot in the room
                if j[0] > 0 and (self.state[j[0]:, j[1]] - ord('A') == (j[1] - 2) // 2).all():
                    continue  # Never leave a room if we're already in the right spot
                # Find the straight paths required to go into the new state
                if j[0] > 0 and i[0] == 0:  # room -> hallway
                    paths = [(slice(0, j[0]+1), j[1]), (0, slice(min(i[1], j[1]), max(i[1], j[1]) + 1))]
                elif i[0] > 0 and j[0] == 0:  # hallway -> room
                    paths = [(0, slice(min(i[1], j[1]), max(i[1], j[1])+1)), (slice(0, i[0]+1), i[1])]
                elif i[0] > 0 and j[0] > 0:  # room -> room
                    paths = [
                        (slice(0, i[0]+1), i[1]),
                        (slice(0, j[0] + 1), j[1]),
                        (0, slice(min(i[1], j[1]), max(i[1], j[1])+1)),
                    ]
                else:
                    raise NotImplementedError(f"Can't calculate cost for this change of state {j} -> {i}")

                # Confirm there's nobody in our way
                if sum(np.sum(self.state[x] != 0) for x in paths) > 1:
                    continue

                # Calculate the cost required to go into this state and the state
                state_cost = sum(self.state[x].size - 1 for x in paths) * 10**(self.state[tuple(j)] - ord('A'))
                state = self.copy()
                state.state[tuple(i)] = state.state[tuple(j)]
                state.state[tuple(j)] = 0
                yield state, state_cost

    def __hash__(self):
        return hash((self.state.shape, self.state.tobytes()))

    def copy(self):
        r = BoardState()
        r.state = np.copy(self.state)
        r.mask = np.copy(self.mask)
        return r

    def get_sorted_state(self):
        r = self.copy()
        r.state[:, :] = 0
        for i in range((self.state.shape[1] - 3) // 2):
            r.state[1:, 2 + 2*i] = i + ord('A')
        return r

    def __lt__(self, other):
        return hash(self) < hash(other)

    def __eq__(self, other):
        return (self.state == other.state).all()


def find_shortest_path(start, end):
    """
    Implementation of Dijkstra's algorithm (version from Wikipedia) using a priority queue to keep track of lowest cost
    vertex
    :param start: the initial state
    :param end: the final state
    :return: (minimum cost to get to final state, the path of states to get there)
    """
    # Create initial datastructures
    seen = {start, }
    dist = {start: 0}
    prev = {}

    # Iterate thru the graph using a priority queue to track the minimum distance node
    q = PriorityQueue()
    q.put((0, start))
    while not q.empty():
        # Get the lowest cost state
        _, u = q.get()

        # If this is the final state, construct the path we took and return
        if u == end:
            s = []
            while u in prev:
                s.append(u)
                u = prev[u]
            return dist[end], list(reversed(s))

        # Iterate over neighbor vertices
        for neighbor, ncost in u.neighbors():
            if neighbor in seen:  # Skip states we've already visited
                continue

            # Get the total distance to next vertex
            alt = dist[u] + ncost
            if neighbor not in dist:
                dist[neighbor] = alt + 1  # Hack so we get right behavior in next comparison
            if alt < dist[neighbor]:  # Update the lists if we're the new minimum distance to here
                dist[neighbor] = alt
                prev[neighbor] = u
                q.put((alt, neighbor))
        seen.add(u)  # We're done with this vertex
    raise ValueError('End state could not be reached from start')


if __name__ == '__main__':
    a = BoardState()
    a.read('input1.txt')
    cost, _ = find_shortest_path(a, a.get_sorted_state())
    print(f'Solution 1: {cost}')

    b = BoardState()
    b.read('input2.txt')
    cost, _ = find_shortest_path(b, b.get_sorted_state())
    print(f'Solution 2: {cost}')
