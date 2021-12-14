import numpy as np


def n_fish_v1(t0, days):
    t = t0
    for _ in range(days):
        t -= 1
        t = np.concatenate([t, 8 * np.ones(np.sum(t < 0), dtype=np.uint32)])
        t[t < 0] = 6
    return t.size


def n_fish_v2(t0, days):
    t_counts = np.pad(np.bincount(t0), (0, 8 - t0.max()))
    for _ in range(days):
        n = t_counts[0]
        t_counts = np.roll(t_counts, -1)
        t_counts[6] += n
        t_counts[8] = n
    return np.sum(t_counts)


if __name__ == '__main__':
    with open('input.txt') as f:
        t0 = np.array([int(x) for x in f.read().split(',')])
    print(f"Solution 1: {n_fish_v2(t0, 80)}")
    print(f"Solution 1: {n_fish_v2(t0, 256)}")
