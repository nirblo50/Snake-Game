from typing import Tuple, List, Optional
import game_parameters
from game_display import GameDisplay
from snake import Snake, UP
from bomb import Bomb
from apple import Apple


# Types
CELL_TYPE = Tuple[int, int]
DRAW_TYPE = List[Tuple[int, int, str]]  # [(row, col, color)]

# Game constants
NUMBER_OF_APPLES = 3
INITIAL_SNAKE_CELLS = [(10, 8), (10, 9), (10, 10)]
APPLE_GROW_SIZE = 3

# Colors that can be drawn
BLACK = "black"
RED = "red"
GREEN = "green"
ORANGE = "orange"

INITIAL_SNAKE_DIRECTION = UP


class GameBoard:
    """
    Represents the snake game.
    """

    def __init__(self) -> None:
        # The game's snake (player character).
        self.snake = Snake(INITIAL_SNAKE_CELLS[:], INITIAL_SNAKE_DIRECTION)
        # The game's bomb (an obstacle).
        # Apples that currently exist in the game (player's target).
        self.apples: List[Apple] = []
        self.bomb: Bomb = self.__randomize_bomb()
        self.__generate_apples()

        # The players current score.
        self.score: int = 0
        # Whether the game should be over or not.
        self.should_quit: bool = False
        # True if there's a new score that wasn't displayed yet.
        self.new_score_available = True

    def execute_round(self, key_clicked: Optional[str]) -> None:
        """
        Execute a single round of the game.
        1. Update the snake's direction to the given direction (if change is
           needed)
        2. Move the snake
        3. Update the bomb
        4. Make sure there are enough apples
        5. Mark if the game should be over.

        :param key_clicked: The key that was clicked by the user to change the
                            direction of the snake (None if no change needed).
        """
        self.snake.change_direction(key_clicked)
        self.__update_snake_head()
        if self.should_quit:
            return

        self.__update_bomb()
        if self.should_quit:
            return

        self.__generate_apples()
        if self.should_quit:
            return

    def draw_board(self) -> DRAW_TYPE:
        """
        :return: current drawing of the board - a list of tuples, each
                 containing parameters for draw_cell.
        """
        drawing: DRAW_TYPE = []
        for x, y in self.snake.cells:
            drawing.append((x, y, BLACK))
        for x, y in self.bomb.get_bomb_cells():
            drawing.append((x, y, RED))
        for x, y in self.bomb.get_blast_cells():
            drawing.append((x, y, ORANGE))
        for apple in self.apples:
            x, y = apple.cell
            drawing.append((x, y, GREEN))

        return drawing

    def get_new_score(self) -> Optional[int]:
        """
        :return: current score if it's new (meaning it wasn't received using
                 this method yet), or None if the score wasn't changed.
        """
        if not self.new_score_available:
            return None
        self.new_score_available = False
        return self.score

    def __validate_cells_empty(self, cells: List[CELL_TYPE],
                               including_bomb: bool = True) -> bool:
        """
        :param cells: cells to validate that are currently empty
        :param including_bomb: True if the bomb should be checked as well
                               (the current bomb is irrelevant for placing a
                               new one).
        :return: True if the cells given are in the board and not occupied by
                 one of the objects in the game such as snake, apple or a bomb
        """
        full_cells = self.snake.cells + [apple.cell for apple in self.apples]
        if including_bomb:
            full_cells.extend(self.bomb.get_all_cells())

        for cell in cells:
            if not self.__is_cell_legal(cell):
                return False
            if cell in full_cells:
                return False
        return True

    def __randomize_bomb(self) -> Bomb:
        """
        :return: a new bomb in a legal random location
        """
        while True:
            x, y, max_radius, turns_until_boom = \
                game_parameters.get_random_bomb_data()

            bomb = Bomb((x, y), turns_until_boom, max_radius)
            if self.__validate_cells_empty([bomb.cell],
                                           including_bomb=False):
                return bomb

    def __randomize_apple(self) -> Apple:
        """
        :return: a new apple in a legal random location
        """
        while True:
            x, y, score = game_parameters.get_random_apple_data()
            apple = Apple((x, y), score)
            if self.__validate_cells_empty([apple.cell]):
                return apple

    def __generate_apples(self) -> None:
        """
        Make sure that self.apples contains enough apples by generating as many
        as are necessary.
        """
        while len(self.apples) < NUMBER_OF_APPLES:
            if self.__is_board_full():
                self.should_quit = True
                return
            self.apples.append(self.__randomize_apple())

    def __is_board_full(self) -> bool:
        """
        :return: True if all the cells in the board are occupied by the objects
                 in the game (snake, apples, bomb)
        """
        full_cells = len(self.snake.cells) + len(self.apples) + len(
            self.bomb.get_all_cells())
        return game_parameters.WIDTH * game_parameters.HEIGHT <= full_cells

    @staticmethod
    def __is_cell_legal(cell: CELL_TYPE) -> bool:
        """
        :param cell: the cell to check if legal
        :return: True if the given cell is in the game board or False if not
        """
        x, y = cell
        return (0 <= x < game_parameters.WIDTH) and (
                0 <= y < game_parameters.HEIGHT)

    def __update_snake_head(self) -> None:
        """
        Update the snake attributes according to current location - check if
        the snake has touched itself, the board's edges, bomb or ate an apple.
        """
        self.snake.shorten_tail()
        new_head = self.snake.get_new_head()
        # Check if the snake had collided with a border or a bomb
        if (not self.__is_cell_legal(new_head)) or (
                new_head in self.snake.cells) or (
                new_head in self.bomb.get_all_cells()):
            self.should_quit = True
            return
        # Check if thee snake ate an apple
        for apple in self.apples:
            if apple.cell == new_head:
                self.score += apple.score
                self.new_score_available = True
                self.apples.remove(apple)
                self.snake.grow(APPLE_GROW_SIZE)
        # The movement is legal - move the snake
        self.snake.advance_head()

    def __update_bomb(self) -> None:
        """
        Update the bomb attributes according to current round and check if the
        bomb had destroyed the snake or an apple.
        """
        # If the previous bomb had died off, replace it
        if self.bomb.is_done():
            self.bomb = self.__randomize_bomb()
            return

        # Advance the bomb 1 turn
        self.bomb.advance()

        # Check if the bomb had reached a border, in which case it dies off
        for cell in self.bomb.get_all_cells():
            if not self.__is_cell_legal(cell):
                self.bomb = self.__randomize_bomb()
                return

        for cell in self.bomb.get_all_cells():
            # Check if the bomb killed the snake
            if cell in self.snake.cells:
                self.should_quit = True
                return
            # Check if the bomb destroyed any apples
            for apple in self.apples:
                if apple.cell == cell:
                    self.apples.remove(apple)


def main_loop(gd: GameDisplay) -> None:
    """
    Main snake game loop.
    Run the game until it's done.

    :param gd: the graphic object for the game
    """
    # Initialize
    game_board = GameBoard()
    gd.show_score(game_board.score)
    for x, y, color in game_board.draw_board():
        gd.draw_cell(x, y, color)
    gd.end_round()

    while not game_board.should_quit:
        # Get user input
        key_clicked = gd.get_key_clicked()
        # Execute game round logic
        game_board.execute_round(key_clicked)

        # Draw new board
        for x, y, color in game_board.draw_board():
            gd.draw_cell(x, y, color)

        # Notify new score
        new_score = game_board.get_new_score()
        if new_score:
            gd.show_score(new_score)

        # End round
        gd.end_round()
