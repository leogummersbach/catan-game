def standard_placements():
    out = []
    for i in range(-1, 2):
        out.append((-2, i))
    for j in range(-1, 2):
        for i in range(-2, 3):
            out.append((j, i))
    out.append((2, 0))
    return out


def standard_harbor_placements():
    return [(3, 0, 2), (2, 2, 1), (0, 3, 1), (-2, 3, 0), (-3, 1, 5), (-3, -1, 5), (-2, -3, 4), (0, -3, 3), (2, -2, 3)]
