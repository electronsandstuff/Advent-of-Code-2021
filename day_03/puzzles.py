import numpy as np


def numpy_bool_array_to_int(arr):
    return int(''.join(['1' if x else '0' for x in arr]), 2)


def most_common_bits(arr):
    if arr.shape[0] % 2 == 0:  # Hack to get the tie-breaker rule to work
        return np.sum(arr, axis=0) >= arr.shape[0] // 2
    else:
        return np.sum(arr, axis=0) > arr.shape[0] // 2


def filter_common_bits(arr, most_least='most'):
    myarr = arr
    for col in range(arr.shape[1]):
        # Find the valid rows
        if most_least == 'most':
            bit = most_common_bits(myarr)[col]
        elif most_least == 'least':
            bit = np.bitwise_not(most_common_bits(myarr))[col]
        else:
            raise ValueError("please do better :(")
        idx = myarr[:, col] == int(bit)

        # Select into the new array
        myarr = myarr[idx, :]

        # If theres no more bits, return it
        if myarr.shape[0] == 1:
            break
    return myarr[0] > 0


if __name__ == '__main__':
    # Read the puzzle input
    with open('input.txt') as f:
        pin = f.readlines()

    # Create big numpy array of bits
    bits = np.array([[int(y) for y in x.strip()] for x in pin])

    # Find the two rates from logs
    gamma = numpy_bool_array_to_int(most_common_bits(bits))
    epsilon = numpy_bool_array_to_int(np.bitwise_not(most_common_bits(bits)))
    print(f'Gamma: {gamma}')
    print(f'Epsilon: {epsilon}')
    print(f'Solution 1: {gamma * epsilon}')

    # Run the filtering procedure on the bits
    o2_rate = numpy_bool_array_to_int(filter_common_bits(bits, most_least='most'))
    co2_rate = numpy_bool_array_to_int(filter_common_bits(bits, most_least='least'))
    print(f'o2_rate: {o2_rate}')
    print(f'co2_rate: {co2_rate}')
    print(f'Solution 2: {o2_rate * co2_rate}')
