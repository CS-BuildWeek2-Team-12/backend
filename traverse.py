from util import Queue, Stack
from world_graph import Room, World
from decouple import config
import requests

class Traverser:

    def __init__(self, world: World, starting_room, apikey=config("APIKEY")):
        self.world = world
        self.visited = set()
        self.starting_room = starting_room
        self.path = []
        self.apikey = apikey


    def go(self):
        reverse = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}
        start = True

        while len(self.visited) < 500:
            if start:
                open_doors = self.starting_room.available_directions
                next_dir = open_doors.pop()
                ceop = self.starting_room
                current_room =

    def initialize_with_api(self):
        headers = {
            'Authorization': 'Token 7a375b52bdc410eebbc878ed3e58b2e94a8cb607',
        }

        response = requests.get('https://lambda-treasure-hunt.herokuapp.com/api/adv/init/', headers=headers)
        res = response.json()
        coordinates = [int(x.strip('()')) for x in res['coordinates'].split(',')]

        self.world.add_room(room_id=res['room_id'],
                            title=res['title'],
                            description=res['description'],
                            elevation=res['elevation'],
                            terrain=res['terrain'],
                            available_directions=res['exits'],
                            x=coordinates[0],
                            y=coordinates[1],
                            )

    def traverse_one(self, direction):
        headers = {
            'Authorization': f'Token {self.apikey}',
            'Content-Type': 'application/json',
        }

        data = "{" + f'"direction":"{direction}"' "}"

        response = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/adv/move/', headers=headers, data=data)
        res = response.json()
        coordinates = [int(x.strip('()')) for x in res['coordinates'].split(',')]

        self.world.add_room(room_id=res['room_id'],
                            title=res['title'],
                            description=res['description'],
                            elevation=res['elevation'],
                            terrain=res['terrain'],
                            available_directions=res['exits'],
                            x=coordinates[0],
                            y=coordinates[1],
                            )