import numpy as np


def octopus_step(h0):
    es = [np.zeros_like(h0), np.ones_like(h0)]  # List of added energy as we converge
    while np.sum(es[-1]) > np.sum(es[-2]):  # Continue until no more octopuses flash
        flash = np.pad(h0 + es[-1] > 9, 1)
        ns = [(2, flash.shape[0]), (1, -1), (0, -2)]  # All neighbors convolution, subtract center pixel
        es.append(1 + sum(flash[i[0]:i[1], j[0]:j[1]] for i in ns for j in ns) - flash[1:-1, 1:-1])
    h = h0 + es[-1]  # Compute the new final energies
    h[h > 9] = 0  # Zero out flashed octopuses
    return h


if __name__ == '__main__':
    with open('input.txt') as f:
        h = np.array([[int(y) for y in x.strip()] for x in f.readlines()])

    flashes = 0
    for _ in range(100):
        h = octopus_step(h)
        flashes += np.sum(h == 0)
    print(f'Solution 1: {flashes}')

    for i in range(1000):
        h = octopus_step(h)
        if (h == 0).all():
            print(f'Solution 2: {i + 100 + 1}')
            break
