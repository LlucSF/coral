import numpy as np
import matplotlib
import matplotlib.pyplot as plt


class GameArea:
    def __init__(self):
        self.size = 17
        self.space = np.zeros((self.size, self.size, self.size))
        self.top_view = np.zeros((self.size, self.size))
        self.rock_position = np.array(
            [int(np.floor(self.size / 2)), int(np.floor(self.size / 2)), 1])
        self.figure = []
        self.frames = []
        self.figure_cnt = 0
        self.rock_visible = True
        self.place_rock()
        self.place_sand()
        # self.draw_coral()

    def reset_game_space(self):
        self.space = np.zeros((self.size, self.size, self.size))
        self.top_view = np.zeros((self.size, self.size))
        self.rock_position = np.array(
            [int(np.floor(self.size / 2)), int(np.floor(self.size / 2)), int(np.floor(self.size / 2))])
        self.figure = []
        self.rock_visible = True
        self.place_rock()
        self.place_sand()

    def update_top_view(self):
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    if self.space[x, y, z] != 0:
                        self.top_view[x, y] = self.space[x, y, z]

    def place_rock(self):
        self.space[self.rock_position[0], self.rock_position[1], self.rock_position[2]] = -1

    def place_sand(self):
        for x in range(self.size):
            for y in range(self.size):
                self.space[x][y][self.rock_position[2] - 1] = -2
        self.update_top_view()

    def update_piece(self, piece):
        self.space[piece.c_pos[0], piece.c_pos[1], piece.c_pos[2]] = piece.number
        self.space[piece.l1_pos[0], piece.l1_pos[1], piece.l1_pos[2]] = piece.number
        self.space[piece.l2_pos[0], piece.l2_pos[1], piece.l2_pos[2]] = piece.number
        self.update_top_view()

    def is_rock_visible(self) -> bool:
        dummy = np.add(self.rock_position, [1, 0, 0])
        flag1 = self.space[dummy[0], dummy[1], dummy[2]] == 0

        dummy = np.add(self.rock_position, [-1, 0, 0])
        flag2 = self.space[dummy[0], dummy[1], dummy[2]] == 0

        dummy = np.add(self.rock_position, [0, 1, 0])
        flag3 = self.space[dummy[0], dummy[1], dummy[2]] == 0

        dummy = np.add(self.rock_position, [0, -1, 0])
        flag4 = self.space[dummy[0], dummy[1], dummy[2]] == 0

        dummy = np.add(self.rock_position, [0, 0, 1])
        flag5 = self.space[dummy[0], dummy[1], dummy[2]] == 0

        if not (flag1 or flag2 or flag3 or flag4 or flag5) and self.rock_visible:
            self.rock_visible = False
            # print("\n||| +++ *** Place the pawns  *** +++ |||\n")
        return self.rock_visible

    def count_rock_visible_sides(self) -> int:
        cnt = 0
        dummy = np.add(self.rock_position, [1, 0, 0])
        if self.space[dummy[0], dummy[1], dummy[2]] == 0:
            cnt = cnt + 1
        dummy = np.add(self.rock_position, [-1, 0, 0])
        if self.space[dummy[0], dummy[1], dummy[2]] == 0:
            cnt = cnt + 1
        dummy = np.add(self.rock_position, [0, 1, 0])
        if self.space[dummy[0], dummy[1], dummy[2]] == 0:
            cnt = cnt + 1
        dummy = np.add(self.rock_position, [0, -1, 0])
        if self.space[dummy[0], dummy[1], dummy[2]] == 0:
            cnt = cnt + 1
        dummy = np.add(self.rock_position, [0, 0, 1])
        if self.space[dummy[0], dummy[1], dummy[2]] == 0:
            cnt = cnt + 1
        return cnt

    def get_cube_below_face(self, position):
        return self.space[position[0], position[1], position[2] - 1]

    # TODO: ensure blocks dont fall by implementing an iterative method which checks
    #  how many blocks a side of a piece is supporting respect the other sides
    # TODO: split the valid position flags in independent functions

    def check_valid_position(self, blocks_positions, pawn_block_position, rotation_axis, piece_neutral,
                             pawn_number) -> bool:
        # First check: Empty space
        empty_flag = True
        if not piece_neutral:
            for i in range(3):
                block = np.add(blocks_positions[i], pawn_block_position)
                empty_flag = empty_flag and self.space[block[0], block[1], block[2]] == 0
            if not empty_flag:
                # print("Invalid position: Not empty.")
                return False
        else:
            for i in range(3):
                block = np.add(blocks_positions[i], pawn_block_position)
                empty_0_flag = self.space[block[0], block[1], block[2]] == 0
                empty_pawn_flag = self.space[block[0], block[1], block[2]] == pawn_number
                empty_flag = empty_flag and (empty_0_flag or empty_pawn_flag)
            if not empty_flag:
                # print("Invalid position: Not empty.")
                return False

        # Second check: Block connectivity
        connection_flag = False
        for i in range(3):
            block = blocks_positions[i]
            if np.sum(np.abs(block)) == 1:
                connection_flag = True
        if not connection_flag:
            # print("Invalid position: Piece not connected to pawn's block.")
            return False

        # Third check: Falling block
        c_block = np.add(blocks_positions[0], pawn_block_position)
        c_flag = self.get_cube_below_face(c_block) == 0

        l1_block = np.add(blocks_positions[1], pawn_block_position)
        l1_flag = self.get_cube_below_face(l1_block) == 0

        l2_block = np.add(blocks_positions[2], pawn_block_position)
        l2_flag = self.get_cube_below_face(l2_block) == 0

        if c_flag and l1_flag and l2_flag:
            # print("Invalid position: Piece falls. Three blocks in the air")
            return False
        if rotation_axis == 2:
            if c_flag and (l1_flag or l2_flag):
                # print("Invalid position: Piece falls. Two blocks in the air")
                return False
        elif rotation_axis == 1 or rotation_axis == 0:
            z_vector = np.array([c_block[2], l1_block[2], l2_block[2]])
            z_min = np.argmin(z_vector)
            if c_flag and z_min == 0:
                # print("Invalid position: Piece falls. Two blocks in the air including central L")
                return False
            elif z_min != 0 and np.array([c_flag, l1_flag, l2_flag])[z_min]:
                # print("Invalid position: Piece falls. Two blocks in the air including central ꓶ")
                return False

        # Fourth check: growing over enemy pawn if there are pawns over the board
        enemy_pawn_code = 0
        if np.any(self.space >= 10):
            if self.space[pawn_block_position[0], pawn_block_position[1], pawn_block_position[2] + 1] == 10:
                enemy_pawn_code = 20
            elif self.space[pawn_block_position[0], pawn_block_position[1], pawn_block_position[2] + 1] == 20:
                enemy_pawn_code = 10
            c_flag = self.get_cube_below_face(c_block) == enemy_pawn_code
            l1_flag = self.get_cube_below_face(l1_block) == enemy_pawn_code
            l2_flag = self.get_cube_below_face(l2_block) == enemy_pawn_code
            if c_flag or l1_flag or l2_flag:
                return False

        return True

    def get_top_view_for_BFS(self, player, destination_position=None, starting_position=None):
        BFS_top_view = np.zeros((self.size, self.size))
        for x in range(self.size):
            for y in range(self.size):
                if self.top_view[x, y] == -2:  # Sand
                    BFS_top_view[x, y] = 0
                elif self.top_view[x, y] == (player.player_number + 1):  # Player color
                    BFS_top_view[x, y] = 0
                elif self.check_pawn_at_xy(x, y):  # Player Pawns
                    BFS_top_view[x, y] = 0
                else:  # Available path
                    BFS_top_view[x, y] = 3
        if destination_position is not None:
            BFS_top_view[destination_position[0], destination_position[1]] = 2
        if starting_position is not None:
            BFS_top_view[starting_position[0], starting_position[1]] = 1
        return BFS_top_view

    def draw_coral(self, title):
        self.figure = plt.figure(str(title)).add_subplot(projection='3d')
        self.figure_cnt = self.figure_cnt + 1
        colors = np.empty(self.space.shape, dtype=object)
        colors[self.space == -1] = 'grey'
        colors[self.space == 1] = "red"
        colors[self.space == 2] = "yellow"
        colors[self.space == 10] = 'salmon'
        colors[self.space == 20] = 'goldenrod'
        colors[self.space == 5] = 'white'
        colors[self.space == -2] = 'papayawhip'
        light = matplotlib.colors.LightSource(azdeg=-135)
        self.figure.voxels(self.space, facecolors=colors, lightsource=light)
        self.figure.set_aspect('equal')
        self.figure.view_init(50, -100, 0)
        plt.axis("off")
        plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
        plt.show()
        # plt.savefig("C:/Users/Lluc/PycharmProjects/coralEngine/img/initial_setup/Coral_figure_" + str(random.randrange(10000000)) + ".png")
        # plt.close()

    def get_top_view_for_scoring(self):
        scoring_top_view = self.top_view
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    if self.space[x, y, z] != 0 and not self.space[x, y, z] == 10 and not self.space[x, y, z] == 20:
                        scoring_top_view[x, y] = self.space[x, y, z]
        return scoring_top_view

    def check_pawn_at_xy(self, x, y) -> bool:
        for z in reversed(range(self.size)):
            if self.space[x, y, z] >= 10:
                return True
        return False
