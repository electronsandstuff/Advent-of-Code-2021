display = {x: set(y) for x, y in {
    0: 'abcefg',
    1: 'cf',
    2: 'acdeg',
    3: 'acdfg',
    4: 'bcdf',
    5: 'abdfg',
    6: 'abdefg',
    7: 'acf',
    8: 'abcdefg',
    9: 'abcdfg'
}.items()}
len_to_display = {x: [y for y in display if len(display[y]) == x] for x in range(8)}


def is_unique_digit(x):
    return len(len_to_display[len(x)]) == 1


def find_display_mapping(my_in):
    # Start w/ empty list of excluded letters
    exclusions = {x: set() for x in 'abcdefg'}

    # Find excluded letters based on unique length of display segments on
    for i in my_in:
        d = [display[x] for x in len_to_display[len(i)]]
        e = display[8] - set().union(*d)
        f = display[8].intersection(*d)
        for x in i:
            exclusions[x] = exclusions[x].union(e)
        for x in display[8] - i:
            exclusions[x] = exclusions[x].union(f)

    # Add in exclusions for uniquely determined letters
    for e in exclusions:
        if len(exclusions[e]) == 6:
            for f in exclusions:
                if f != e:
                    exclusions[f] = exclusions[f].union(display[8] - exclusions[e])

    # Translate to the mapping
    mapping = {x: next(iter(display[8] - y)) for x, y in exclusions.items()}
    return mapping


def unscramble_digit(o, m):
    """o is the set with the digit's lit up number, m is the digit mapping"""
    return [y for y in display if display[y] == {m[x] for x in o}][0]


if __name__ == '__main__':
    with open('input.txt') as f:
        pin = [{y: [set(z) for z in x.strip().split(' ')] for x, y in zip(l.strip().split('|'), ['ten', 'out'])}
               for l in f.readlines()]

    # Get number of outputs w/ unique length
    n = len([x for x in sum([x['out'] for x in pin], []) if is_unique_digit(x)])
    print(f"Solution 1: {n}")

    # Sum up the decoded letters
    s = sum([int(''.join([str(unscramble_digit(x, find_display_mapping(l['ten']))) for x in l['out']])) for l in pin])
    print(f"Solution 2: {s}")
