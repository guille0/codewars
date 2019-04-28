# 1 kyu
# Mine Sweeper

import numpy as np
import queue
from itertools import permutations


class Minefield:
    def __init__(self, minefield, number_of_bombs):
        self.minefield, self.starting_positions = self.parse_map(minefield)
        self.n = number_of_bombs

    def solve(self):
        q = queue.Queue()
        [q.put(x) for x in self.starting_positions]
        maybe_stuck = 0

        while 1:

            if (self.n - self.bombs_found() <= 0 and len(self.question_marks()) == 0) or q.empty():

                if self.n - self.bombs_found() <= 0 and len(self.question_marks()) > 0:
                    for qm in self.question_marks():
                        qm.value = open(qm.y, qm.x)

                if self.n - self.bombs_found() == len(self.question_marks()):
                    if self.n - self.bombs_found() > 0:
                        for qm in self.question_marks():
                            qm.value = 'x'

                if self.solved():
                    return self.map_to_string()

                if maybe_stuck == 0:
                    # Put numbers adjacent to question marks in queue
                    qms = self.question_marks()
                    to_queue = set()
                    for qm in qms:
                        [to_queue.add(number) for number in qm.nearby_numbers()]
                        [q.put(x) for x in to_queue]
                    maybe_stuck = 1
                    continue
                else:
                    type, solution = self.solve_stuck()
                    if solution:
                        # print(solution)
                        # print('found a unique solution to this pickle')
                        if type == 'mines':
                            for bomb in solution:
                                bomb.value = 'x'
                        if type == 'safe':
                            for confirmed_safe in solution:
                                confirmed_safe.value = int(open(confirmed_safe.y, confirmed_safe.x))

                        # print(minefield.minefield)

                        qms = self.question_marks()
                        to_queue = set()
                        for qm in qms:
                            [to_queue.add(number) for number in qm.nearby_numbers()]
                            [q.put(x) for x in to_queue]
                        maybe_stuck = 0
                        continue

                    # print(f'stuck at ({len(minefield.question_marks())} question marks)')
                    # print(f'{n- minefield.bombs_found()} bombs remaining')
                    print(self.minefield)
                    return '?'

            box = q.get()
            unknowns = box.nearby_unknowns()
            bombs = box.nearby_bombs()

            # If all nearby bombs have been found, open everything else
            if len(unknowns) > 0 and box.value == len(bombs):
                for guy in unknowns:
                    guy.value = int(open(guy.y, guy.x))
                    q.put(guy)
                    maybe_stuck = 0

            unknowns = box.nearby_unknowns()
            bombs = box.nearby_bombs()
            # Find bombs
            if box.value == len(unknowns)+len(bombs):
                for guy in unknowns:
                    guy.value = 'x'
                    maybe_stuck = 0

    def solve_stuck(self, test_bombs=0):
        bombs_remaining = self.n - self.bombs_found()

        # Just a test parameter, ignore
        if test_bombs:
            bombs_remaining = test_bombs

        all_qms = self.question_marks()
        numbers = set()
        qms = set()
        for qm in all_qms:
            [numbers.add(number) for number in qm.nearby_numbers()]
        for number in numbers:
            [qms.add(qm) for qm in number.nearby_unknowns()]

        # Can change this if '?'s take too long
        if len(self.question_marks())*bombs_remaining > 100 and len(self.question_marks()) != len(qms):
            return None, False

        # picks 2 question marks at random to check if they could be it
        posibilities = []

        if len(all_qms) == len(qms):
            bomb_range = range(bombs_remaining, bombs_remaining+1)
        else:
            bomb_range = range(1, bombs_remaining+1)

        for bomb_amount in bomb_range:
            ps = permutations(list(qms), bomb_amount)
            posibilities += list(set([tuple(sorted(p)) for p in ps]))

        unique_solution = True
        solution = None

        possible_values = []

        for posibility in posibilities:
            # turn all cases to 'x'
            for bomb in posibility:
                bomb.value = 'x'

            # see if it's a valid solution
            for number in numbers:
                if number.value != number.n_nearby_bombs():

                    for bomb in posibility:
                        bomb.value = '?'
                    # print(f'{number.nearby_bombs()}')
                    # print(f'{number.value} at {number.y}, {number.x} wasnt satisfied')
                    break
            else:
                bad = False
                if len(posibility) == bombs_remaining:
                    for qm in self.question_marks():
                        if qm.n_nearby_bombs() == 0:
                            # print(f'empty spot at {qm.y}, {qm.x}')
                            bad = True

                else:
                    for qm in qms:
                        if qm.value != 'x':
                            if qm.n_nearby_bombs() == 0:
                                # print(f'empty spot at {qm.y}, {qm.x}')
                                bad = True

                if bad is False:
                    possible_values.append(posibility)
                    if solution:
                        for bomb in posibility:
                            bomb.value = '?'
                        unique_solution = False
                    if len(self.question_marks()) >= bombs_remaining:
                        solution = posibility

                for bomb in posibility:
                    bomb.value = '?'

        # PRINT POSSIBLE_VALUES:
        # print(possible_values)
        # print('Possible values at:')
        # for ps in possible_values:
        #     print(ps)
        #     for dimension in ps:
        #         print(f'{dimension.y}, {dimension.x}')
        # print('we see they all agree on 1,1, so its gotta be correct')
        # END PRINT POSSIBLE_VALUES
        # GET VALUE IN COMMON FROM POSSIBLE_VALUES
        cpv = common_possible_values(possible_values)
        if cpv == []:
            safe_cases = unseen_possible_values(possible_values, qms)
        # if we don't have a solution, we return cpv
        # print('cpv', cpv)
        # print(self.minefield)
        if solution and unique_solution is True:
            return ('mines', solution)
        elif cpv != []:
            return ('mines', cpv)
        else:
            return ('safe', safe_cases)

    def parse_map(self, gamefield):
        self.bombs_remaining = 0
        starting_positions = []
        minefield = np.array([x.split(' ') for x in gamefield.split('\n')],
                             dtype=np.object)

        for y, row in enumerate(minefield):
            for x, value in enumerate(row):
                minefield[y, x] = Node(y, x, value)
                if value != '?':
                    self.bombs_remaining += 1
                    starting_positions.append(minefield[y, x])

        for row in minefield:
            for node in row:
                node.get_paths(minefield)

        return minefield, starting_positions

    def map_to_string(self):
        rows = []
        for row in self.minefield:
            rows.append(' '.join([str(node.value) for node in row]))
        return '\n'.join(rows)

    def solved(self):
        for row in self.minefield:
            for node in row:
                if node.value == '?':
                    return False
        else:
            return True

    def question_marks(self):
        qs = []
        for row in self.minefield:
            for node in row:
                if node.value == '?':
                    qs.append(node)
        return qs

    def bombs_found(self):
        bs = []
        for row in self.minefield:
            for node in row:
                if node.value == 'x':
                    bs.append(node)
        return len(bs)


