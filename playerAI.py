import numpy as np
import random
from player import Player
from player import compute_blocks_positions
from player import check_growing_up
from itertools import product
import BFS
from action import Action


class PlayerAI(Player):
    def __init__(self, piece_color, player_number, pawn, piece_pile, behaviour, gameArea):
        super().__init__(piece_color, player_number, pawn, piece_pile, gameArea)
        self.player_type = "AI"
        self.behaviour = behaviour
        self.action_array = []
        self.turn_action = Action("")

    def colors_in_hand(self):
        """
        Function to determine the available piece colors in hand
        """
        flags = []
        for piece in self.piece_pile:
            if not piece.used:
                flags.append(piece.neutral)
        return list(set(flags))

    def compute_all_legal_grows(self):
        """
        Function to compute all legal grow action in a specific game stage
        """
        if not self.pieces_in_pile() == 0:
            cbp_array = (list(product([0, 1, -1, 2, -2], repeat=3)))
            dummy = (list(product([0, 1, -1, 2, -2], repeat=3)))
            for item in dummy:
                if np.sum(np.abs(item)) > 2 or np.sum(np.abs(item)) == 0:
                    cbp_array.remove(item)
            del dummy
            pawn_block_position = np.add(self.pawn.position, np.array([0, 0, -1]))
            for rotation_axis in range(3):
                for rotation_quadrant in range(1, 5):
                    for cbp in cbp_array:
                        for neutral_color in self.colors_in_hand():
                            if self.gameArea.is_rock_visible():
                                three_rules = self.check_three_rules_from_rock(cbp, rotation_axis,
                                                                               rotation_quadrant)
                                block_positions = compute_blocks_positions(cbp, rotation_axis, rotation_quadrant)
                                valid_position = self.gameArea.check_valid_position(block_positions,
                                                                                    self.gameArea.rock_position,
                                                                                    rotation_axis, neutral_color,
                                                                                    10 * self.pawn.player_number)
                                if three_rules and valid_position:
                                    grow_action = Action("G", grow_central_block_position=cbp,
                                                         grow_rotation_axis=rotation_axis,
                                                         grow_rotation_quadrant=rotation_quadrant,
                                                         grow_neutral_color=neutral_color)
                                    self.action_array.append(grow_action)
                            else:
                                block_positions = compute_blocks_positions(cbp, rotation_axis, rotation_quadrant)
                                valid_position = self.gameArea.check_valid_position(block_positions,
                                                                                    pawn_block_position,
                                                                                    rotation_axis, neutral_color,
                                                                                    10 * self.pawn.player_number)
                                if valid_position:
                                    grow_action = Action("G", grow_central_block_position=cbp,
                                                         grow_rotation_axis=rotation_axis,
                                                         grow_rotation_quadrant=rotation_quadrant,
                                                         grow_neutral_color=neutral_color)
                                    self.action_array.append(grow_action)

    def compute_all_legal_pawn_drops(self):
        """
        Function to compute all legal pawn drop action in a specific game stage
        """
        top_view = self.gameArea.get_top_view_for_BFS(self)
        for x in range(self.gameArea.size):
            for y in range(self.gameArea.size):
                if top_view[x, y] == 3:
                    if self.last_turn == "F":
                        pawn_drop_action = Action("PD", pawn_drop_position=[x, y], pawn_drop_float=True)
                    else:
                        pawn_drop_action = Action("PD", pawn_drop_position=[x, y], pawn_drop_float=False)
                    self.action_array.append(pawn_drop_action)

    def compute_all_legal_moves(self):
        """
        Function to compute all legal move action (slide and float) in a specific game stage
        """
        top_view = self.gameArea.get_top_view_for_BFS(self, starting_position=np.add(self.pawn.position, [0, 0, -1]))
        for x in range(self.gameArea.size):
            for y in range(self.gameArea.size):
                if top_view[x, y] == 3:
                    slide_map = self.gameArea.get_top_view_for_BFS(self,
                                                                   starting_position=np.add(self.pawn.position,
                                                                                            [0, 0, -1]),
                                                                   destination_position=np.array([x, y]))
                    if BFS.findPath(slide_map, self.gameArea.size):
                        slide_action = Action("S", slide_position=[x, y])
                        self.action_array.append(slide_action)
        self.action_array.append(Action("F"))  # Appending float action

    def choose_action(self):
        """
        Function to evaluate and choose an action
        """
        self.print_action_array_information()
        if self.behaviour == "random":
            action_index = int(random.randrange(len(self.action_array)))
            self.turn_action = self.action_array[action_index]
            print(" Action", action_index + 1, ":")
            self.turn_action.print()
        if self.behaviour == "minmax":
            self.generate_game_tree()
            self.score_game_positions()
            self.choose_best_action()

    # TODO: define the 'minmax' behaviour
    def generate_game_tree(self):
        print(self.behaviour)

    def score_game_positions(self):
        print(self.behaviour)

    def choose_best_action(self):
        print(self.behaviour)

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

    def select_piece_from_pile(self, neutral_flag):
        for piece in self.piece_pile:
            if piece.neutral == neutral_flag and not piece.used:
                return piece

    def discard_piece_from_pile(self):
        if not self.pieces_in_pile() == 0:
            discard_pile = []
            for piece in self.piece_pile:
                if not piece.used:
                    discard_pile.append(piece)
            if self.behaviour == "random":
                index = random.randrange(len(discard_pile))
                discard_pile[index].used = True

    def print(self):
        super().print()
        print("AI behaviour:", self.behaviour)

    def print_action_array_information(self):
        moves = 0
        grows = 0
        pawn_drops = 0
        for action in self.action_array:
            if action.type == "G":
                grows += 1
            if action.type == "S" or action.type == "F":
                moves += 1
            if action.type == "PD":
                pawn_drops += 1

        print(" Number of legal actions:", moves + grows + pawn_drops)
        print(" - Grows:", grows)
        print(" - Moves:", moves)
        print(" - Pawn drops:", pawn_drops)
