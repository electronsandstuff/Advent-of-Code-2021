import numpy as np


def deterministic_dice_rolls():
    val = 1
    while True:
        yield val
        val = (val % 100) + 1


def get_winning_scores(positions, d, winning_score=1000, n_roll=3, max_rounds=1024):
    scores = [0 for _ in positions]
    positions = list(positions)
    for i in range(max_rounds):
        for j, x in enumerate(positions):
            positions[j] = (x + sum(next(d) for _ in range(n_roll)) - 1) % 10 + 1
            scores[j] = scores[j] + positions[j]
            if scores[j] >= winning_score:  # Winning condition
                return scores, i * n_roll * len(positions) + n_roll * (j + 1)
    raise ValueError(f'Nobody won before max rounds was reached: {max_rounds}')


def count_wins(positions, n_rolls=3, max_dice_value=3, max_score=21, max_rounds=32, n_positions=10):
    """
    Count the distribution of positions and scores of both players instead of explicitly running games.  I guess this
    does have a quantum-ish feel to it :)
    :param positions: list of player starting positions
    :param n_rolls: number of die rolls per player's turn
    :param max_dice_value: maximum value on the die
    :param max_score: score players must reach to win
    :return: np.array (m, ) for m players, their wins
    """
    # Element counts_{i,j,k,l} represents the number of universes where player 1 is on position i and has score k and
    # player 2 is on position j and has score l
    counts = np.zeros((n_positions, n_positions, max_score, max_score), dtype=np.uint64)
    counts[positions[0]-1, positions[1]-1, 0, 0] = 1  # Start us out at the intial position
    wins = np.zeros(len(positions), dtype=np.uint64)
    for _ in range(max_rounds):  # This loops over rounds in the game
        for pidx in range(2):  # Each player's turn
            for _ in range(n_rolls):  # Player rolls die n times and we update the counts
                counts = np.sum([np.roll(counts, i, axis=pidx) for i in range(1, max_dice_value+1)], axis=0)
            for sidx in range(counts.shape[0]):  # Handle incrementing score for each pawn position
                # The following tuple indexes all counts with the current player on position sidx
                idx = ([sidx, slice(None)][pidx], [slice(None), sidx][pidx], slice(None), slice(None))
                counts[idx] = np.roll(counts[idx], sidx+1, axis=pidx+1)  # Increment the score with rollover to start
                idx = (  # This tuple indexes just the values that rolled over during score increment
                    [sidx, slice(None)][pidx],
                    [slice(None), sidx][pidx],
                    [slice(sidx+1), slice(None)][pidx],
                    [slice(None), slice(sidx+1)][pidx]
                )
                wins[pidx] += np.sum(counts[idx])  # Sum up the values that rolled over, these are winners
                counts[idx] = 0  # Remove winners from play
    return wins


if __name__ == '__main__':
    with open('input.txt') as f:
        positions = tuple(int(x.strip()[-2:]) for x in f.readlines())

    d = deterministic_dice_rolls()
    s, i = get_winning_scores(positions, deterministic_dice_rolls())
    print(f'Solution 1: {min(s)*i}')

    wins = count_wins(positions)
    print(f'Solution 2: {max(wins)}')
