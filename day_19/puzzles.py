import numpy as np
from itertools import permutations, product
from functools import lru_cache


def read_probes(path):
    """
    Reads probes from files and returns list of numpy arrays where each numpy array is (m, n) and contains the m
    observations of n-dimensional probes.
    :param path: path to the file containing probe info
    :return: list of numpy arrays as described above
    """
    with open(path) as f:
        probes = []
        for l in f.readlines():
            if '---' in l:
                probes.append([])
            try:
                probes[-1].append([int(x) for x in l.strip().split(',')])
            except ValueError:
                pass
        probes = [np.array(p) for p in probes]
    return probes


@lru_cache()
def generate_rotation_matrices(n):
    """
    Generate all rotations by 90 degrees in n dimensional space (includes identity)

    :param n: dimension of space
    :return: np.ndarray, (m, n, n) where m is the number of generated rotations
    """
    rs = []
    for combo in permutations(range(n)):
        for val in product(*[[1, -1]]*n):
            r = np.zeros((n, n), dtype=int)
            for idx1, (idx2, v) in enumerate(zip(combo, val)):
                r[idx1, idx2] = v
            if np.linalg.det(r) > 0:  # Only consider right handed coordinate systems
                rs.append(r)
    return np.array(rs)


def find_transformation(a, b, min_points=12):
    """
    Given the two sets of points a and b, finds the transformation which when applied to set b maps as many points onto
    a as possible.  If the number of mapped points is less than min_points, an error is thrown.  Works by explicitly
    evaluating all the possible transformations and looking for matches.  REALLY SLOW :(
    :param a: np.ndarray (m, n) list of m n-dimensional points in set a
    :param b: np.ndarray (l, n) list of l n-dimensional points in set b
    :param min_points: minimum number of matching points to get a transformation
    :return: r, t, the rotation matrix and translation vector that brings set b into set a
    """
    rs = generate_rotation_matrices(b.shape[1])  # Generate all possible rotations
    b_rot = np.einsum('ijk,lk->ilj', rs, b)  # Transform by all rotations
    ts = a[None, :, None, :] - b_rot[:, None, :, :]  # Generate all possible translations to bring rotated b into a
    b_trns = b_rot[:, None, None, :, :] + ts[:, :, :, None, :]  # indices (rotat., transl. 1, transl. 2, beacon , dim.)
    matches = np.sum((b_trns[None, :, :, :, :, :] == a[:, None, None, None, None, :]).all(axis=-1).any(axis=0), axis=-1)
    if (matches >= min_points).any():  # If any transformation has 12 matching points
        idx = np.unravel_index(np.argmax(matches), matches.shape)  # Find the optimal transformation and return it
        return rs[idx[0]], ts[idx[0], idx[1], idx[2]]
    else:
        raise ValueError(f'Unable to match the minimum number of points between sets: {min_points}')


def find_pairwise_transformations(probes, max_iter=64):
    """
    Given a list of sets of beacons from the perspective of different probes returns the list of lists where the element
    r[i][j] is the transformation that maps probe j's coordinate system to probe i's.  This transformation is the tuple
    r, t where r is a rotation matrix and t is a translation vector.  This method may fail with an exception if there
    are isolated patches of beacons that cannot be linked together.
    :param probes: list of np.array's. each array is (m, n) and represents m observed beacons in n-dimensional space
    :param max_iter: Max iterations in the transformation completion method before failing
    :return: list of lists where elements are as described in body of docstring
    """
    ts = [[None for _ in probes] for _ in probes]
    for i in range(len(probes)):
        ts[i][i] = np.identity(3), np.zeros(3)
    for idx1, i in enumerate(probes):
        for idx2, j in enumerate(probes):
            if idx2 > idx1:
                try:
                    r, t = find_transformation(i, j)
                    ts[idx1][idx2] = r, t
                    ts[idx2][idx1] = np.linalg.inv(r), -1 * np.linalg.inv(r) @ t
                except ValueError:
                    pass

    # Iterate to find all transformations to other nodes
    found = False
    for _ in range(max_iter):
        for idx1, i in enumerate(ts):
            for idx2, j in enumerate(i):
                if j is not None:
                    for idx3, k in enumerate(ts[idx2]):
                        if k is not None:
                            ts[idx1][idx3] = j[0] @ k[0], j[1] + j[0] @ k[1]
        found = all([None not in t for t in ts])
        if found:
            break
    if not found:
        ValueError(f'Could not find all transformations by time max iterations reached: {max_iter}')
    return ts


if __name__ == '__main__':
    probes = read_probes('input.txt')
    ts = find_pairwise_transformations(probes)

    # Merge together the beacons into the first probe's coordinate system
    merged_probes = set()
    for p, t in zip(probes, ts[0]):
        merged_probes = merged_probes.union(set(tuple(u) for u in p @ t[0].T + t[1]))
    print(f'Solution 1: {len(merged_probes)}')

    # Find the probe locations in the first scanner's coordinate system and get pairwise distance
    pl = np.array([t[1] for t in ts[0]])
    manhattan = np.sum(np.abs(pl[:, None, :] - pl[None, :, :]), axis=-1).astype(int)
    print(f'Solution 2: {manhattan.max()}')
