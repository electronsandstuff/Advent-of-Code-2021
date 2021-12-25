import numpy as np
from itertools import product, combinations
import matplotlib.pyplot as plt
from math import prod


def load_ops(path):
    with open(path) as f:
        ops = []
        for line in f.readlines():
            cmd, coords = line.strip().split(' ')
            start, stop = zip(*[tuple(int(y.split('=')[-1]) for y in x.split('..')) for x in coords.split(',')])
            cmin, cmax = zip(*[(min(a, b), max(a, b)) for a, b in zip(start, stop)])
            cmax = tuple(x+1 for x in cmax)
            ops.append({'cmd': cmd, 'start': cmin, 'stop': cmax})
    return ops


def cubes_intersect(a, b):
    """
    Find if two cubes intersect w/ each other
    :param a: cube a, tuple of min, max tuple of coords
    :param b: cube a, tuple of min, max tuple of coords
    :return: bool, if cubes intersect
    """
    for i, j, k, l in zip(a[0], a[1], b[0], b[1]):
        if i >= l or k >= j:
            return False
    return True


def get_cube_intersection(a, b):
    """
    Find the intersection of two cubes.  Note: method returns invalid cube if input cubes do not actually intersect
    :param a: cube a, tuple of min, max tuple of coords
    :param b: cube a, tuple of min, max tuple of coords
    :return: intersecting volume, tuple of min, max tuple of coords
    """
    return tuple(zip(*[(max(i, k), min(j, l)) for i, j, k, l in zip(a[0], a[1], b[0], b[1])]))


def split_cube_axis(c, idx, pos):
    """
    Splits a cube along a single axis and returns the results as a set.  Runs even if there is not intersection.
    :param c: The cube as tuple of tuple ((min coords), (max coords))
    :param idx: int, The axis to split along
    :param pos: list[int] The positions to split.  The split occurs between cubes pos-1 and pos
    :return: set of cubes (tuples of tuples)
    """
    s = set()
    start = c[0][idx]
    for p in sorted(pos):
        if c[0][idx] < p < c[1][idx]:
            s.add((c[0][:idx] + (start,) + c[0][idx + 1:], c[1][:idx] + (p, ) + c[1][idx+1:]))
            start = p
    s.add((c[0][:idx] + (start,) + c[0][idx + 1:], c[1]))
    return s


def can_merge(a, b):
    """
    Test if two cubes may be merged into a single cube (their bounding box)
    :param a: cube a, tuple of tuple ((min coords), (max coords))
    :param b: cube b, tuple of tuple ((min coords), (max coords))
    :return: bool, if cubes can be merged
    """
    c = 0  # Count the number of continued dimensions
    for i, j, k, l in zip(a[0], a[1], b[0], b[1]):
        x = i == k and j == l  # If this dimension matches exactly
        y = i == l or j == k  # If one cube continues the other
        z = y and (c == 0)  # If we are the first dimension to be continued
        if not x and not z:
            return False
        if y:  # Increment the continued dimension count
            c += 1
    return True


def get_bounding_box(a, b):
    """
    Finds bounding box of two cubes as another cube
    :param a: cube a, tuple of tuple ((min coords), (max coords))
    :param b: cube b, tuple of tuple ((min coords), (max coords))
    :return: bounding box, tuple of tuple ((min coords), (max coords))
    """
    return tuple(zip(*[(min(i, k), max(j, l)) for i, j, k, l in zip(a[0], a[1], b[0], b[1])]))


def contains(a, b):
    """
    Test if cube a is contained in cube b
    :param a: cube a, tuple of tuple ((min coords), (max coords))
    :param b: cube b, tuple of tuple ((min coords), (max coords))
    :return: bool, if a in b
    """
    for i, j, k, l in zip(a[0], a[1], b[0], b[1]):
        if i < k or j > l:
            return False
    return True


