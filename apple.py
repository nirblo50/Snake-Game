from game_parameters import CELL_TYPE


class Apple:
    """
    Represents an apple in the game.
    The snake should eat apples to gain score.
    """

    def __init__(self, cell: CELL_TYPE, score: int):
        """
        :param cell: the location of the apple (row, col)
        :param score: the score that the player should get for eating this
                      apple
        """
        self.cell = cell
        self.score = score
