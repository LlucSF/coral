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


class Player:

    def __init__(self, piece_color, player_number, pawn, piece_pile, gameArea):
        self.action_array = None
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

    def colors_in_hand(self):
        """
        Function to determine the available piece colors in hand
        """
        flags = []
        for piece in self.piece_pile:
            if not piece.used:
                flags.append(piece.neutral)
        return list(set(flags))

    def display_piece_pile_information(self):
        for i in range(self.number_pieces):
            piece = self.piece_pile[i]
            print("Piece ", i, " is ", piece.color, ". Used: ", piece.used, sep="")

    def select_piece_from_pile(self, neutral_flag):
        for piece in self.piece_pile:
            if piece.neutral == neutral_flag and not piece.used:
                return piece

    def new_move_action(self):
        print("Move action [{S}lide or {F}loat]: ", end="")
        player_action = input()
        if player_action == "S":
            self.new_slide_action()
        elif player_action == "F":
            self.turn_action = Action("F")
        else:
            print("Error: Not recognized input. Try again.")
            self.new_move_action()
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

    def new_action(self):
        print("Action [{G}row or {M}ove]: ", end="")
        player_action = input()
        if player_action == "M":
            self.new_move_action()
        elif player_action == "G":
            self.new_grow_action()
        else:
            print("Error: Not recognized input. Try again.")
            self.new_action()

    def new_slide_action(self):
        print("Introduce the x and y offset from the pawn's block to the destiny block:")
        print("x = ", end="")
        x = int(input())
        print("y = ", end="")
        y = int(input())

        destiny_position = np.array([int(x), int(y)])
        starting_position = np.array([self.pawn.position[0], self.pawn.position[1]])
        destiny_position = np.add(starting_position, destiny_position)
        slide_action = Action("S", slide_position=destiny_position)

        slide_action.print()
        print("Submit action?: [{Y}es or {N}o] = ", end="")
        accept_flag = input()
        if accept_flag == "Y":
            BFS_top_view = self.gameArea.get_top_view_for_BFS(self,
                                                              destination_position=destiny_position,
                                                              starting_position=starting_position)
            if BFS.findPath(BFS_top_view, self.gameArea.size) and self.validate_pawn_drop_action(slide_action):
                self.turn_action = slide_action
                return
            else:
                print("Invalid action")
                self.new_slide_action()
                return
        else:
            print("Action canceled")
            self.new_slide_action()

    def new_grow_action(self):
        print("Piece color [{P}layer or {N}eutral]: ", end="")
        player_action = input()
        if player_action == "P":
            neutral_color = False
        elif player_action == "N":
            neutral_color = True
        else:
            print("Error: Not recognized input. Try again.")
            self.new_grow_action()
            return

        if not (neutral_color in self.colors_in_hand()):
            print("Error: Piece color not available.")
            self.new_grow_action()
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
            self.new_grow_action()
            return

        print("Rotation quadrant [{1}, {2}, {3} or {4}] = ", end="")
        rotation_quadrant = int(input())
        if not (rotation_quadrant == 1 or rotation_quadrant == 2 or rotation_quadrant == 3 or rotation_quadrant == 4):
            print("\nError: Not recognized input. Try again.")
            self.new_grow_action()
            return

        grow_action = Action("G", grow_central_block_position=cbp,
                             grow_rotation_axis=rotation_axis,
                             grow_rotation_quadrant=rotation_quadrant,
                             grow_neutral_color=neutral_color)
        grow_action.print()
        print("Submit action?: [{Y}es or {N}o] = ", end="")
        accept_flag = input()
        if accept_flag == "Y" and self.validate_grow_action(grow_action):
            self.turn_action = grow_action
            return
        else:
            print("Action canceled")
            self.new_grow_action()
            return

    def validate_grow_action(self, action):
        block_positions = compute_blocks_positions(action.central_block_position,
                                                   action.rotation_axis,
                                                   action.rotation_quadrant)

        if self.gameArea.is_rock_visible():
            three_rules = self.check_three_rules_from_rock(action.central_block_position,
                                                           action.rotation_axis,
                                                           action.rotation_quadrant)

            valid_position = self.gameArea.check_valid_position(block_positions,
                                                                self.gameArea.rock_position,
                                                                action.rotation_axis,
                                                                action.neutral_color,
                                                                10 * self.pawn.player_number)
            if three_rules and valid_position:
                return True
            else:
                return False

        else:

            valid_position = self.gameArea.check_valid_position(block_positions,
                                                                np.add(self.pawn.position, np.array([0, 0, -1])),
                                                                action.rotation_axis,
                                                                action.neutral_color,
                                                                10 * self.pawn.player_number)
            if valid_position:
                return True
            else:
                return False

    def new_pawn_drop_action(self):
        self.gameArea.update_top_view()
        print("Introduce the x and y offset from the rock:")
        print("x = ", end="")
        x = int(input())
        print("y = ", end="")
        y = int(input())
        position = [x + self.gameArea.rock_position[0], y + self.gameArea.rock_position[1]]
        pawn_drop_action = Action("PD", pawn_drop_position=position)
        pawn_drop_action.print()
        print("Submit action?: [{Y}es or {N}o] = ", end="")
        accept_flag = input()
        if accept_flag == "Y" and self.validate_pawn_drop_action(pawn_drop_action):
            self.turn_action = pawn_drop_action
        else:
            self.new_pawn_drop_action()
            return

    def validate_pawn_drop_action(self, action):
        for z in reversed(range(self.gameArea.size)):
            if self.gameArea.space[action.position[0], action.position[1], z] != 0:
                break
        pawn_position = np.array([action.position[0], action.position[1], z + 1])
        if self.gameArea.space[pawn_position[0], pawn_position[1], pawn_position[2]] == 0:
            cube_below = self.gameArea.get_cube_below_face(pawn_position)
            if cube_below == self.player_number + 1 or cube_below >= 10 or cube_below == 0 or cube_below == -2:
                print("Invalid position: Invalid block below")
                return False
        else:
            print("Invalid position: Not empty")
            return False
        return True

    def apply_action(self):
        """
        Function to apply an action selected by the 'choose_action' function
        """
        # --------------------- Grow action --------------------- #
        if self.turn_action.type == "G":
            piece = self.select_piece_from_pile(self.turn_action.neutral_color)
            positions = compute_blocks_positions(self.turn_action.central_block_position,
                                                 self.turn_action.rotation_axis,
                                                 self.turn_action.rotation_quadrant)
            pawn_block_position = np.add(self.pawn.position, np.array([0, 0, -1]))
            if check_growing_up(positions) and self.game_started:
                self.pawn.remove(self.gameArea)
                piece.place(positions, self.turn_action.rotation_axis,
                            self.turn_action.rotation_quadrant, pawn_block_position)
                self.gameArea.update_piece(piece)
                self.pawn.place(pawn_block_position, self.gameArea)
            else:
                piece.place(positions, self.turn_action.rotation_axis,
                            self.turn_action.rotation_quadrant, pawn_block_position)
                self.gameArea.update_piece(piece)
            if self.pieces_in_pile() == 0:
                self.empty_hand = True

        # --------------------- Pawn drop action --------------------- #
        elif self.turn_action.type == 'PD':
            self.pawn.place(self.turn_action.position, self.gameArea)

        # --------------------- Slide action --------------------- #
        elif self.turn_action.type == 'S':
            self.pawn.remove(self.gameArea)
            self.pawn.place(self.turn_action.position, self.gameArea)

        # --------------------- Float action --------------------- #
        elif self.turn_action.type == 'F':
            self.pawn.remove(self.gameArea)

        # --------------------- Checking for consecutive move actions --------------------- #
        turn_move = (self.turn_action.type == "S" or self.turn_action.type == "F")
        if turn_move and self.last_turn == "S":
            print("Two consecutive move actions. Discarding a piece.")
            self.discard_piece_from_pile()

        # --------------------- Keeping record of this turn action and preparing next turn --------------------- #
        if self.turn_action.type == "PD" and self.turn_action.float:
            self.last_turn = "S"  # Trick to ensure discarding piece after consecutive moves
        else:
            self.last_turn = self.turn_action.type
        self.action_array = []
        self.turn_action = Action("")
