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
            'Authorization': f'Token {self.apikey}',
        }

        response = requests.get('https://lambda-treasure-hunt.herokuapp.com/api/adv/init/', headers=headers)
        res = response.json()
        coordinates = [int(x.strip('()')) for x in res['coordinates'].split(',')]
        sleep(res['cooldown'])
        self.world.add_room(room_id=res['room_id'],
                            title=res['title'],
                            description=res['description'],
                            elevation=res['elevation'],
                            terrain=res['terrain'],
                            available_directions=res['exits'],
                            x=coordinates[0],
                            y=coordinates[1],
                            )
        print(f'started in room {res["room_id"]}')
        return self.world.rooms[res['room_id']]

    def traverse_one(self, direction,
                     # previous_id,
                     id_predict=None,):

        if id_predict is None:
            headers = {
                'Authorization': f'Token {self.apikey}',
                'Content-Type': 'application/json',
            }

            data = "{" + f'"direction":"{direction}"' "}"

        else:
            print(id_predict)
            headers = {
                'Authorization': f'Token {self.apikey}',
                'Content-Type': 'application/json',
            }

            data = "{" + f'"direction":"{direction}","next_room_id":"{id_predict}"' + "}"

        for _ in range(5):
            try:
                response = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/adv/move/',
                                         headers=headers,
                                         data=data)
                if response.status_code == 200:
                    break
                elif response.status_code != 500:
                    print(response.status_code)
                    res1 = response.json()
                    sleep(int(res1['cooldown']) + 6)
            except requests.exceptions.RequestException as e:
                print(e)
                continue


        if response.status_code == 200:
            res = response.json()
            coordinates = [int(x.strip('()')) for x in res['coordinates'].split(',')]

            if res['room_id'] not in self.world.rooms.keys():
                self.world.add_room(room_id=res['room_id'],
                                    title=res['title'],
                                    description=res['description'],
                                    elevation=res['elevation'],
                                    terrain=res['terrain'],
                                    available_directions=res['exits'],
                                    x=coordinates[0],
                                    y=coordinates[1],
                                    )
            room = self.world.rooms[res['room_id']]
            # self.world.rooms[previous_id].connect_rooms(direction, room)
            sleep(res['cooldown'])
            print(f"travelled {direction} to room {res['room_id']}")
            return self.world.rooms[res['room_id']]

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

    def check_for_treasure(self):
        headers = {
            'Authorization': f'Token {self.apikey}',
        }

        response = requests.get('https://lambda-treasure-hunt.herokuapp.com/api/adv/init/', headers=headers)
        res = response.json()
        coordinates = [int(x.strip('()')) for x in res['coordinates'].split(',')]
        sleep(res['cooldown'])

        print(res['items'])
        return res

    def pick_up_treasure(self):
        headers = {
            'Authorization': f'Token {self.apikey}',
            'Content-Type': 'application/json',
            }

        data = '{"name":"treasure"}'

        response = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/adv/take/', headers=headers, data=data)
        res = response.json()
        sleep(res['cooldown'])
        print(f'{res["messages"]}')
        return

    def sell_treasure(self):
        headers = {
            'Authorization': f'Token {self.apikey}',
            'Content-Type': 'application/json',
            }

        data = '{"name":"treasure"}'

        response = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/adv/sell/', headers=headers, data=data)
        res = response.json()
        sleep(res['cooldown'])

        headers = {
            'Authorization': f'Token {self.apikey}',
            'Content-Type': 'application/json',
            }

        data = '{"name":"treasure", "confirm":"yes"}'

        response = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/adv/sell/', headers=headers, data=data)
        res = response.json()
        sleep(res['cooldown'])
        return

    def status_inventory(self):
        headers = {
            'Authorization': f'Token {self.apikey}',
            'Content-Type': 'application/json',
        }
        response = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/status/", headers= headers)
        res = response.json()
        sleep(res['cooldown'])
        return res