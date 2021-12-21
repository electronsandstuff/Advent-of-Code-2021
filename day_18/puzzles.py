explode_tests = [
    {'test': '[[[[[9,8],1],2],3],4]', 'ref': '[[[[0,9],2],3],4]'},
    {'test': '[7,[6,[5,[4,[3,2]]]]]', 'ref': '[7,[6,[5,[7,0]]]]'},
    {'test': '[[6,[5,[4,[3,2]]]],1]', 'ref': '[[6,[5,[7,0]]],3]'},
    {'test': '[[3,[2,[1,[7,3]]]],[6,[5,[4,[3,2]]]]]', 'ref': '[[3,[2,[8,0]]],[9,[5,[4,[3,2]]]]]'},
    {'test': '[[3,[2,[8,0]]],[9,[5,[4,[3,2]]]]]', 'ref': '[[3,[2,[8,0]]],[9,[5,[7,0]]]]'},
]


def parse_snailfish_number(a):
    try:
        return int(a)
    except ValueError:
        pass

    brackets = []
    elems = ['', ]
    for c in a:
        if c == '[':
            brackets.append(c)
        elif c == ']':
            brackets.pop()
        elif c == ',' and len(brackets) < 2:
            elems.append('')
        elems[-1] += c
    elems = [i[1:] for i in elems]
    elems[-1] = elems[-1][:-1]

    return tuple(parse_snailfish_number(i) for i in elems)


def read_snailfish_numbers(path):
    with open(path) as f:
        ns = [parse_snailfish_number(a.strip()) for a in f.readlines()]
    return ns


def snailfish_sum(arr):
    s = snailfish_reduce((arr[0], arr[1]))
    for n in arr[2:]:
        s = snailfish_reduce((s, n))
    return s


def add_to_node(x, val, idx):
    if isinstance(x, int):
        return x + val
    return x[:idx] + (add_to_node(x[idx], val, idx), ) + x[idx+1:]


def explode(x):
    a, b, c = explode_internal(x)
    if not c:
        raise ValueError("Unable to explode input")
    return a


def explode_internal(a, i=0, exp_depth=4):
    if isinstance(a, int):  # Handle leaf nodes
        return a, [], False
    if i >= exp_depth and all(isinstance(x, int) for x in a):  # Explode pair of fundamental numbers at the right level
        return 0, [{'val': x, 'upidx': 2*idx-1, 'dwnidx': 1-idx} for idx, x in enumerate(a)], True

    for idx, x in enumerate(a):  # Recurse on remaining nodes
        res, add, exp = explode_internal(x, i+1, exp_depth=exp_depth)
        a = a[:idx] + (res, ) + a[idx+1:]
        if add:  # Process any additions from the explosion
            for y in add:
                y['upidx'] = min(y['upidx'], len(a) - 1) + idx
                if 0 <= y['upidx'] < len(a):
                    a = a[:y['upidx']] + (add_to_node(a[y['upidx']], y['val'], y['dwnidx']), ) + a[y['upidx']+1:]
        if exp:  # Return the explosion if it happened, return additions if they lie outside of this node
            return a, [x for x in add if x['upidx'] < 0 or x['upidx'] > len(a) - 1], True
    return a, [], False


def split(a):
    b, c = split_internal(a)
    if not c:
        raise ValueError("Unable to split input")
    return b


def split_internal(a):
    if isinstance(a, int):
        if a > 9:
            return (a // 2, a // 2 + (a % 2)), True
    else:
        for idx, x in enumerate(a):
            res, spl = split_internal(x)
            if spl:
                return a[:idx] + (res, ) + a[idx+1:], True
    return a, False


def snailfish_reduce(a, max_red=1024):
    changed = True
    out = a
    for _ in range(max_red):
        changed = False
        for red_op in [explode, split, ]:
            try:
                out = red_op(out)
                changed = True
                break
            except ValueError:
                pass
        if not changed:
            break
    if changed:
        raise ValueError(f'Max reductions exceeded: {max_red}')
    return out


def snailfish_magnitude(a):
    if isinstance(a, int):
        return a
    return 3*snailfish_magnitude(a[0]) + 2*snailfish_magnitude(a[1])


def max_magnitude(a):
    mag = 0
    for i in a:
        for j in a:
            mag = max(mag, snailfish_magnitude(snailfish_sum([i, j])))
    return mag


if __name__ == '__main__':
    for et in explode_tests:
        assert(explode(parse_snailfish_number(et['test'])) == parse_snailfish_number(et['ref']))
    for i in range(5):
        assert(snailfish_sum(read_snailfish_numbers(f'test{i}.txt')) == read_snailfish_numbers(f'ref{i}.txt')[0])
    assert(snailfish_magnitude(snailfish_sum(read_snailfish_numbers(f'hw1.txt'))) == 4140)
    print(f"Solution 1: {snailfish_magnitude(snailfish_sum(read_snailfish_numbers(f'input.txt')))}")
    assert(max_magnitude(read_snailfish_numbers(f'hw1.txt')) == 3993)
    print(f"Solution 2: {max_magnitude(read_snailfish_numbers(f'input.txt'))}")
