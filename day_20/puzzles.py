from itertools import product


neighbors = [(i, j) for i in range(-1, 2) for j in range(-1, 2)]


class InfiniteImage:
    def __init__(self, n=2):
        self.max, self.min = ([0 for _ in range(n)] for _ in range(2))
        self.n = n
        self.lit_pixels = set()
        self.outer_value = 0  # The value of pixels outside our bounding box.  Can flip in enhancement algorithm

    def read(self, txt):
        self.lit_pixels = {(i, j) for i, r in enumerate(txt.strip().split('\n')) for j, e in enumerate(r) if e == '#'}
        self.calc_bounds()

    def get_n_lit_pixels(self):
        if self.outer_value:
            return float('inf')
        return len(self.lit_pixels)

    def display(self):
        self.assert_2d()
        if self.outer_value:
            raise RuntimeError("Cannot render an infinite number of pixels")
        d = [range(a, b+1) for a, b in zip(self.min, self.max)]
        for i in d[0]:
            print(''.join(['#' if (i, j) in self.lit_pixels else '.' for j in d[1]]))

    def enhance(self, algo):
        self.assert_2d()
        self.lit_pixels = {
            (i, j) for i, j in product(*[range(n-1, x+2) for n, x in zip(self.min, self.max)])
            if algo[sum([1 << 8-k for k, n in enumerate(neighbors) if (i+n[0], j+n[1]) in self.lit_pixels
                         or (self.outer_value and not self.in_bounds(i+n[0], j+n[1]))])]  # Handle lit outside pixels
        }
        self.outer_value = algo[self.outer_value * 511]
        self.calc_bounds()

    def calc_bounds(self):
        self.min, self.max = zip(*[(min(x), max(x)) for x in zip(*self.lit_pixels)])

    def assert_2d(self):
        if self.n != 2:  # Only going to write stuff for 2D, good luck otherwise
            raise ValueError("you better not cry, you better not pout")

    def in_bounds(self, *idx):
        return all([m <= i <= x for m, i, x in zip(self.min, idx, self.max)])


if __name__ == '__main__':
    with open('input.txt') as f:
        alg = [1 if x == '#' else 0 for x in f.readline().strip()]
        f.readline()
        img = InfiniteImage()
        img.read(f.read())

    for _ in range(2):
        img.enhance(alg)
    print(f'Solution 1: {img.get_n_lit_pixels()}')
    for _ in range(48):
        img.enhance(alg)
    print(f'Solution 2: {img.get_n_lit_pixels()}')
