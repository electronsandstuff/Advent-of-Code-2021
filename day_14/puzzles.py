def apply_polymerization_step(x, r):
    insertions = ""
    for c1, c2 in zip(x[:-1], x[1:]):
        try:
            insertions += r[c1 + c2]
        except KeyError:
            insertions += ' '
    return ''.join(x + y for x, y in zip(x, insertions)).strip(' ') + x[-1]


def apply_polymerization_step_counts_only(ip, r):
    op = ip.copy()  # Copy so we don't modify input dict (output pairs)
    for p in ip:  # Step through each pair count
        if p in r:  # Interact if there's a rule
            op[p] -= ip[p]  # This pair turns into two others, get rid of it
            for np in [p[0]+r[p], r[p]+p[1]]:  # These are the two new pairs
                if np not in op:  # Add the pairs to the count
                    op[np] = 0
                op[np] += ip[p]
    return op


def count_all_occurances(s):
    occ = {}
    for c in s:
        if c not in occ:
            occ[c] = 0
        occ[c] += 1
    return occ


def first_char_pair_occurances(ps):
    occ = {}
    for p in ps:
        c = p[0]  # Don't double count
        if c not in occ:
            occ[c] = 0
        occ[c] += ps[p]
    return occ


def most_common_char_minus_least_common(o):
    s = sorted([(a, o[a]) for a in o], key=lambda x: x[1])
    return s[-1][1] - s[0][1]


if __name__ == '__main__':
    with open('input.txt') as f:
        template = f.readline().strip()
        f.readline()
        rules = {y[0]: y[1] for y in [x.strip().split(' -> ') for x in f.readlines()]}

    x = template
    for _ in range(10):
        x = apply_polymerization_step(x, rules)
    print(f'Solution 1: {most_common_char_minus_least_common(count_all_occurances(x))}')

    # Count all pairs from template
    pairs = count_all_occurances([a + b for a, b in zip(template[:-1], template[1:])])
    for _ in range(40):  # Apply polymerization 40 times
        pairs = apply_polymerization_step_counts_only(pairs, rules)
    occ = first_char_pair_occurances(pairs)
    occ[template[-1]] += 1
    print(f'Solution 2: {most_common_char_minus_least_common(occ)}')
