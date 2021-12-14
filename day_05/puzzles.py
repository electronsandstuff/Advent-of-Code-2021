import numpy as np


def generate_map(lines, diags=False):
    vents = np.zeros((np.max(lines[:, :, 1]) + 1, np.max(lines[:, :, 0]) + 1), dtype=np.uint32)
    for l in lines:
        if l[0][0] == l[1][0]:  # horizontal line
            vents[np.min(l[:, 1]):np.max(l[:, 1]) + 1, l[0][0]] += 1
        elif l[0][1] == l[1][1]:  # vertical line
            vents[l[0][1], np.min(l[:, 0]):np.max(l[:, 0])+1] += 1
        elif diags:
            n = np.abs(l[1] - l[0])[0] + 1  # number of points in line
            d = (l[1] - l[0])//(n - 1)  # direction vector
            for i in range(n):
                vents[tuple(reversed(tuple(zip(l[0] + i * d))))] += 1  # **shrug emoji**
    return vents


if __name__ == '__main__':
    # Process the text input
    with open('input.txt') as f:
        pin = f.readlines()
    lines = np.array([[[int(z) for z in y.split(',')] for y in x.strip().split('->')] for x in pin])

    # Generate the grid of line overlaps
    print(f"Solution 1: {np.sum(generate_map(lines) > 1)}")
    print(f"Solution 2: {np.sum(generate_map(lines, diags=True) > 1)}")
