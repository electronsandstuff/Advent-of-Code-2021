import numpy as np


def crab_fuel(n):
    return (n**2 + n) // 2


if __name__ == '__main__':
    with open('input.txt') as f:
        pin = np.array([int(x) for x in f.read().split(',')])

    distances = np.abs(pin[None, :] - np.arange(pin.max() + 1)[:, None])
    total_fuel = np.sum(distances, axis=1)
    print(f'Solution 1: {total_fuel.min()}')

    distances_v2 = crab_fuel(distances)
    total_fuel_v2 = np.sum(distances_v2, axis=1)
    print(f'Solution 2: {total_fuel_v2.min()}')
