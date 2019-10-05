from gym_tetris.board import Board


class Game:
    def __init__(self, board: Board):
        self.board = board
        self.level = 0
        self.score = 0
        self.lines = 0
        self.drop_time = self.get_drop_speed()

    def get_drop_speed(self):
        """Returns how many frames it takes for the piece to drop a cell."""
        return round(max(1.0, 8 - self.level / 2))

    def get_level_up_lines(self):
        """Returns how many lines it takes to level up."""
        return 10 * (self.level + 1)

    def get_score(self, row_count):
        """Returns the score the player receives by x rows."""
        if row_count == 1:
            return 40 * (self.level + 1)
        elif row_count == 2:
            return 100 * (self.level + 1)
        elif row_count == 3:
            return 300 * (self.level + 1)
        elif row_count == 4:
            return 1200 * (self.level + 1)
        return 0

    def _complete_rows(self, rows):
        """Remove the rows on the board and optionally adds score/level"""
        for y in rows:
            self.board.remove_row(y)
        self.score += self.get_score(len(rows))
        self.lines += len(rows)
        if self.lines >= self.get_level_up_lines():
            self.level += 1

    def tick(self):
        """Remove the rows on the board and optionally adds score/level"""
        rows = []

        if self.board.is_game_over():
            return rows

        self.drop_time -= 1
        if self.drop_time <= 0:
            self.board.drop_piece()
            self.drop_time = self.get_drop_speed()

        if self.board.piece is None:
            self.board.create_piece()
            rows = self.board.get_cleared_rows()
            if rows:
                self._complete_rows(rows)

        return rows
