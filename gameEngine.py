from pawn import Pawn
from player import Player
from piece import Piece
from gameArea import GameArea
from playerAI import PlayerAI

# import cv2
# import os
# import random
# def record_video(image_folder) -> None:
#     video_name = image_folder + '/video.avi'
#     images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
#     frame = cv2.imread(os.path.join(image_folder, images[0]))
#     height, width, layers = frame.shape
#     video = cv2.VideoWriter(video_name, 0, fps=10, frameSize=(width, height))
#     for image in images:
#         video.write(cv2.imread(os.path.join(image_folder, image)))
#     cv2.destroyAllWindows()
#     video.release()


class GameEngine:
    def __init__(self, game_type, AI_behaviour):
        self.player_turn = 0
        self.player_array = []
        self.gameArea = GameArea()
        self.figure = []
        self.game_started = False
        self.player_without_pieces = False
        self.game_end = False
        self.turn_number = 0
        if game_type == "HvsH":
            self.add_H_player('red', 0)
            self.add_H_player('yellow', 1)
        elif game_type == "HvsAI":
            self.add_H_player('red', 0)
            self.add_AI_player('yellow', 1, AI_behaviour[0])
        elif game_type == "AIvsH":
            self.add_AI_player('red', 0, AI_behaviour[0])
            self.add_H_player('yellow', 1)
        elif game_type == "AIvsAI":
            self.add_AI_player('red', 0, AI_behaviour[0])
            self.add_AI_player('yellow', 1, AI_behaviour[1])
        else:
            print("Invalid game type")
        self.run()

    def score_game(self):
        if self.player_array[0].pawn.in_game:
            self.player_array[0].pawn.remove(self.gameArea)
        if self.player_array[1].pawn.in_game:
            self.player_array[1].pawn.remove(self.gameArea)
        player_0_score = 0
        player_1_score = 0
        scoring_top_view = self.gameArea.get_top_view_for_scoring()
        for x in range(self.gameArea.size):
            for y in range(self.gameArea.size):
                if scoring_top_view[x, y] == 1:
                    player_0_score = player_0_score + 1
                elif scoring_top_view[x, y] == 2:
                    player_1_score = player_1_score + 1
        print("Player 0 with the", self.player_array[0].piece_color, "color has scored", player_0_score, "blocks.")
        print("Player 1 with the", self.player_array[1].piece_color, "color has scored", player_1_score, "blocks.")
        if player_0_score > player_1_score:
            print("Player 0 with the", self.player_array[0].piece_color, "color WINS!")
        elif player_1_score > player_0_score:
            print("Player 1 with the", self.player_array[1].piece_color, "color WINS!")
        else:
            print('It is a TIE from the top view! The TIEBREAK is by height and ...')
            self.score_tiebreak()

    def score_tiebreak(self):
        for z in reversed(range(self.gameArea.size - 1)):
            player_0_score = 0
            player_1_score = 0
            for x in range(self.gameArea.size):
                for y in range(self.gameArea.size):
                    if self.gameArea.space[x, y, z + 1] == 0:
                        if self.gameArea.space[x, y, z] == 1:
                            player_0_score = player_0_score + 1
                        elif self.gameArea.space[x, y, z] == 2:
                            player_1_score = player_1_score + 1
            if player_0_score > 0 or player_1_score > 0:
                if player_0_score > player_1_score:
                    print('¡¡¡ Player 0 with the', self.player_array[0].piece_color, 'color WINS with', player_0_score,
                          'blocks in level', z - self.gameArea.rock_position[2] + 1, '!!!')
                    return
                elif player_1_score > player_0_score:
                    print('¡¡¡ Player 1 with the', self.player_array[1].piece_color, 'color WINS with', player_1_score,
                          'blocks in level', z - self.gameArea.rock_position[2] + 1, '!!!')
                    return
                else:
                    print('Another tie on level', z - self.gameArea.rock_position[2], '!')
        print("¡¡¡ Your competition lead to a perfect symbiosis. ABSOLUTE TIE !!!")

    def add_H_player(self, color, number):
        pawn = Pawn(color, number + 1, self.gameArea.rock_position)
        piece_pile = []
        for i in range(6):
            piece = Piece(color, number + 1, False)
            piece_pile.append(piece)
        for i in range(3):
            piece = Piece('white', 5, True)
            piece_pile.append(piece)
        player = Player(color, number, pawn, piece_pile, self.gameArea)
        self.player_array.append(player)

    def add_AI_player(self, color, number, behaviour):
        pawn = Pawn(color, number + 1, self.gameArea.rock_position)
        piece_pile = []
        for i in range(6):
            piece = Piece(color, number + 1, False)
            piece_pile.append(piece)
        for i in range(3):
            piece = Piece('white', 5, True)
            piece_pile.append(piece)
        player = PlayerAI(color, number, pawn, piece_pile, behaviour, self.gameArea)
        self.player_array.append(player)

    def run(self):
        while (self.player_array[0].pieces_in_pile() + self.player_array[1].pieces_in_pile()) != 0:
            # ---------------- Player selection ---------------- #
            player = self.player_array[self.player_turn]
            print("\n----- Turn ", self.turn_number, ": Player ", player.piece_color, " -----", sep="")

            # ---------------- First stage: grow from rock ---------------- #
            if self.gameArea.is_rock_visible():
                print("* Cover the rock *")
                # Human
                if player.player_type == "H":
                    player.new_grow_action()

                # AI
                elif player.player_type == "AI":
                    player.compute_all_legal_grows()
                    player.choose_action()

                player.apply_action()

            # ---------------- Second stage: place the pawn ---------------- #
            elif (not self.pawns_in_game()) and (not self.game_started):
                print("* Place the pawn *")
                # Human
                if player.player_type == "H":
                    player.new_pawn_drop_action()

                # AI
                elif player.player_type == "AI":
                    player.compute_all_legal_pawn_drops()
                    player.choose_action()

                player.apply_action()

            # ---------------- Third stage: grow the reef ---------------- #
            else:
                print("* Grow the reef *")
                # Human
                if player.player_type == "H":
                    if player.last_turn == "F":
                        player.new_pawn_drop_action()
                    elif player.last_turn != "F":
                        player.new_action()
                # AI
                elif player.player_type == "AI":
                    if player.last_turn != "F":
                        player.compute_all_legal_grows()
                        player.compute_all_legal_moves()
                    elif player.last_turn == "F":
                        player.compute_all_legal_pawn_drops()
                    player.choose_action()

                player.apply_action()

            # ----------------Check end game conditions ---------------- #
            if player.empty_hand and not self.player_without_pieces:
                self.player_without_pieces = True
                print("   ªªª Player", player.piece_color, "has run out of pieces. ªªª   ")

            if self.player_without_pieces and not player.empty_hand:
                if player.player_type == "H":
                    print("The other player has run out of pieces. Choose a piece to discard: ")
                    player.discard_piece_from_pile()
                if player.player_type == "AI":
                    player.discard_piece_from_pile()

                if player.pieces_in_pile() == 0:
                    break

            # ---------------- Update game state info ---------------- #
            self.gameArea.draw_coral(self.turn_number)
            self.turn_number += 1

            # ---------------- Turn exchange ---------------- #
            if not self.player_without_pieces:
                self.change_turns()
            elif player.empty_hand:
                self.change_turns()

        print("\n*********   Game Score  *********")
        self.score_game()
        self.gameArea.draw_coral("Final position")
        return

    def pawns_in_game(self):
        flag = True
        for player in self.player_array:
            flag = flag and player.pawn.in_game
        if flag and not self.game_started:
            self.game_started = True
            self.player_array[0].game_started = True
            self.player_array[1].game_started = True
        return flag

    def change_turns(self):
        if self.player_turn == 0:
            self.player_turn = 1
        else:
            self.player_turn = 0
