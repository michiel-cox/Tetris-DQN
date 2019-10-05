import random


def get_random_bag():
    """Returns a bag with unique pieces. (Bag randomizer)"""
    random_shapes = list(SHAPES)
    random.shuffle(random_shapes)
    return [Piece(0, 0, shape) for shape in random_shapes]


class Shape:
    def __init__(self, code, blueprints):
        self.code = code
        self.rotations = len(blueprints)
        self.blueprints = blueprints
        self.shape_coords = []
        self.width = len(blueprints[0])
        self.height = len(blueprints)
        for rotation in range(self.rotations):
            self.shape_coords.append(list(self._create_shape_coords(rotation)))

    def _get_blueprint(self, rotation):
        """Returns a list of strings that defines how the shape looks like."""
        return self.blueprints[rotation % self.rotations]

    def get_shape_coords(self, rotation):
        """Returns a list of relative coordinates that make up the shape."""
        return self.shape_coords[rotation % self.rotations]

    def _create_shape_coords(self, rotation):
        blueprint = self._get_blueprint(rotation)
        width = len(blueprint[0])
        height = len(blueprint)
        for offset_y in range(height):
            for offset_x in range(width):
                if blueprint[offset_y][offset_x] != ' ':
                    yield offset_y, offset_x


SHAPE_I = Shape(1, [[
    '    ',
    '####',
    '    ',
    '    ',
], [
    '  # ',
    '  # ',
    '  # ',
    '  # ',
]])

SHAPE_O = Shape(2, [[
    '##',
    '##',
]])

SHAPE_T = Shape(3, [[
    '   ',
    '###',
    ' # ',
], [
    ' # ',
    '## ',
    ' # ',
], [
    ' # ',
    '###',
    '   ',
], [
    ' # ',
    ' ##',
    ' # ',
]])

SHAPE_S = Shape(4, [[
    '   ',
    ' ##',
    '## ',
], [
    ' # ',
    ' ##',
    '  #',
]])

SHAPE_Z = Shape(5, [[
    '   ',
    '## ',
    ' ##',
], [
    '  #',
    ' ##',
    ' # ',
]])

SHAPE_J = Shape(6, [[
    '   ',
    '###',
    '  #',
], [
    ' # ',
    ' # ',
    '## ',
], [
    '#  ',
    '###',
    '   ',
], [
    ' ##',
    ' # ',
    ' # ',
]])

SHAPE_L = Shape(7, [[
    '   ',
    '###',
    '#  ',
], [
    '## ',
    ' # ',
    ' # ',
], [
    '  #',
    '###',
    '   ',
], [
    ' # ',
    ' # ',
    ' ##',
]])

SHAPES = [SHAPE_I, SHAPE_O, SHAPE_T, SHAPE_S, SHAPE_Z, SHAPE_J, SHAPE_L]


class Piece:

    def __init__(self, x, y, shape: Shape, rotation=0):
        self.x = x
        self.y = y
        self.shape = shape
        self.rotation = rotation
        self.shape_coords = None

    def rotate(self, dir_rotate):
        """Rotate the piece."""
        self.rotation += dir_rotate
        self.shape_coords = None

    def move(self, x, y):
        """Move the piece."""
        self.x += x
        self.y += y
        self.shape_coords = None

    def get_shape_coords(self):
        """Returns a list of coordinates that the piece occupies."""
        if self.shape_coords is None:
            begin_x = self.x - round(self.shape.width / 2)
            begin_y = self.y
            shape_coords = self.shape.get_shape_coords(self.rotation)
            self.shape_coords = [(begin_x + offset_x, begin_y + offset_y) for offset_y, offset_x in shape_coords]
        return self.shape_coords


