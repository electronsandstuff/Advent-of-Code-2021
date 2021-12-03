import numpy as np


def n_increase(arr):
    return np.sum(arr[1:] > arr[:-1])


if __name__ == '__main__':
    # Read the puzzle input
    with open('input.txt') as f:
        pin = f.readlines()
    depths = np.array([int(x.strip()) for x in pin])

    # Count the number of times the depth increases
    print(f'Puzzle 1 answer: {n_increase(depths)}')

    # Get the sliding window and number of increases
    window = depths[:-2] + depths[1:-1] + depths[2:]
    print(f'Puzzle 2 answer: {n_increase(window)}')
