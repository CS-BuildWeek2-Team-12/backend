from world_graph import World, Room
from communication import Calls
from util import Queue
from random import choice


def find_treasure(world: World):

    current_room: Room

    calls = Calls(world=world)
    res = calls.check_for_treasure()
    current_room = world.rooms[int(res['room_id'])]

    directions = current_room.get_exits()
    for item in res['items']:
        if 'treasure' in item:
            calls.pick_up_treasure()

    status_inventory = calls.status_inventory()

    while len(status_inventory['inventory']) < 9:
        d = choice(directions)
        room_id_next = current_room.getRoomInDirection(d).room_id
        calls.traverse_one(direction=d,
                            previous_id=current_room.room_id,
                            id_predict=room_id_next)
        res = calls.check_for_treasure()
        current_room = world.rooms[int(res['room_id'])]

        directions = current_room.get_exits()
        if len(res['items']) > 0:
            for item in res['items']:
                if 'treasure' in item:
                    calls.pick_up_treasure()
        status_inventory = calls.status_inventory()

    status_inventory = calls.status_inventory()

    path = path_to_room(current_room, world.rooms[1])
    print(path)
    for d in path:
        print(d)
        rn_l = current_room.getRoomInDirection(d).room_id
        print(rn_l)
        current_room = calls.traverse_one(d, world.rooms[rn_l].room_id)
    res = calls.check_for_treasure()
    if res['room_id'] == '1':
        for tr in status_inventory['inventory']:
            calls.sell_treasure()








def path_to_room(starting_room, target=None):
    # print(f"ptcu called, curpath: {self.path} from {target}")
    queue = Queue()
    paths = []
    visited_local = set()
    queue.enqueue(starting_room)

    start = True

    while queue.size() > 0:
        if not start:
            current_path = queue.dequeue()
            current_room = starting_room
            for d in current_path:
                current_room = current_room.getRoomInDirection(direction=d)
        else:
            current_path = []
            current_room = queue.dequeue()
            start = False
        # print(current_path)
        open_doors = current_room.get_exits()
        if current_room not in visited_local:
            # print(f"cr id: {current_room.id}, cp: {current_path}")
            if current_room == target:
                # print(f"got uv room: {current_path}")
                visited_local.add(current_room)
                paths.append(current_path)
                return current_path
            else:
                # if (len(open_doors) < 2 and
                #         current_room.getRoomInDirection(open_doors[0]) is not prev_room):
                #     visited_local.add(current_room)
                # else:
                visited_local.add(current_room)
                for next_room in open_doors:
                    cpath_copy = current_path.copy()
                    cpath_copy.append(next_room)
                    queue.enqueue(cpath_copy)
    # print(f"final paths: {paths}")
    return min(paths)
