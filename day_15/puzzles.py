import numpy as np


def solve_shortest_path_2d(m, max_iter=4096):
    converged = False
    cs = [np.zeros_like(m, dtype=float), ]
    for _ in range(max_iter):
        cp = np.pad(cs[-1], 1, constant_values=np.inf)
        costs = np.concatenate((
            (cp[:-2, 1:-1] + m)[:, :, None],
            (cp[2:, 1:-1] + m)[:, :, None],
            (cp[1:-1, :-2] + m)[:, :, None],
            (cp[1:-1, 2:] + m)[:, :, None],
        ), axis=2)
        costs[-1, -1, :] = 0
        cs.append(np.min(costs, axis=2))
        if (cs[-2] == cs[-1]).all():
            converged = True
            break
        cs.pop(0)
    if not converged:
        raise ValueError(f'Path did not converge after {max_iter} iterations.  Try increasing max_iter')
    return cs[-1] - m + m[-1, -1]  # Correct to count entering into node, not leaving node


def get_tiled_map(m, n=5):
    o = np.empty((m.shape[0]*n, m.shape[1]*n))
    for i in range(n):
        for j in range(n):
            o[i*m.shape[0]:(i+1)*m.shape[0], j*m.shape[1]:(j+1)*m.shape[1]] = (m + i + j - 1) % 9 + 1
    return o


if __name__ == '__main__':
    with open('input.txt') as f:
        m = np.array([[int(y) for y in x.strip()] for x in f.readlines()])

    print(f'Solution 1: {int(solve_shortest_path_2d(m)[0, 0])}')
    print(f'Solution 2: {int(solve_shortest_path_2d(get_tiled_map(m, n=5))[0, 0])}')
