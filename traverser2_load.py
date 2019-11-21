from util import Queue, Stack
from world_graph import Room, World
from communication import Calls
from decouple import config
from time import sleep, time
import random


class Traverser:
    starting_room: Room
    world: World

    def __init__(self, world, visited, path):
        self.world = world
        self.calls = Calls(world=self.world)
        self.visited = visited
        self.world.add_starting_room(self.calls.initialize_with_api())
        self.starting_room = self.world.start_room
        self.path = path
        self.apikey = config("APIKEY")

        self.current_room_id = self.starting_room.room_id

    def go(self):
        reverse = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}
        start = True
        self.current_room_id = self.starting_room.room_id
        current_room = self.starting_room
        self.visited.add(self.starting_room.room_id)


        while len(self.visited) < 500:
            current_room : Room
            if start:
                self.traverse_all_connections(self.starting_room)
                open_doors = self.starting_room.get_exits()
                next_dir = open_doors.pop()
                current_room = self.calls.traverse_one(direction=next_dir,
                                                       previous_id=current_room.room_id,
                                                       id_predict=current_room.getRoomInDirection(next_dir).room_id)
                start = False
            else:
                if next_dir not in current_room.get_exits():
                    self.traverse_all_connections(current_room)
                current_room = self.calls.traverse_one(direction=next_dir,
                                                       previous_id=current_room.room_id,
                                                       id_predict=current_room.getRoomInDirection(next_dir).room_id)
            if current_room.room_id not in self.visited:
                print(f"current room {current_room.room_id} not in visited")
                print(self.visited)
                open_doors = current_room.available_directions.copy()
                self.visited.add(current_room.room_id)
                self.path.append(next_dir)
                if len(self.visited) == 500:
                    return self.path
                elif len(current_room.available_directions) > 1:
                    next_dir = open_doors.pop()
                    current_room.traveled_directions.add(next_dir)
                elif len(current_room.available_directions) == 1:
                    next_dir = current_room.available_directions[0]
                else:
                    print("Error!")
            else:
                print('room in visited')
                if len(current_room.available_directions) > 1:
                    print('nv, condition 1')
                    found_dir = False
                    for d in current_room.available_directions:
                        if current_room.getRoomInDirection(d) is not None:
                            room_in_d = current_room.getRoomInDirection(d).room_id
                        else:
                            room_in_d = None
                        if (room_in_d is not None) or (room_in_d not in self.visited):
                            next_dir = d
                            current_room.traveled_directions.add(d)
                            found_dir = True
                            break
                    if not found_dir:
                        print("didn't find any unvisited")
                        path_back = self.path_to_closest_unvisited(current_room)
                        for d in path_back[:-1]:
                            print(f"traversing path back, current room: {current_room.room_id}")
                            print(f"travelling in direction {d}")
                            current_room = self.calls.traverse_one(direction=d,
                                                                previous_id=current_room.room_id,
                                                                id_predict=current_room.getRoomInDirection(d).room_id)
                        next_dir = path_back[-1]

                elif len(current_room.available_directions) == 1:
                    print("nv, condition 2. reversing one room")
                    next_dir = current_room.available_directions[0]
                    print(f"current room: {current_room.room_id}")
                    print(f"going in direction: {next_dir}")
                    current_room.traveled_directions.add(next_dir)
                    # current_room = self.calls.traverse_one(direction=next_dir,
                    #                                     previous_id=current_room.room_id,
                    #                                     id_predict=current_room.getRoomInDirection(next_dir).room_id)


            print(f"next direction: {next_dir}")
            print('fin loop')
        return self.path

    def path_to_closest_unvisited(self, starting_room):
        print('called get closest')
        current_room: Room
        queue = Queue()
        paths = []
        visited_local = set()
        queue.enqueue(starting_room)
        current_path = []

        start = True

        while queue.size() > 0:
            if not start:
                current_path = queue.dequeue()
                current_room = starting_room
                for d in current_path:
                    current_room = current_room.getRoomInDirection(d)
                    if current_room == None:
                        return current_path
            else:
                current_room = queue.dequeue()
                start = False
            open_doors = current_room.available_directions.copy()

            if current_room.room_id not in visited_local:

                if ((current_room.room_id not in self.visited)
                        or len(self.visited.union(visited_local)) == 500):

                    visited_local.add(current_room.room_id)
                    paths.append(current_path)
                    print(f"returned {current_path}")
                    return current_path

                else:
                    visited_local.add(current_room.room_id)
                    for next_room in open_doors:
                        cpath_copy = current_path.copy()
                        cpath_copy.append(next_room)
                        queue.enqueue(cpath_copy)
            print('fin loop')
            print(paths)
        return paths.pop()


    def traverse_all_connections(self, room):
        checked_room: Room

        reverse = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}
        cur_rmid = room.room_id
        print('called traverse all dirs')
        print(f'available: {room.available_directions}')
        remaining_dirs_for_room = []
        for d in room.available_directions:
            if room.getRoomInDirection(d) is None:
                checked_room = self.calls.traverse_one(direction=d,
                                                        previous_id=cur_rmid)

                checked_room.connect_rooms(reverse[d], room)

                self.calls.traverse_one(direction=reverse[d],
                                        previous_id=checked_room.room_id,
                                        id_predict=cur_rmid)
                room.connect_rooms(d, checked_room)

                remaining_dirs_for_room.append(d)
            print(remaining_dirs_for_room)
        return remaining_dirs_for_room


