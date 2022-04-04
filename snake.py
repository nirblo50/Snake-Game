from game_parameters import CELL_TYPE
from typing import List, Optional, Dict

# Direction names
LEFT = "Left"
RIGHT = "Right"
UP = "Up"
DOWN = "Down"

# Maps each direction to other directions it can be changed to
LEGAL_DIRECTIONS: Dict[str, List[str]] = {
    LEFT: [UP, DOWN],
    RIGHT: [UP, DOWN],
    DOWN: [LEFT, RIGHT],
    UP: [LEFT, RIGHT],
}

# The vectors of advancing in each direction
DIRECTION_VECTORS: Dict[str, CELL_TYPE] = {
    LEFT: (-1, 0),
    RIGHT: (1, 0),
    UP: (0, 1),
    DOWN: (0, -1),
}


class Snake:
    """
    Represents a snake.
    The snake is the character controlled by the player.
    """

    def __init__(self, cells: List[CELL_TYPE], direction: str):
        """
        :param cells: a list of cells currently occupied by the snake, ordered
                      from tail to head.
        :param direction: the direction which the snake is facing
                          (one of UP, DOWN, LEFT, RIGHT)
        """
        self.__cells = cells
        self._direction = direction
        # Number of turns which the snake needs to 'grow' by one
        self._grow_turns: int = 0

    @property
    def cells(self) -> List[CELL_TYPE]:
        """
        :return: a list of cells currently occupied by the snake, ordered
                 from tail to head.
        """
        return self.__cells

    @property
    def head(self) -> CELL_TYPE:
        """
        :return: the cell which contain the head of the snake
        """
        return self.cells[-1]

    def change_direction(self, direction: Optional[str]) -> None:
        """
        Change the direction that the snake is facing but only if it's a legal
        direction (e.g., if the snake is currently facing UP, then it can only
        be changed to LEFT or RIGHT).

        :param direction: the new wanted direction
        """
        if direction in LEGAL_DIRECTIONS[self._direction]:
            self._direction = direction

    def shorten_tail(self) -> None:
        """
        Remove old tail, unless the snake is currently growing.
        """
        if self._grow_turns > 0:
            self._grow_turns -= 1
        else:
            self.cells.pop(0)

    def get_new_head(self) -> CELL_TYPE:
        """
        :return: the snake's next head location: Tuple[int, int] if the snake
                 will advance in its direction
        """
        direction_vector = DIRECTION_VECTORS[self._direction]
        return (self.head[0] + direction_vector[0],
                self.head[1] + direction_vector[1])

    def advance_head(self) -> None:
        """
        Advance the snake 1 step in the current direction.
        """
        # Add new head
        self.cells.append(self.get_new_head())

    def grow(self, amount: int) -> None:
        """
        Makes the snake grow a given amount of cells (grow one cell each round
        until it reaches the amount that was given).

        :param amount: the amount of cells the snake should grow
        """
        self._grow_turns += amount
