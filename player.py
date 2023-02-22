import numpy as np
import BFS
from action import Action


def compute_blocks_positions(c_pos, rotation_axis, angle):
    l1_increment = np.array([1, 1, 1])
    l2_increment = np.array([1, 1, 1])
    l1_increment[rotation_axis] = 0
    l2_increment[rotation_axis] = 0
    other_zero = [0, 1, 2]
    other_zero.remove(rotation_axis)

    if angle == 1:
        l1_increment = 1 * l1_increment
        l1_increment[other_zero[0]] = 0

        l2_increment = 1 * l2_increment
        l2_increment[other_zero[1]] = 0

    if angle == 4:
        l1_increment = 1 * l1_increment
        l1_increment[other_zero[1]] = 0

        l2_increment = -1 * l2_increment
        l2_increment[other_zero[0]] = 0

    if angle == 3:
        l1_increment = -1 * l1_increment
        l1_increment[other_zero[0]] = 0

        l2_increment = -1 * l2_increment
        l2_increment[other_zero[1]] = 0

    if angle == 2:
        l1_increment = -1 * l1_increment
        l1_increment[other_zero[1]] = 0

        l2_increment = 1 * l2_increment
        l2_increment[other_zero[0]] = 0

    l1_pos = np.add(c_pos, l1_increment)
    l2_pos = np.add(c_pos, l2_increment)
    positions = np.array([c_pos, l1_pos, l2_pos])
    return positions


def check_growing_up(positions):
    for position in positions:
        if np.array_equal(position, np.array([0, 0, 1])):
            return True
    return False


# TODO adapt the player class to the Action class

