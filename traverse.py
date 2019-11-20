from typing import Any, Union

from util import Queue, Stack
from world_graph import Room, World
from communication import Calls
from decouple import config
from time import sleep, time
import requests


class Traverser:

    starting_room: Room
    world: World

    def __init__(self, world, apikey=config("APIKEY")):
        self.world = world
        self.calls = Calls(world=self.world)
        self.visited = set()
        self.starting_room = self.calls.initialize_with_api()
        self.path = []
        self.apikey = apikey
        self.stack = Stack()

        self.current_room_id = self.starting_room.room_id

    def go(self):
        reverse = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}
        start = True
        self.current_room_id = self.starting_room.room_id
        current_room = self.starting_room

        while len(self.visited) < 500:
            if start:
                open_doors = self.starting_room.available_directions
                next_dir = open_doors.pop()
                ceop = self.starting_room
                current_room = self.calls.traverse_one(direction=next_dir)
                ceop.connect_rooms(next_dir, current_room)
                start = False
            elif next_dir in current_room.traveled_directions:
                id_next = current_room.getRoomInDirection(next_dir).room_id
                prev_room = current_room
                current_room = self.calls.traverse_one(next_dir)
                ceop = self.starting_room
                for d in self.path:
                    ceop = ceop.getRoomInDirection(d)
            else:
                id_next = current_room.getRoomInDirection(next_dir).room_id
                prev_room = current_room
                current_room = self.calls.traverse_one(next_dir)
                prev_room.connect_rooms(next_dir, current_room)
                ceop = self.starting_room
                for d in self.path:
                    ceop = ceop.getRoomInDirection(d)

            if current_room not in self.visited:
                current_room: Room
                open_doors = current_room.get_exits()
                self.visited.add(current_room)
                self.path.append(next_dir)
                if len(self.visited) == 500:
                    return self.path
                elif len(current_room.available_directions) > 1:
                    next_dir = open_doors.pop()
                elif len(current_room.available_directions) == 1:
                    path_back = self.path_to_closest_unvisited(current_room)
                    for d in path_back[:-1]:
                        if current_room.getRoomInDirection(d) is not None:
                            current_room = self.calls.traverse_one(d, current_room.getRoomInDirection(d).room_id)
                            self.path.append(d)
                        else:
                            current_room = self.calls.traverse_one(d)
                            self.path.append(d)

                    next_dir = path_back[-1]
                else:
                    print("Error")
            else:
                if (len(current_room.get_exits()) > 1) & (len(open_doors) > 0):
                    # if current room is has been traversed
                    current_room = self.calls.traverse_one(reverse[next_dir])
                    next_dir = open_doors.pop()
                elif len(open_doors) == 0:
                    path_back = self.path_to_closest_unvisited(current_room)
                    current_room = self.calls.traverse_one(reverse[next_dir])
                    for d in path_back[:-1]:
                        if current_room.getRoomInDirection(d) is not None:
                            current_room = self.calls.traverse_one(d, current_room.getRoomInDirection(d).room_id)
                            self.path.append(d)
                        else:
                            current_room = self.calls.traverse_one(d)
                            self.path.append(d)
                    next_dir = path_back[-1]
        return self.path

    def path_to_closest_unvisited(self, starting_room):
        queue = Queue()
        paths = []
        visited_local = set()
        queue.enqueue(starting_room)
        current_room: Room

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
            open_doors = current_room.get_exits()
            if current_room not in visited_local:
                if (len(current_room.traveled_directions) < len(current_room.available_directions) or
                        (len(self.visited.union(visited_local)) == 500)):
                    visited_local.add(current_room)
                    not_travelled = set(current_room.traveled_directions) - set(current_room.available_directions)
                    current_path.append(not_travelled.pop())
                    paths.append(current_path)
                    return current_path
                else:
                    visited_local.add(current_room)
                    for next_room in open_doors:
                        cpath_copy = current_path.copy()
                        cpath_copy.append(next_room)
                        queue.enqueue(cpath_copy)
        return min(paths)


    # def initialize_with_api(self):
    #     headers = {
    #         'Authorization': f'Token {self.apikey}',
    #     }
    #
    #     response = requests.get('https://lambda-treasure-hunt.herokuapp.com/api/adv/init/', headers=headers)
    #     res = response.json()
    #     coordinates = [int(x.strip('()')) for x in res['coordinates'].split(',')]
    #
    #     self.world.add_room(room_id=res['room_id'],
    #                         title=res['title'],
    #                         description=res['description'],
    #                         elevation=res['elevation'],
    #                         terrain=res['terrain'],
    #                         available_directions=res['exits'],
    #                         x=coordinates[0],
    #                         y=coordinates[1],
    #                         )
    #
    # def traverse_one(self, direction, id_predict=None):
    #
    #     if id_predict is None:
    #         headers = {
    #             'Authorization': f'Token {self.apikey}',
    #             'Content-Type': 'application/json',
    #         }
    #
    #         data = "{" + f'"direction":"{direction}"' "}"
    #
    #     else:
    #         headers = {
    #             'Authorization': f'Token {self.apikey}',
    #             'Content-Type': 'application/json',
    #         }
    #
    #         data = "{" + f'"direction":"{direction}","next_room_id":"{id_predict}' "}"
    #
    #     response = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/adv/move/',
    #                              headers=headers,
    #                              data=data)
    #
    #     if response.status_code == 200:
    #         res = response.json()
    #         coordinates = [int(x.strip('()')) for x in res['coordinates'].split(',')]
    #
    #         self.world.add_room(room_id=res['room_id'],
    #                             title=res['title'],
    #                             description=res['description'],
    #                             elevation=res['elevation'],
    #                             terrain=res['terrain'],
    #                             available_directions=res['exits'],
    #                             x=coordinates[0],
    #                             y=coordinates[1],
    #                             )
    #         sleep(res['cooldown'])
    #         return self.world.last_added_room_obj
    #
    #     elif response.status_code == 400:
    #         res = response.json()
    #         sleep(res['cooldown'] + 10)
    #         return "Too Slow"
    #     elif response.status_code == 500:
    #         print('500 error')
    #         return False
    #     else:
    #         print(f"There was another error {response.status_code}")
    #         return False
