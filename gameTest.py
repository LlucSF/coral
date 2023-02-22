from gameEngine import GameEngine
import numpy as np


# ********** Game setup ********** #
myGameEngine = GameEngine(2, ['red', 'yellow'])
# ------------------------------------------------------ #

# ********** Piece 1 red player ********** #
piece1 = myGameEngine.player_array[0].piece_pile[0]
position1 = np.array([-1, 0, 0])
axis1 = 2
angle1 = 2
myGameEngine.player_array[0].place_piece(piece1, position1, axis1, angle1, myGameEngine.gameArea, False)
# ********** Piece 2 yellow player ********** #
piece2 = myGameEngine.player_array[1].piece_pile[0]
position2 = np.array([1, 0, 0])
axis2 = 0
angle2 = 1
myGameEngine.player_array[1].place_piece(piece2, position2, axis2, angle2, myGameEngine.gameArea, False)
# ********** Piece 3 red player ********** #
piece3 = myGameEngine.player_array[0].piece_pile[1]
position3 = np.array([0, 1, 0])
axis3 = 0
angle3 = 1
myGameEngine.player_array[0].place_piece(piece3, position3, axis3, angle3, myGameEngine.gameArea, False)
# ********** Piece 4 yellow player ********** #
piece4 = myGameEngine.player_array[1].piece_pile[1]
position4 = np.array([0, -1, 0])
axis4 = 0
angle4 = 2
myGameEngine.player_array[0].place_piece(piece4, position4, axis4, angle4, myGameEngine.gameArea, False)
# ********** Piece 5 red player ********** #
piece4 = myGameEngine.player_array[0].piece_pile[6]
position4 = np.array([0, 0, 2])
axis4 = 1
angle4 = 4
myGameEngine.player_array[0].place_piece(piece4, position4, axis4, angle4, myGameEngine.gameArea, False)
# ------------------------------------------------------ #

# ********** Pawn yellow player ********** #
pawn2position = np.add(np.array([0, 0, 0]), myGameEngine.gameArea.rock_position)
myGameEngine.player_array[1].pawn.place(pawn2position, myGameEngine.gameArea)
# ********** Pawn red player ********** #
pawn1position = np.add(np.array([0, -1, 0]), myGameEngine.gameArea.rock_position)
myGameEngine.player_array[0].pawn.place(pawn1position, myGameEngine.gameArea)
# ------------------------------------------------------ #

# ********** Continue game ********** #
# myGameEngine.game_end = True
for i in range(7):
    myGameEngine.player_array[0].piece_pile[i].used = True
for i in range(7):
    myGameEngine.player_array[1].piece_pile[i].used = True
myGameEngine.run()
# ------------------------------------------------------ #