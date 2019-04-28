# 2 kyu
# Break the pieces

# +------+-----+
# |      |     |
# |      +-----+
# |      |     |
# +------+-----+
# |      |     |
# |      |     |
# +------+-----+

# Turn into array of objects Case.
# Walls, borders and spaces all get turned to Case
# each Case has 8 adjacents (or less)

# Create a list of Cases that are adjacent to walls
# Start with the first one, find all the other borders and white cells it's connected to
# Pop them all from the list and create an array from them that gives them borders
# To do that just make the array +2 the height and +2 the width of the other one,
# put in the borders and whites starting at 1,1
# Change whatever is left to walls (+, / or -)

# look for the next case in the list
# (it will be from a different shape, since all the other ones got popped)

import numpy as np
import queue


class Field:
    def __init__(self, field):
        self.original = field
        tolist = field.split('\n')
        maxlen = len(max(tolist, key=len))
        for i, line in enumerate(tolist):
            if len(line) < maxlen:
                tolist[i] += ' '*(maxlen-len(line))

        self.field = np.array([list(row) for row in tolist], dtype=np.object, ndmin=2)

        self.value_field = np.copy(self.field)
        self.height, self.width = self.value_field.shape

        for i, row in enumerate(self.field):
            for j, value in enumerate(row):
                self.field[i, j] = Case(value)
                self.field[i, j].y, self.field[i, j].x = i, j
        for row in self.field:
            for case in row:
                case.field = self.field
                case.value_field = self.value_field
                case.parent = self
                case.get_paths()
        self.outside = self.get_outside()

    def __repr__(self):
        return self.field.__str__()

    def get_walls(self):
        walls = []
        for row in self.field:
            for node in row:
                if isinstance(node.value, list):
                    raise Exception(self.original, self.field)
                if node.value in '+-|':
                    walls.append(node)
        return walls

    def get_borders(self, walls):
        borders = set()
        for wall in walls:
            [borders.add(path) for path in wall.paths if path.value == ' ' and path.is_inside]
        return borders

    def get_outside(self):
        outside = set()
        bordes = set()
        [bordes.add(x) for x in self.field[:, 0].ravel()]
        [bordes.add(x) for x in self.field[:, -1].ravel()]
        [bordes.add(x) for x in self.field[0, :].ravel()]
        [bordes.add(x) for x in self.field[-1, :].ravel()]

        q = queue.Queue()
        [q.put(point) for point in bordes if point.value == ' ']

        while q.qsize() > 0:
            guy = q.get()
            for path in guy.paths:
                if path.value == ' ' and path.solved is False:
                    q.put(path)
                    path.solved = True
                    outside.add(path)

        return outside

    # def get_all_whitespace(self):
    #     white = []
    #     for row in self.field:
    #         for node in row:
    #             if node.value == ' ':
    #                 white.append(node)
    #     return white

    def make_square(self, point, borders):
        # Given a border that's part of the square, it builds it.
        border = set()
        whitespace = set()
        q = queue.Queue()
        q.put(point)

        while q.qsize() > 0:
            guy = q.get()
            if guy.value == ' ' and guy.solved is False:
                if guy in borders:
                    border.add(guy)
                    whitespace.add(guy)
                    guy.solved = True
            for path in guy.paths:
                if path.value == ' ' and path.solved is False:
                    q.put(path)
                    path.solved = True
                    whitespace.add(path)
                    if path in borders:
                        border.add(path)

        # border = all borders in the square
        min_x = min(border, key=lambda guy: guy.x).x
        max_x = max(border, key=lambda guy: guy.x).x
        width = max_x-min_x+1
        min_y = min(border, key=lambda guy: guy.y).y
        max_y = max(border, key=lambda guy: guy.y).y
        height = max_y-min_y+1
        # bottom_right_corner = max(border)

        # print(f'Height: {height}')
        # print(f'Width: {width}')
        # print(bottom_right_corner.y, bottom_right_corner.x)

        square = np.zeros((height+2, width+2), dtype=str)

        # Borders
        for guy in border:
            for path in guy.paths:
                if path not in whitespace:
                    # self.value_field[path.y, path.x]
                    
                    square[path.y-min_y+1, path.x-min_x+1] = 'x'

        # Space inside the square
        for guy in whitespace:
            square[guy.y-min_y+1, guy.x-min_x+1] = ' '
        
        # Space outside the square
        square[square == ''] = ' '

        for guy in border:
            for path in guy.paths:
                if path not in whitespace:
                    # print(path)
                    y, x = path.y-min_y+1, path.x-min_x+1
                    direction = 'n'
                    if x < square.shape[1]-1 and square[y, x+1] != ' ':
                        direction = '-'
                    if x > 0 and square[y, x-1] != ' ':
                        direction = '-'

                    if y < square.shape[0]-1 and square[y+1, x] != ' ':
                        direction = '+' if direction == '-' else '|'
                    if y > 0 and square[y-1, x] != ' ':
                        direction = '+' if direction == '-' else '|'

                    square[y, x] = direction

        # print(square)

        # Get all borders connected to the first one
        # Mark all borders as solved
        # Build a list of all the borders
        # Then get the max and the min (corners)
        # Then build an array with dimensions of that square +2
        # Then place the corners inside it in the same disposition
        # Done (no need to fill in the squares, though maybe needed for 1kyu)
        return square

    def break_apart(self):
        walls = self.get_walls()
        borders = self.get_borders(walls)
        solution = []
        while 'solving':
            unseen_squares = [border for border in borders if border.solved is False]
            if not unseen_squares:
                break

            new_square = unseen_squares[0]
            solution.append(self.make_square(new_square, borders))

        print(f'found {len(solution)} squares')

        final = []
        for square in solution:
            guy = []
            for row in square:
                guy.append(''.join(row).rstrip())
            final.append('\n'.join(guy))

        return final


class Case:
    def __init__(self, value):
        self.value = value
        self.solved = False
        self.field = None
        self.paths = []
    
    def __repr__(self):
        return str(self.value)

    def __gt__(self, other):
        return self.x+self.y > other.x+other.y
    
    def __lt__(self, other):
        return self.x+self.y < other.x+other.y

    def get_paths(self):
        height, width = self.field.shape

        if self.y > 0 and self.x > 0:
            self.paths.append(self.field[self.y-1, self.x-1])
        if self.y < height-1 and self.x > 0:
            self.paths.append(self.field[self.y+1, self.x-1])
        if self.x < width-1 and self.y > 0:
            self.paths.append(self.field[self.y-1, self.x+1])
        if self.x < width-1 and self.y < height-1:
            self.paths.append(self.field[self.y+1, self.x+1])

        if self.y > 0:
            self.paths.append(self.field[self.y-1, self.x])
        if self.y < height-1:
            self.paths.append(self.field[self.y+1, self.x])
        if self.x > 0:
            self.paths.append(self.field[self.y, self.x-1])
        if self.x < width-1:
            self.paths.append(self.field[self.y, self.x+1])

    @property
    def is_inside(self):
        return False if self in self.parent.outside else True


def break_pieces(shape):
    field = Field(shape)
    print(field)
    squares = field.break_apart()
    [print(square) for square in squares]
    return squares

# TESTING


shape = '\n'.join(["+------------+",
                   "|            |",
                   "|            |",
                   "|            |",
                   "+-----+-+----+",
                   "|     | |    |",
                   "|     +-+    |",
                   "+-----+-+----+"])
break_pieces(shape)