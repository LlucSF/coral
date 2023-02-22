class Action:
    def __init__(self, action_type, grow_central_block_position=None, grow_rotation_axis=None,
                 grow_rotation_quadrant=None, grow_neutral_color=None, pawn_drop_position=None,
                 pawn_drop_float=False, slide_position=None):
        self.type = action_type

        if self.type == "G":
            self.central_block_position = grow_central_block_position
            self.rotation_axis = grow_rotation_axis
            self.rotation_quadrant = grow_rotation_quadrant
            self.neutral_color = grow_neutral_color

        if self.type == "PD":
            self.position = pawn_drop_position
            self.float = pawn_drop_float

        if self.type == "S":
            self.position = slide_position

    def print(self):
        print(' - Action type:', self.type)
        if self.type == "G":
            if self.neutral_color:
                print(' - Color: Neutral')
            else:
                print(' - Color: Player')
            print(' - CBP:', self.central_block_position)
            if self.rotation_axis == 0:
                print(' - Rotation axis: x')
            elif self.rotation_axis == 1:
                print(' - Rotation axis: y')
            elif self.rotation_axis == 2:
                print(' - Rotation axis: z')
            print(' - Rotation quadrant:', self.rotation_quadrant)
        if self.type == "PD":
            print(' - Pawn drop position:', self.position)
        if self.type == "S":
            print(' - Slide position:', self.position)
        if self.type == "F":
            print(" - Floating")
