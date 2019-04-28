# 2 kyu
# Insane Coloured Triangles

good_numbers = [1, 4, 10, 28, 82, 244, 730, 2188, 6562, 19684, 59050, 177148]

colors = set('RGB')


def simple_solve(guys):
    while len(guys) > 1:
        guys = [a if a == b else (colors-{a, b}).pop() for a, b in zip(guys, guys[1:])]
    return guys[0]


def closest_good_number(number, good_numbers):
    closest = sorted(good_numbers, key=lambda x: abs(x - number))
    for value in closest:
        if value <= number:
            return value


def sides_until_good(guys):
    # Solves the sides of the pyramid until we get to a number from which we can simplify
    if len(guys) < 4:
        return simple_solve(guys)

    good_number = closest_good_number(len(guys), good_numbers)
    size = len(guys) - good_number + 1

    left = guys[:size]
    right = guys[-size:]

    # recurse to find smallest guy in left and right

    a = sides_until_good(left)
    b = sides_until_good(right)
    final = simple_solve((a, b))

    return final


def triangle(input):
    guy = sides_until_good(input)
    return guy