class Node:
    def __init__(self, y, x, value):
        self.y = y
        self.x = x
        # Turns numbers into ints and leaves question marks
        self.value = value if value == '?' or value == 'x' else int(value)

    def get_paths(self, minefield):
        self.paths = []
        height, width = minefield.shape

        if self.y > 0 and self.x > 0:
            self.paths.append(minefield[self.y-1, self.x-1])
        if self.y < height-1 and self.x > 0:
            self.paths.append(minefield[self.y+1, self.x-1])
        if self.x < width-1 and self.y > 0:
            self.paths.append(minefield[self.y-1, self.x+1])
        if self.x < width-1 and self.y < height-1:
            self.paths.append(minefield[self.y+1, self.x+1])

        if self.y > 0:
            self.paths.append(minefield[self.y-1, self.x])
        if self.y < height-1:
            self.paths.append(minefield[self.y+1, self.x])
        if self.x > 0:
            self.paths.append(minefield[self.y, self.x-1])
        if self.x < width-1:
            self.paths.append(minefield[self.y, self.x+1])

    def nearby_unknowns(self):
        return [box for box in self.paths if box.value == '?']

    def nearby_bombs(self):
        return [box for box in self.paths if box.value == 'x']

    def nearby_numbers(self):
        return [box for box in self.paths if isinstance(box.value, int)]

    def n_nearby_unknowns(self):
        return sum(1 for box in self.paths if box.value == '?')

    def n_nearby_bombs(self):
        return sum(1 for box in self.paths if box.value == 'x')

    def n_nearby_numbers(self):
        return sum(1 for box in self.paths if isinstance(box.value, int))

    def __repr__(self):
        return str(self.value)

    def __gt__(self, other):
        return id(self) > id(other)


def common_possible_values(possible_values):

    values = set()
    for guy in possible_values:
        for ps in guy:
            values.add(ps)

    values = list(values)
    common_values = []

    for value in values:
        for every_one in possible_values:
            if value not in every_one:
                break
        else:
            common_values.append(value)
    
    return common_values


def unseen_possible_values(possible_values, unknowns):
    qms = list(unknowns)
    values = set()
    for guy in possible_values:
        for ps in guy:
            values.add(ps)

    values = list(values)
    unseen_values = []
    # print(values)
    # print(qms)

    for qm in qms:
        if qm not in values:
            unseen_values.append(qm)

    return unseen_values


def solve_mine(mapa, n):
    minefield = Minefield(mapa, n)
    return minefield.solve()

# TESTING


s = '''
1 ? ?
2 ? ?
x 2 1
'''.strip()
# this one has 3 bombs V
s = '''
1 2 x 1
? ? 2 1
? ? 2 1
? ? 2 x
? ? ? 2
? ? ? 1
'''.strip()
s = '''
x 2 1
2 ? ?
1 ? ?
2 ? ?
2 ? ?
2 ? ?
'''.strip()
s = '''
1 2 2 1 0 0
2 x x 2 1 1
2 3 ? ? ? ?
1 1 ? ? ? ?
'''.strip()
s = '''
x 2 x 2 x 1 1 x 2 1
1 2 1 2 1 1 1 2 ? ?
0 0 1 1 1 0 0 1 ? ?
0 0 1 x 1 1 1 2 ? ?
0 0 1 1 1 1 x 2 ? ?
0 0 0 0 0 1 1 2 ? ?
'''.strip()
# s = '''
# 1 ? 1 0 0 1 ? 1
# 2 ? 2 2 2 3 ? 2
# x 3 ? ? ? ? ? 1
# 1 2 ? ? ? ? ? 2
# 0 1 ? ? ? ? ? 1
# '''.strip()
s = '''
x 1 ?
? ? ?
? ? ?
'''.strip()

# Testing for advanced situations:

# minefield = Minefield(s)
# test = stuck_solver(minefield, 2, test=True)
# if test[1]:
#     if test[0] == 'safe':
#         print(f'Found safe square(s) at:')
#     if test[0] == 'mines':
#         print(f'Found mine(s) at:')
#     [print(f'({case.y}, {case.x})') for case in test[1]]
# else:
#     print('Couldn\'t solve this situation.')
