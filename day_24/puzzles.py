from itertools import groupby


def int_if_can(x):
    try:
        return int(x)
    except ValueError:
        return x


def block_in_reverse(w, z_final, c0, c1, c2):
    z = set()
    a = z_final - w - c2
    if 0 <= w - c1 < 26:
        z.add(w - c1 + z_final * c0)
    if a % 26 == 0:
        z.add(a // 26 * c0)
    return z


def run_block(w, z, c0, c1, c2):
    a = z // c0
    if w != (z % 26 + c1):
        return 26*a + w + c2
    return a


def find_serial_number(c, min_max='max'):
    if min_max == 'max':
        ws = range(1, 10)
    elif min_max == 'min':
        ws = list(reversed(range(1, 10)))
    else:
        ws = None
        ValueError(f"min_max can only be one of ('min', 'max') not '{min_max}'")

    zs = {0, }
    z_to_digits = {}
    for block in reversed(c):
        zs2 = set()
        for w in ws:
            for z in zs:
                for z2 in block_in_reverse(w, z, *block):
                    zs2.add(z2)
                    if z not in z_to_digits:
                        z_to_digits[z] = []
                    z_to_digits[z2] = [w, ] + z_to_digits[z]
        zs = zs2
    return ''.join(str(x) for x in z_to_digits[0])


if __name__ == '__main__':
    with open('input.txt') as f:
        ops = [tuple(int_if_can(y) for y in x.strip().split(' ')) for x in f.readlines()]

    """
    By manual inspection of the code, each digit is treated by the same set of instructions and inside of that digit set
    the x and y registers are initialized to zero before any further operations are performed.  This means that each
    digit is only affected by the w and z register from any code before it.  However, each digit set also has an input
    going to register w.  My plan is to run the code backwards through each set of instructions and iterate over all the
    allowed digit inputs to that block.  I'll find the largest digit that causes the right output and the z input(s)
    required to make this happen.  The issue is then that we require the z register is initialized to zero at the
    program's start.  I need to keep track of the mapping z -> (largest valid digits) and then just choose z = 0 at the
    end.
    
    Since the input is fixed, I will try and work out the explicit function to reverse a single set of operations for
    one digit.  Here is one block.  Each block only differs by three constants which I call C0, C1, and C2.  This is
    found by inspection of the code with the help of python.
    inp w
    mul x 0
    add x z
    mod x 26
    div z C0
    add x C1
    eql x w
    eql x 0
    mul y 0
    add y 25
    mul y x
    add y 1
    mul z y
    mul y 0
    add y w
    add y C2
    mul y x
    add z y
    
    Reading the code give me:
    def block(w, z, c0, c1, c2):
        x = z % 26 + c1
        z = z // c0
        x = w != x
        y = x * 25 + 1
        z = y * z
        y = (w + c2)*x
        z += y
        return z
    
    def run_block(w, z, c0, c1, c2):  # Further refinement
        a = z // c0
        if w != (z % 26 + c1):
            return 26*a + w + c2
        return a
              
    Reversing this to find the values of z that go through this gives
    
    def block_in_reverse(w, z_final, c0, c1, c2):
        z = set()
        a = z_final - w - c2
        b = w - c1
        if 0 <= b < 26:
            z.add(w - c1 + z_final*c0)
        if not a % 26:
            z.add(a // 26 * c0)
        return z
    """

    # Group the code by digit
    digit_ops = [list(g) for k, g in groupby(ops, lambda x: x[0] == 'inp') if not k]

    # Print out the right operand to see which ones change
    # for o in digit_ops:
    #     print("".join([str(x[-1]).rjust(4) for x in o]))

    # Extract constants from the code
    c = [(o[3][-1], o[4][-1], o[14][-1]) for o in digit_ops]

    # Run the problem
    print(f'Solution 1: {find_serial_number(c, "max")}')
    print(f'Solution 2: {find_serial_number(c, "min")}')
