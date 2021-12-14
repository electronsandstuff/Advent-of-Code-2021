import numpy as np
import matplotlib.pyplot as plt


axes = {'x': 0, 'y': 1}


def fold(p, axis, val):
    s2 = p.shape[axis] - val - 1
    m1 = max(0, max(val, s2) - val)
    m2 = max(0, max(val, s2) - s2)
    if axis == 0:
        return np.bitwise_or(
            np.pad(p[:val, :][::-1, :], ((0, m1), (0, 0))),
            np.pad(p[val+1:, :], ((0, m2), (0, 0)))
        )
    elif axis == 1:
        return np.bitwise_or(
            np.pad(p[:, :val][:, ::-1], ((0, 0), (0, m1))),
            np.pad(p[:, val+1:], ((0, 0), (0, m2)))
        )
    raise ValueError('Help me :(')


if __name__ == '__main__':
    pairs = []
    folds = []
    with open('input.txt') as f:
        while True:
            l = f.readline().strip()
            if not l:
                break
            pairs.append(tuple(int(x) for x in l.split(',')))
        for l in f.readlines():
            folds.append(l.strip().split(' ')[-1].split('='))
    pairs = np.array(pairs)

    paper = np.zeros([np.max(pairs[:, i] + 1) for i in range(2)], dtype=bool)
    paper[pairs[:, 0], pairs[:, 1]] = True

    print(f'Solution 1: {np.sum(fold(paper, axes[folds[0][0]], int(folds[0][1])))}')

    for f in folds:
        paper = fold(paper, axes[f[0]], int(f[1]))

    print("Plotting solution 2")
    plt.imshow(np.rot90(np.rot90(paper.T)))
    plt.show()
