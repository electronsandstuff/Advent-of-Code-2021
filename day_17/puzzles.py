import numpy as np
import re


def solve_motion(vi, n_step=32, coord='y'):
    # Initialize the coordinates
    n = vi.size
    x = np.empty((n_step+1, 2*n), dtype=int)
    x[0, :n] = 0  # Positions
    x[0, n:] = vi  # Velocities

    # Run through steps
    for i in range(n_step):
        x[i+1, :n] = x[i, n:] + x[i, :n]
        if coord == 'x':
            x[i + 1, n:] = x[i, n:] - np.sign(x[i, n:])
        elif coord == 'y':
            x[i+1, n:] = x[i, n:] - 1
        else:
            raise ValueError("I'm disappointed in you :(")
    return x


if __name__ == '__main__':
    with open('input.txt') as f:
        t = [int(x) for x in re.search('x=([0-9-]+)\.\.([0-9-]+), y=([0-9-]+)\.\.([0-9-]+)', f.readline()).groups()]

    # Simulate a ton of initial conditions
    vs = np.arange(1024) - 512
    yy = solve_motion(vs, n_step=512, coord='y')

    # Filter to find the best height
    valididx = np.bitwise_and(t[2] <= yy[:, :len(vs)], yy[:, :len(vs)] <= t[3]).any(axis=0)
    max_y = np.max(yy[:, :len(vs)][:, valididx])
    print(f'Solution 1: {max_y}')

    # We already have y computed, now check x
    xx = solve_motion(vs, n_step=512, coord='x')
    valididx = np.bitwise_and(  # Find all instances where x and y are valid at the same timestep
        np.bitwise_and(t[0] <= xx[:, :len(vs)], xx[:, :len(vs)] <= t[1])[:, :, None],
        np.bitwise_and(t[2] <= yy[:, :len(vs)], yy[:, :len(vs)] <= t[3])[:, None, :]
    ).any(axis=0)
    print(f'Solution 2: {np.sum(valididx)}')
