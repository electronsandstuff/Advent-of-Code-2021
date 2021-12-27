import numpy as np


char_map = {'>': 1, '.': 2, 'v': 0}
int_map = {0: 'v', 1: '>', 2: '.'}


def step(x):
    n_move = 0
    for ax in [1, 0]:
        moved = np.roll(x, 1, axis=ax)
        can_move_to = np.bitwise_and(moved == ax, x == 2)
        can_move_from = np.roll(can_move_to, -1, axis=ax)
        x[can_move_to] = ax
        x[can_move_from] = 2
        n_move += np.sum(can_move_to)
    return n_move


def display(x):
    print('\n'.join(''.join(int_map[j] for j in i) for i in x))


def find_step_last_moved(x, max_iter=4096):
    y = np.copy(x)
    i = 0
    j = -1
    for j in range(max_iter):
        i = step(y)
        if i == 0:
            break
    if i:
        raise ValueError(f'Could not find stopping condition before max_iter reached: {max_iter}')
    return j + 1


if __name__ == '__main__':
    with open('input.txt') as f:
        x = np.array([[char_map[y] for y in x.strip()] for x in f.readlines()])
    print(f'Solution 1: {find_step_last_moved(x)}')
    print('Solution 2: *just push a button on the website*')
