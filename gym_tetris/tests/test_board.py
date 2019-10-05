import unittest

from gym_tetris.board import Board


class BoardTest(unittest.TestCase):
    def setUp(self):
        self.board = Board(10, 20)
        board_blueprint = [
            "          ",
            "          ",
            "          ",
            "          ",
            "          ",
            "          ",
            "          ",
            "   ##     ",
            "   ##    #",
            "   ##    #",
            "   ###   #",
            "# ##### ##",
            "# ### # ##",
            "# ########",
            "# ####### ",
            "#### #####",
            " ####   ##",
            " #########",
            " #########",
            " #########",
        ]
        self.board.pieces_table = [[1 if x == "#" else 0 for x in y] for y in board_blueprint]

    def test_has_correct_holes(self):
        self.assertEqual(self.board.get_hole_count(), 10)

    def test_has_correct_row_transitions(self):
        self.assertEqual(self.board.get_row_transitions(), 44)

    def test_has_correct_column_transitions(self):
        self.assertEqual(self.board.get_column_transitions(), 14)

    def test_has_correct_cumulative_wells(self):
        self.assertEqual(self.board.get_cumulative_wells(), 6)

    def test_has_correct_bumpiness(self):
        self.assertEqual(self.board.get_bumpiness(), 23)

    def test_has_correct_aggregate_height(self):
        self.assertEqual(self.board.get_aggregate_height(), 96)

    def test_has_correct_rows_cleared(self):
        self.assertEqual(len(self.board.get_cleared_rows()), 0)
