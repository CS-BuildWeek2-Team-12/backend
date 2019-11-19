class Room:
    def __init__(self, room_id):
        self.room_id = room_id
        self.title = None
        self.description = None
        self.elevation = None
        self.terrain = None
        self.available_directions = []
        self.traveled_directions = []
        self.n_to = None
        self.s_to = None
        self.e_to = None
        self.w_to = None
        self.x = None
        self.y = None

    def __str__(self):
        return f"\n-----------------\n\n{self.title}, id num: {self.room_id}" \
               f"\n\n {self.description}\n\n  {self.get_exits_str}"

    def get_exits(self):
        exits = []
        if self.n_to is not None:
            exits.append('n')
        if self.s_to is not None:
            exits.append('s')
        if self.e_to is not None:
            exits.append('e')
        if self.w_to is not None:
            exits.append('w')
        return exits

    def get_exits_str(self):
        return f"Exits in directions: [{' ,'.join(self.get_exits())}]"

    def connect_rooms(self, direction, room):
        if direction == 'n':
            self.n_to = room
            room.s_to = self
        elif direction == 's':
            self.s_to = room
            room.n_to = self
        elif direction == 'e':
            self.e_to = room
            room.w_to = self
        elif direction == 'w':
            self.w_to = room
            room.e_to = self
        else:
            print("Invalid Connection")
        return None

    def getRoomInDirection(self, direction):
        ddict = {'n': 'n_to', 's': 's_to', 'e': 'e_to', 'w': 'w_to'}

        if getattr(self, ddict[direction]) is not None:
            return getattr(self, ddict[direction])
        else:
            if direction in self.available_directions:
                #traverse
                print('add functionality')
                return 'add functionality'
            else:
                return None

    def get_xy(self):
        return [self.x, self.y]

class World:

    def __init__(self, start_room):
        self.start_room = start_room
        self.rooms = {}
        self.room_grid = []
        self.grid_size = 0

    def add_room(self, room_id, title, description, elevation, terrain, available_directions, x, y):
        room = Room(room_id=room_id)
        room.title = title
        room.description = description
        room.elevation = elevation
        room.terrain = terrain
        room.available_directions = available_directions
        room.x = x
        room.y = y


    def generate_grid(self):
        return 'add functionality'