def add_to_map(start, end, m):
    if start not in m:
        m[start] = []
    m[start].append(end)


def count_paths(cave, start='start', p=None, extra_visits=None):
    if p is None:
        p = ['start', ]
    if extra_visits is None:
        extra_visits = []

    n = 0  # Count number of paths at this node
    for c in cave[start]:
        if c == 'end':
            n += 1
        elif c.isupper() or c not in p:
            n += count_paths(cave, start=c, p=p + [c, ], extra_visits=extra_visits)
        elif c in extra_visits:
            n += count_paths(cave, start=c, p=p + [c, ], extra_visits=[x for x in extra_visits if x != c])

    return n


if __name__ == '__main__':
    cave = {}
    with open('input.txt') as f:
        for l in f.readlines():
            s = l.strip().split('-')
            add_to_map(s[0], s[1], cave)
            add_to_map(s[1], s[0], cave)

    base_paths = count_paths(cave)
    print(f'Solution 1: {base_paths}')
    all_paths = base_paths + sum(count_paths(cave, extra_visits=[x, ]) - base_paths
                                 for x in cave if x.islower() and x != 'start')
    print(f'Solution 2: {all_paths}')
