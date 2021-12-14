if __name__ == '__main__':
    # Read the puzzle input
    with open('input.txt') as f:
        pin = f.readlines()

    # Make a table of commands
    commands = {
        'forward': {'scale': 1, 'axis': 'horizontal'},
        'down': {'scale': 1, 'axis': 'depth'},
        'up': {'scale': -1, 'axis': 'depth'},
    }

    # Apply commands
    position = {'depth': 0, 'horizontal': 0}
    for cmd in pin:
        a, b = cmd.strip().split()
        position[commands[a]['axis']] += commands[a]['scale'] * int(b)
    print(f"Puzzle 1 solution: {position['depth']*position['horizontal']}")

    # Make the new table of commands
    commands = {
        'forward': {'scale': 1, 'axis': 'horizontal', 'aim': 1},
        'down': {'scale': 1, 'axis': 'aim', 'aim': 0},
        'up': {'scale': -1, 'axis': 'aim', 'aim': 0},
    }

    # Apply commands
    position = {'depth': 0, 'horizontal': 0, 'aim': 0}
    for cmd in pin:
        a, b = cmd.strip().split()
        position[commands[a]['axis']] += commands[a]['scale'] * int(b)
        position['depth'] += position['aim'] * commands[a]['aim'] * int(b)
    print(f"Puzzle 2 solution: {position['depth']*position['horizontal']}")
