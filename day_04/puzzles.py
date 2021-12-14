import numpy as np
from io import StringIO


def find_winning_score(boards, chosen_nums, first_last='first'):
    board_state = [np.zeros_like(x, dtype=bool) for x in boards]
    winners = np.zeros(len(boards), dtype=bool)
    for n in chosen_nums:
        # Update the boards
        board_state = [np.bitwise_or(s, b == n) for s, b in zip(board_state, boards)]

        # Check for winning board
        for idx, (b, bs) in enumerate(zip(boards, board_state)):
            if np.bitwise_and.reduce(bs, 0).any() or np.bitwise_and.reduce(bs, 1).any():
                if (np.sum(winners) == winners.shape[0] - 1 and not winners[idx]) or first_last == 'first':
                    return np.sum(b[~bs]) * n
                winners[idx] = True


if __name__ == '__main__':
    # Process the text input
    with open('input.txt') as f:
        pin = f.readlines()
    chosen_nums = [int(x) for x in pin.pop(0).split(',')]
    boards = [np.genfromtxt(StringIO(x), dtype=np.uint32) for x in ''.join(pin).split('\n\n')]

    print(f'Solution 1: {find_winning_score(boards, chosen_nums)}')
    print(f'Solution 2: {find_winning_score(boards, chosen_nums, "last")}')