class Player:

    def __init__(self, piece_color, player_number, pawn, piece_pile, gameArea):
        self.player_type = "H"
        self.piece_color = piece_color
        self.gameArea = gameArea
        self.player_number = player_number
        self.pawn = pawn
        self.piece_pile = piece_pile
        self.number_pieces = len(self.piece_pile)
        self.last_turn = ""
        self.floating = False
        self.empty_hand = False
        self.game_started = False
        self.turn_action = Action("")
        # self.print()

    def pieces_in_pile(self) -> int:
        cnt = 0
        for piece in self.piece_pile:
            if not piece.used:
                cnt = cnt + 1
        return cnt

    def move(self):
        print("Move action [{S}lide or {F}loat]: ", end="")
        player_action = input()
        if player_action == "S":
            self.slide()
        elif player_action == "F":
            self.float()
        else:
            print("Error: Not recognized input. Try again.")
            self.move()
            return

    def grow_from_rock(self):
        # Command line interaction
        print("Piece color [{P}layer or {N}eutral]: ", end="")
        player_action = input()
        if player_action == "P":
            neutral_flag = False
        elif player_action == "N":
            neutral_flag = True
        else:
            print("Error: Not recognized input. Try again.")
            self.grow_from_rock()
            return

        print("Introduce the offset of the piece's central block to the rock:")
        print("x = ", end="")
        x = int(input())
        print("y = ", end="")
        y = int(input())
        print("z = ", end="")
        z = int(input())
        position = np.array([int(x), int(y), int(z)])

        print("Rotation axis [{x} ,{y} or {z}] = ", end="")
        rotation_axis = input()
        if rotation_axis == "x":
            rotation_axis = 0
        elif rotation_axis == "y":
            rotation_axis = 1
        elif rotation_axis == "z":
            rotation_axis = 2
        else:
            print("Error: Not recognized input. Try again.")
            self.grow_from_rock()
            return

        print("Rotation quadrant [{1}, {2}, {3} or {4}] = ", end="")
        angle = int(input())
        if not (angle == 1 or angle == 2 or angle == 3 or angle == 4):
            print("\nError: Not recognized input. Try again.")
            self.grow_from_rock()
            return

        # Piece selection and placement
        for i in range(self.number_pieces):
            if self.piece_pile[i].neutral == neutral_flag and not self.piece_pile[i].used:
                piece = self.piece_pile[i]
                if self.check_three_rules_from_rock(position, rotation_axis, angle):
                    self.place_piece(piece, position, rotation_axis, angle, False)
                else:
                    self.grow_from_rock()
                return
        print("No more pieces to use")
        return

    def check_three_rules_from_rock(self, c_pos, rotation_axis, angle):
        positions = compute_blocks_positions(c_pos, rotation_axis, angle)

        # Rule 1, covering one side of the rock
        rule1 = False
        for i in range(3):
            block = positions[i]
            if np.sum(np.abs(block)) == 1:
                rule1 = True

        # Rule 2, connection with the sand
        rule2 = False
        for i in range(3):
            block = positions[i]
            block = np.add(block, self.gameArea.rock_position)
            if self.gameArea.get_cube_below_face(block) == -2:
                rule2 = True

        # Rule 3, not covering another piece
        rule3 = True
        for i in range(3):
            block = positions[i]
            block = np.add(block, self.gameArea.rock_position)
            block_below = self.gameArea.get_cube_below_face(block)
            other_player_number = 0
            if self.player_number == 0:
                other_player_number = 2
            elif self.player_number == 1:
                other_player_number = 1
            if block_below == other_player_number:
                rule3 = False

        if not rule1:
            return False
        elif rule2 and rule3:
            return True
        elif rule2 and not rule3:
            return False
        elif not rule2:
            if self.gameArea.count_rock_visible_sides() == 1:
                return True
        else:
            return False

    def create_action(self):
        if self.floating:
            self.place_pawn()
            self.floating = False
        else:
            print("Action [{G}row or {M}ove]: ", end="")
            player_action = input()
            if player_action == "M":
                self.move()
            elif player_action == "G":
                self.grow()
            else:
                print("Error: Not recognized input. Try again.")
                self.play()

    def place_pawn(self):
        if self.floating:
            print("Returning from floating ...")
        print("Introduce the offset of the pawn to the rock:")
        print("x = ", end="")
        x = int(input())
        print("y = ", end="")
        y = int(input())
        position = np.add(np.array([int(x), int(y), 0]), self.gameArea.rock_position)
        if not self.pawn.place(position, self.gameArea):
            self.place_pawn()

    def place_piece(self, piece, c_pos, rotation_axis, angle, game_start):
        pawn_block_position = np.add(self.pawn.position, np.array([0, 0, -1]))
        positions = compute_blocks_positions(c_pos, rotation_axis, angle)
        if self.gameArea.check_valid_position(positions, pawn_block_position,
                                              rotation_axis, piece.neutral,
                                              10 * self.pawn.player_number):
            if not piece.neutral:
                piece.c_pos = np.add(positions[0], pawn_block_position)
                piece.l1_pos = np.add(positions[1], pawn_block_position)
                piece.l2_pos = np.add(positions[2], pawn_block_position)
                piece.used = True
                self.gameArea.update_piece(piece)
                self.last_turn = "G"
            elif check_growing_up(positions) and game_start:
                print("Growing up")
                self.pawn.remove(self.gameArea)
                piece.c_pos = np.add(positions[0], pawn_block_position)
                piece.l1_pos = np.add(positions[1], pawn_block_position)
                piece.l2_pos = np.add(positions[2], pawn_block_position)
                piece.used = True
                self.gameArea.update_piece(piece)
                self.pawn.place(pawn_block_position, self.gameArea)
            else:
                piece.c_pos = np.add(positions[0], pawn_block_position)
                piece.l1_pos = np.add(positions[1], pawn_block_position)
                piece.l2_pos = np.add(positions[2], pawn_block_position)
                piece.used = True
                self.gameArea.update_piece(piece)
        else:
            self.grow()

    def display_piece_pile_information(self):
        for i in range(self.number_pieces):
            piece = self.piece_pile[i]
            print("Piece ", i, " is ", piece.color, ". Used: ", piece.used, sep="")

    def float(self):
        self.pawn.remove(self.gameArea)
        self.floating = True
        if self.last_turn == "S" or self.last_turn == "F":
            print("Your have used the MOVE action before. Choose a piece to discard: ")
            self.discard_piece_from_pile()
        self.last_turn = "F"

    def slide(self):
        self.gameArea.update_top_view()
        print("Introduce the x and y offset from the pawn's block to the destiny block:")
        print("x = ", end="")
        x = int(input())
        print("y = ", end="")
        y = int(input())

        destiny_position = np.array([int(x), int(y)])
        starting_position = np.array([self.pawn.position[0], self.pawn.position[1]])
        destiny_position = np.add(starting_position, destiny_position)
        BFS_top_view = self.gameArea.get_top_view_for_BFS(self,
                                                          destination_position=destiny_position,
                                                          starting_position=starting_position)
        if BFS.findPath(BFS_top_view, self.gameArea.size):
            if not self.pawn.place(destiny_position, self.gameArea):
                self.slide()
            if self.last_turn == "S" or self.last_turn == "F":
                print("Your have used the MOVE action before. Choose a piece to discard: ")
                self.discard_piece_from_pile()
            self.floating = False
            self.last_turn = "S"
        else:
            print("No path found to reach the destination. Try again")
            self.slide()
        return

    def discard_piece_from_pile(self):
        if not self.pieces_in_pile() == 0:
            self.display_piece_pile_information()
            print("Index = ", end="")
            i = int(input())
            if i > self.number_pieces:
                print("Invalid piece number. Try again.")
                self.discard_piece_from_pile()
            elif self.piece_pile[i].used:
                print("Invalid piece number. Try again.")
                self.discard_piece_from_pile()
            else:
                self.piece_pile[i].used = True

    def print(self):
        print("\nPlayer number:", self.player_number)
        print("Player color:", self.piece_color)
        print("Player type:", self.player_type)

    def create_action(self):
        print("Action [{G}row or {M}ove]: ", end="")
        player_action = input()
        if player_action == "M":
            self.move()
        elif player_action == "G":
            self.grow()
        else:
            print("Error: Not recognized input. Try again.")
            self.play()

    def grow(self):
        print("Piece color [{P}layer or {N}eutral]: ", end="")
        player_action = input()
        if player_action == "P":
            neutral_color = False
        elif player_action == "N":
            neutral_color = True
        else:
            print("Error: Not recognized input. Try again.")
            self.grow_dialogue()
            return

        print("Introduce the offset of the piece's central block to the rock:")
        print("x = ", end="")
        x = int(input())
        print("y = ", end="")
        y = int(input())
        print("z = ", end="")
        z = int(input())
        cbp = np.array([int(x), int(y), int(z)])

        print("Rotation axis [{x} ,{y} or {z}] = ", end="")
        rotation_axis = input()
        if rotation_axis == "x":
            rotation_axis = 0
        elif rotation_axis == "y":
            rotation_axis = 1
        elif rotation_axis == "z":
            rotation_axis = 2
        else:
            print("Error: Not recognized input. Try again.")
            self.grow_dialogue()
            return

        print("Rotation quadrant [{1}, {2}, {3} or {4}] = ", end="")
        rotation_quadrant = int(input())
        if not (rotation_quadrant == 1 or rotation_quadrant == 2 or rotation_quadrant == 3 or rotation_quadrant == 4):
            print("\nError: Not recognized input. Try again.")
            self.grow_dialogue()
            return

        grow_action = Action("G", grow_central_block_position=cbp,
                             grow_rotation_axis=rotation_axis,
                             grow_rotation_quadrant=rotation_quadrant,
                             grow_neutral_color=neutral_color)
        grow_action.print()
        self.turn_action = grow_action


