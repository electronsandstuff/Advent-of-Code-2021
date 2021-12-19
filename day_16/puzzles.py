from math import prod


examples = {
    'literal': 'D2FE28',
    'op1': '38006F45291200',
    'op2': 'EE00D40C823060',
    'additional0': '8A004A801A8002F478',
    'additional1': '620080001611562C8802118E34',
    'additional2': 'C0015000016115A2E0802F182340',
    'additional3': 'A0016C880162017C3686B18A3D4780',
    'operators0': 'C200B40A82',
    'operators1': '04005AC33890',
    'operators2': '880086C3E88112',
    'operators3': 'CE00C43D881120',
    'operators4': 'D8005AC2A8F0',
    'operators5': 'F600BC2D8F',
    'operators6': '9C005AC2F8F0',
    'operators7': '9C0141080250320F1802104A08',
}


operators = {
    0: sum,
    1: prod,
    2: min,
    3: max,
    5: lambda x: x[0] > x[1],
    6: lambda x: x[0] < x[1],
    7: lambda x: x[0] == x[1],
}


def extract_bit(b, pos):
    return (b[pos // 8] >> 7 - (pos % 8)) & 0b00000001


def extract_int(b, pos, n=3):
    o = 0
    for i in range(n):
        o += extract_bit(b, pos + i) << (n - i - 1)
    return o


def parse_packet(b, start=0, max_literal_nibbles=16, max_contained_packets=64):
    v = extract_int(b, start, n=3)
    t = extract_int(b, start+3, n=3)

    if t == 4:  # Literal packet
        nibbles = []
        start = start + 6
        complete = False
        for _ in range(max_literal_nibbles):
            nibbles.append(extract_int(b, start+1, n=4))
            start += 5
            if not extract_bit(b, start - 5):
                complete = True
                break
        if not complete:
            raise ValueError(f'Number of nibbles in literal packet exceeded limit: {max_literal_nibbles}')

        val = 0
        for i, n in enumerate(nibbles):
            val += n << (len(nibbles) - i - 1)*4

        packet = {"type": t, "version": v, "value": val}

    else:  # Operator packet
        packet = {"type": t, "version": v, "children": []}
        if extract_bit(b, start + 6):  # Number of subpackets
            n = extract_int(b, start + 7, 11)
            start = start + 18
            for _ in range(n):
                p, start = parse_packet(b, start=start, max_literal_nibbles=max_literal_nibbles,
                                        max_contained_packets=max_contained_packets)
                packet["children"].append(p)

        else:  # Number of bits read
            n = extract_int(b, start + 7, 15)
            start = start + 22
            end = start + n
            completed = False
            for _ in range(max_contained_packets):
                p, start = parse_packet(b, start=start, max_literal_nibbles=max_literal_nibbles,
                                        max_contained_packets=max_contained_packets)
                packet['children'].append(p)
                if start == end:
                    completed = True
                    break
                elif start > end:
                    raise ValueError('Packets exceeded defined in operator header')
            if not completed:
                raise ValueError(f'Max contained packets exceeded: {max_contained_packets}')
    return packet, start  # Returns packet and the pointer to where we ended


def get_version_sum(p):
    if p['type'] == 4:
        return p['version']
    else:
        return p['version'] + sum([get_version_sum(x) for x in p['children']])


def evaluate_packet(p):
    if p['type'] == 4:
        return p['value']
    else:
        cvals = [evaluate_packet(x) for x in p['children']]
        return operators[p['type']](cvals)


if __name__ == '__main__':
    for a, b in zip(range(4), [16, 12, 23, 31]):  # Some quick checks from the puzzle
        assert(get_version_sum(parse_packet(bytes.fromhex(examples[f'additional{a}']))[0]) == b)
    for a, b in zip(range(8), [3, 54, 7, 9, 1, 0, 0, 1]):  # Some quick checks from the puzzle
        assert(evaluate_packet(parse_packet(bytes.fromhex(examples[f'operators{a}']))[0]) == b)

    with open('input.txt') as f:
        p = bytes.fromhex(f.readline().strip())
    print(f'Solution 1: {get_version_sum(parse_packet(p)[0])}')
    print(f'Solution 2: {evaluate_packet(parse_packet(p)[0])}')
