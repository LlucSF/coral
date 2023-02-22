import numpy as np


class Pawn:
    def __init__(self, color, player_number, rock_position):
        self.color = color
        self.player_number = player_number
        self.position = np.add(rock_position, [0, 0, 1])
        self.in_game = False

    def place(self, position, gameArea):
        z = []
        for z in reversed(range(gameArea.size)):
            if gameArea.space[position[0], position[1], z] != 0:
                break
        pawn_position = np.array([position[0], position[1], z + 1])
        if gameArea.space[pawn_position[0], pawn_position[1], pawn_position[2]] == 0:
            cube_below = gameArea.get_cube_below_face(pawn_position)
            if not (cube_below == self.player_number or cube_below >= 10 or cube_below == 0 or cube_below == -2):
                if self.in_game:
                    self.remove(gameArea)
                self.position = pawn_position
                gameArea.space[self.position[0], self.position[1], self.position[2]] = 10 * self.player_number
                self.in_game = True
                gameArea.update_top_view()
                return True
            else:
                print("Invalid position: Invalid block below")
                return False
        else:
            print("Invalid position: Not empty")
            return False

    def remove(self, gameArea):
        gameArea.space[self.position[0], self.position[1], self.position[2]] = 0
        self.position = []
        self.in_game = False
        gameArea.update_top_view()