class Board:

    def __init__(self, columns, rows):
        self.columns = columns
        self.rows = rows
        self.pieces_table = [[0 for i in range(columns)] for j in range(rows)]
        self.piece = None
        self.piece_next = None
        self.piece_holding = None
        self.piece_last = None
        self.can_hold = True
        self.bag = get_random_bag()
        self.create_piece()

    def create_piece(self):
        """The next piece becomes the current piece and spawn it on the board."""
        if self.piece_next is not None:
            self.piece = self.piece_next
        else:
            self.piece = self.bag.pop()

        self.piece.move(int(self.columns / 2), 0)
        self.piece_next = self.bag.pop()
        self.can_hold = True

        if not self.bag:
            self.bag = get_random_bag()

    def _place_piece(self):
        """Solidify the current piece onto the board and returns success."""
        coords = self.piece.get_shape_coords()

        if any(x < 0 or x >= self.columns or y < 0 or y >= self.rows or self.pieces_table[y][x] != 0 for x, y in
               coords):
            return False

        for x, y in coords:
            self.pieces_table[y][x] = self.piece.shape.code

        self.piece_last = self.piece
        self.piece = None
        return True

    def can_move_piece(self, dir_x, dir_y):
        """Returns true if the piece does not intersect with a non-empty cell when moved."""
        for x, y in self.piece.get_shape_coords():
            next_x = x + dir_x
            next_y = y + dir_y
            if next_x < 0 or next_x >= self.columns or next_y < 0 or next_y >= self.rows:
                return False
            if self.pieces_table[next_y][next_x] != 0:
                return False
        return True

    def move_piece(self, dir_x):
        """Move the piece in a direction and returns success."""
        if self.piece is None:
            return False

        if not self.can_move_piece(dir_x, 0):
            return False

        self.piece.move(dir_x, 0)
        return True

    def drop_piece(self):
        """Drop the piece by one cell and returns success."""
        if self.piece is None:
            return False
        if not self.can_move_piece(0, 1):
            self._place_piece()
            return True
        self.piece.move(0, 1)
        return False

    def rotate_piece(self, dir_rotation):
        """Rotate the current piece and returns success."""
        if self.piece is None:
            return False

        self.piece.rotate(dir_rotation)

        if not self.can_move_piece(0, 0):
            if not self.move_piece(-1) and not self.move_piece(1):
                self.piece.rotate(-dir_rotation)
                return False

        return True

    def is_game_over(self):
        """Returns if the current piece is able to move."""
        return self.piece is not None and not self.can_move_piece(0, 0)

    def is_row(self, y):
        """Returns if the row is a fully filled one."""
        return 0 not in self.pieces_table[y]

    def remove_row(self, y):
        """Removes a row from the board."""
        removed_row = self.pieces_table.pop(y)
        self.pieces_table.insert(0, [0 for i in range(self.columns)])
        return removed_row

    def insert_row(self, y, row):
        """Inserts a row into the board."""
        self.pieces_table.pop(0)
        self.pieces_table.insert(y, row)

    def move_and_drop(self, x, rotation):
        """Move the piece and drop it as far down as possible and returns success."""
        if self.piece is None:
            return False

        self.piece.rotate(rotation)

        return self.can_move_piece(0, 0) and self.move_piece(-self.piece.x + x) and self.drop_piece_fully()

    def drop_piece_fully(self):
        """Drops the current piece as far down as possible and returns success."""
        if self.piece is None:
            return False

        while self.can_move_piece(0, 1):
            self.piece.move(0, 1)

        return self._place_piece()

    def hold_piece(self):
        """Switches the piece held with the current and returns success."""
        if self.piece is None or not self.can_hold:
            return False
        piece_current = self.piece
        self.piece = self.piece_holding
        self.piece_holding = piece_current
        self.piece_holding.move(-self.piece_holding.x, -self.piece_holding.y)

        if self.piece is None:
            self.create_piece()
        else:
            self.piece.move(int(self.columns / 2), 2)

        self.can_hold = False
        return True

    def get_possible_states(self):
        """Returns all possible states of the board with the corresponding action tuple.

        Tries out every possible way to turn and move the current piece.
        The action taken and the state of the board is combined into a tuple and added to the returning list
        After every try the board is reset to original state.

        :rtype: A list with a tuple of (action, state).
        action = (column, rotation)
        state = return value of `get_info`
        """
        if self.piece is None:
            return []

        states = []

        last_piece = self.piece_last

        for rotation in range(self.piece.shape.rotations):
            for column in range(self.columns + 1):
                piece = Piece(self.piece.x, self.piece.y, self.piece.shape, self.piece.rotation)

                # Execute
                if self.move_and_drop(column, rotation):
                    rows_cleared = self.get_cleared_rows()
                    removed_rows = []
                    for y in rows_cleared:
                        removed_rows.append((y, self.remove_row(y)))

                    # Save
                    states.append(((column, rotation), self.get_info(rows_cleared)))

                    # Reset
                    for y, row in reversed(removed_rows):
                        self.insert_row(y, row)

                    for x, y in self.piece_last.get_shape_coords():
                        self.pieces_table[y][x] = 0

                self.piece = piece
                self.piece_last = last_piece
        return states

    def get_info(self, rows_cleared):
        """Returns the state of the board using statistics.

         0: Rows cleared
         1: Bumpiness
         2: Holes
         3: Landing height
         4: Row transitions
         5: Column transitions
         6: Cumulative wells
         7: Eroded piece cells
         8: Aggregate height

        :rtype: Integer array
        """
        if self.piece_last is not None:
            last_piece_coords = self.piece_last.get_shape_coords()
            eroded_piece_cells = len(rows_cleared) * sum(y in rows_cleared for x, y in last_piece_coords)
            landing_height = 0 if self.piece_last is None else 1 + self.rows - max(y for x, y in last_piece_coords)
        else:
            eroded_piece_cells = 0
            landing_height = 0

        return [
            len(rows_cleared),
            self.get_bumpiness(),
            self.get_hole_count(),
            landing_height,
            self.get_row_transitions(),
            self.get_column_transitions(),
            self.get_cumulative_wells(),
            eroded_piece_cells,
            self.get_aggregate_height(),
        ]

    def get_cleared_rows(self):
        """Returns the the amount of rows cleared."""
        return list(filter(lambda y: self.is_row(y), range(self.rows)))

    def get_row_transitions(self):
        """Returns the number of horizontal cell transitions."""
        total = 0
        for y in range(self.rows):
            row_count = 0
            last_empty = False
            for x in range(self.columns):
                empty = self.pieces_table[y][x] == 0
                if last_empty != empty:
                    row_count += 1
                    last_empty = empty

            if last_empty:
                row_count += 1

            if last_empty and row_count == 2:
                continue

            total += row_count
        return total

    def get_column_transitions(self):
        """Returns the number of vertical cell transitions."""
        total = 0
        for x in range(self.columns):
            column_count = 0
            last_empty = False
            for y in reversed(range(self.rows)):
                empty = self.pieces_table[y][x] == 0
                if last_empty and not empty:
                    column_count += 2
                last_empty = empty

            if last_empty and column_count == 1:
                continue

            total += column_count
        return total

    def get_bumpiness(self):
        """Returns the total of the difference between the height of each column."""
        bumpiness = 0
        last_height = -1
        for x in range(self.columns):
            current_height = 0
            for y in range(self.rows):
                if self.pieces_table[y][x] != 0:
                    current_height = self.rows - y
                    break
            if last_height != -1:
                bumpiness += abs(last_height - current_height)
            last_height = current_height
        return bumpiness

    def get_cumulative_wells(self):
        """Returns the sum of all wells."""
        wells = [0 for i in range(self.columns)]
        for y, row in enumerate(self.pieces_table):
            left_empty = True
            for x, code in enumerate(row):
                if code == 0:
                    well = False
                    right_empty = self.columns > x + 1 >= 0 and self.pieces_table[y][x + 1] == 0
                    if left_empty or right_empty:
                        well = True
                    wells[x] = 0 if well else wells[x] + 1
                    left_empty = True
                else:
                    left_empty = False
        return sum(wells)

    def get_aggregate_height(self):
        """Returns the sum of the heights of each column."""
        aggregate_height = 0
        for x in range(self.columns):
            for y in range(self.rows):
                if self.pieces_table[y][x] != 0:
                    aggregate_height += self.rows - y
                    break
        return aggregate_height

    def get_hole_count(self):
        """returns the number of empty cells covered by a full cell."""
        hole_count = 0
        for x in range(self.columns):
            below = False
            for y in range(self.rows):
                empty = self.pieces_table[y][x] == 0
                if not below and not empty:
                    below = True
                elif below and empty:
                    hole_count += 1

        return hole_count