def cube_subtract(a, b):
    """
    Compute the set of cubes a - b
    :param a: cube a, tuple of tuple ((min coords), (max coords))
    :param b: cube a, tuple of tuple ((min coords), (max coords))
    :return: difference, set of tuples of tuples ((min coords), (max coords))
    """
    if contains(a, b):
        return set()
    if not cubes_intersect(a, b):
        return {a, }
    c = get_cube_intersection(a, b)
    splitting_cube = a
    out_set = set()
    for idx, i in enumerate(zip(*c)):
        s = split_cube_axis(splitting_cube, idx, i)
        for j in s:
            if cubes_intersect(j, c):
                splitting_cube = j
                break
        s.remove(splitting_cube)
        out_set.update(s)
        if splitting_cube == c:
            break
    return out_set


class CubeSet:
    def __init__(self, start=None, stop=None):
        t = [x is None for x in [start, stop]]
        if not any(t):
            self.blocks = {(tuple(start), tuple(stop)), }
        elif all(t):
            self.blocks = set()
        elif not t[0]:
            self.blocks = start
        else:
            raise ValueError('Start and stop must both lists or both None')

    def display(self):
        """
        Plot a 2D cube set using matplotlib
        :return: None
        """
        if not self.blocks:
            plt.plot([], [])
        else:
            if len(next(iter(self.blocks))[0]) != 2:
                raise ValueError('Can only display 2D cube sets')
            for b in self.blocks:
                plt.fill_between([b[0][0]-0.5, b[1][0]-0.5], [b[0][1]-0.5, b[0][1]-0.5], [b[1][1]-0.5, b[1][1]-0.5])
        plt.show()

    def add(self, start, stop):
        """
        Adds a cubes to the set correctly taking into account intersections
        :param start: tuple of starting coords
        :param stop: tuple of ending coords
        :return: None
        """
        self.remove(start, stop)
        self.blocks.add((start, stop))

    def remove(self, start, stop):
        """
        Subtracts cubic volume from the set
        :param start: tuple of starting coords
        :param stop: tuple of ending coords
        :return: None
        """
        self.blocks = set().union(*[cube_subtract(b, (start, stop)) for b in self.blocks])

    def get_volume(self):
        """
        Return total volume contained in set
        :return: int, volume
        """
        return sum(prod(z-y for y, z in zip(*b)) for b in self.blocks)

    def reduce(self, max_iter=1024):
        """
        Merges blocks in the cube set into larger chunks until there are none left to be merged.
        :param max_iter: Max iterations in reduction method before failure
        :return: None
        """
        possible_merges = None
        found = False
        for x in range(max_iter):
            r = set()
            a = set()
            found = False
            it = product(possible_merges, self.blocks) if x else combinations(self.blocks, 2)
            for i, j in it:
                if i == j:
                    continue
                if i not in r and j not in r and can_merge(i, j):
                    r.add(i)
                    r.add(j)
                    a.add(get_bounding_box(i, j))
                    found = True
            self.blocks.difference_update(r)
            self.blocks.update(a)
            possible_merges = a
            if not found:
                break
        if found:
            raise ValueError(f'Reduction not complete when max_iter hit: {max_iter}')


if __name__ == '__main__':
    ops = load_ops('input.txt')

    # Do things the naive way
    side_len = 101
    c = ([-(side_len//2) for _ in range(3)], [side_len//2 for _ in range(3)])
    volume = np.zeros((side_len, side_len, side_len), dtype=bool)
    for op in ops:
        start, stop = get_cube_intersection((op['start'], op['stop']), c)
        idx = tuple(slice(a + side_len//2, b + side_len//2) for a, b in zip(start, stop))
        volume[idx] = op['cmd'] == 'on'
    print(f'Solution 1: {np.sum(volume)}')

    # Do it with intersections
    a = CubeSet()
    for idx, op in enumerate(ops):
        if op['cmd'] == 'on':
            a.add(op['start'], op['stop'])
        else:
            a.remove(op['start'], op['stop'])
    print(f'Solution 2: {a.get_volume()}')
