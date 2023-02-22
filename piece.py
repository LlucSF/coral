import numpy as np


class Piece:
    def __init__(self, color, number, neutral):
        self.color = color
        self.number = number
        self.neutral = neutral
        self.c_pos = np.array([0, 0, 0])
        self.l1_pos = np.array([0, 0, 0])
        self.l2_pos = np.array([0, 0, 0])
        self.rotation_axis = ""
        self.rotation_quadrant = 0
        self.used = False

    def place(self, positions, rotation_axis, rotation_quadrant, pawn_position):
        self.used = True
        self.rotation_axis = rotation_axis
        self.rotation_quadrant = rotation_quadrant
        self.c_pos = np.add(positions[0], pawn_position)
        self.l1_pos = np.add(positions[1], pawn_position)
        self.l2_pos = np.add(positions[2], pawn_position)