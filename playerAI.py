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
            for rotation_axis in range(3):
                for rotation_quadrant in range(1, 5):
                    for cbp in cbp_array:
                        for neutral_color in self.colors_in_hand():
                            grow_action = Action("G", grow_central_block_position=cbp,
                                                 grow_rotation_axis=rotation_axis,
                                                 grow_rotation_quadrant=rotation_quadrant,
                                                 grow_neutral_color=neutral_color)
                            if self.validate_grow_action(grow_action):
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
            print(" Action ", action_index + 1, ":", sep="")
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
