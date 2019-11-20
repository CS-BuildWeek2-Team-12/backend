from decouple import config
from world_graph import World, Room
from time import time, sleep
import requests


class Calls:
    def __init__(self,
                 world: World,
                 apikey=config('APIKEY')
                 ):
        self.apikey = apikey
        self.world = world

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
        return self.world.last_added_room_obj

    def traverse_one(self, direction, id_predict=None):

        if id_predict is None:
            headers = {
                'Authorization': f'Token {self.apikey}',
                'Content-Type': 'application/json',
            }

            data = "{" + f'"direction":"{direction}"' "}"

        else:
            headers = {
                'Authorization': f'Token {self.apikey}',
                'Content-Type': 'application/json',
            }

            data = "{" + f'"direction":"{direction}","next_room_id":"{id_predict}' "}"

        response = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/adv/move/',
                                 headers=headers,
                                 data=data)

        if response.status_code == 200:
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
            sleep(res['cooldown'])
            return self.world.last_added_room_obj

        elif response.status_code == 400:
            res = response.json()
            sleep(res['cooldown'] + 10)
            return "Too Slow"
        elif response.status_code == 500:
            print('500 error')
            return False
        else:
            print(f"There was another error {response.status_code}")
            return False
