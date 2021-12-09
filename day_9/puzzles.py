import numpy as np


def pad_h(h):
    # Pad the map with 10's (IE infinity in this problem)
    hp = np.ones(tuple(x + 2 for x in h.shape), dtype=np.int32) * 10
    hp[1:-1, 1:-1] = h
    return hp


def get_low_points(h):
    h_padded = pad_h(h)
    up = h < h_padded[:-2, 1:-1]
    down = h < h_padded[2:, 1:-1]
    left = h < h_padded[1:-1, :-2]
    right = h < h_padded[1:-1, 2:]
    return up & down & left & right


def label_basins(h):
    """My messy implementation of blob detection"""
    foreground = pad_h(h) < 9
    labels = np.zeros_like(foreground, dtype=np.int32)
    q = []
    l = 1
    for i in range(h.shape[0]):
        for j in range(h.shape[1]):
            if foreground[i+1, j+1] and labels[i+1, j+1] == 0:
                labels[i+1, j+1] = l
                q.append(np.array([i+1, j+1]))

                while q:
                    idx = q.pop()
                    for n in [np.array(x, dtype=np.int32) for x in [[1, 0], [-1, 0], [0, 1], [0, -1]]]:
                        if foreground[tuple(idx + n)] and labels[tuple(idx + n)] == 0:
                            labels[tuple(idx + n)] = l
                            q.append(idx + n)
                l += 1
    return labels[1:-1, 1:-1]


if __name__ == '__main__':
    with open('input.txt') as f:
        h = np.array([[int(y) for y in x.strip()] for x in f.readlines()])

    # Find the low points
    low_point = get_low_points(h)
    risk = np.sum(h[low_point] + 1)
    print(f'Solution 1: {risk}')

    # Find basins and their size
    b = label_basins(h)
    bs = sorted([np.sum(b == x + 1) for x in range(b.max())])[::-1]
    print(f'Solution 2: {bs[0]*bs[1]*bs[2]}')
