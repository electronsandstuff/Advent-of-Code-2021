termination = {'(': ')', '{': '}', '[': ']', '<': '>'}
err_score = {')': 3, ']': 57, '}': 1197, '>': 25137}
cmp_score = {'(': 1, '[': 2, '{': 3, '<': 4}


def open_char_list_to_cmp_score(arr, score=0):
    if arr:
        return open_char_list_to_cmp_score(arr[:-1], 5 * score + cmp_score[arr[-1]])
    return score


def parse_line(l):
    o = []
    for c in l:
        if c in termination:
            o.append(c)
        elif c != termination[o.pop()]:
            return {'err': err_score[c], 'cmp': None}
    return {'err': 0, 'cmp': open_char_list_to_cmp_score(o)}


def middle(arr):
    return arr[(len(arr) - 1)//2]


if __name__ == '__main__':
    with open('input.txt') as f:
        lines = [x.strip() for x in f.readlines()]

    ps = [parse_line(l) for l in lines]
    print(f'Solution 1: {sum(p["err"] for p in ps)}')
    print(f'Solution 2: {middle(sorted(p["cmp"] for p in ps if p["cmp"]))}')
