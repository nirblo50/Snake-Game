from game_parameters import CELL_TYPE
from typing import List


class Bomb:
    """
    Represents a bomb in the game.
    The snake should avoid the bomb and its blast.
    """

    def __init__(self, cell: CELL_TYPE, turns_until_boom: int,
                 max_radius: int):
        """
        :param cell: the location of the bomb (row, col)
        :param turns_until_boom: number of turns until the bomb will go off
        :param max_radius: the maximum radius the bomb's blast can go up to
        """
        self.cell = cell
        self.max_radius = max_radius
        self.turns_until_boom = turns_until_boom
        # Blast radius in the current round (0 <= current_radius <= max_radius)
        self.current_radius: int = 0

    def get_blast_cells(self) -> List[CELL_TYPE]:
        """
        :return: list of the cells which the blast is occurring in, if there is
                 no blast - will return an empty list
        """
        if self.turns_until_boom > 0:
            return []

        x, y = self.cell
        r = self.current_radius
        blast_cells = [(i, j) for j in range(y - r, y + r + 1)
                       for i in range(x - r, x + r + 1)
                       if abs(x - i) + abs(y - j) == r]
        return blast_cells

    def get_bomb_cells(self) -> List[CELL_TYPE]:
        """
        :return: a list of the location of the bomb before it went off or empty
                 list if it went off already
        """
        return [self.cell] if self.turns_until_boom > 0 else []

    def get_all_cells(self) -> List[CELL_TYPE]:
        """
        :return: list of all the cells with a bomb (both bomb location and bomb
                 blast cells)
        """
        return self.get_blast_cells() + self.get_bomb_cells()

    def is_done(self) -> bool:
        """
        :return: True if the bomb blast and done, and the bomb should be
                 removed, False otherwise.
        """
        return self.current_radius >= self.max_radius

    def advance(self) -> None:
        """
        Update the bomb to a new round:
        1. if the bomb has yet to explode, the bomb's timer (turns_until_boom)
         'ticks' by one.
        2. if the bomb has already exploded - expand the current blast radius
           by one.
        """
        if self.turns_until_boom > 0:
            self.turns_until_boom -= 1
        else:
            self.current_radius += 1
