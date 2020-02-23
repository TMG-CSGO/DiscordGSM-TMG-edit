import json
from enum import Enum
from bin import *

# load servers.json -> get all servers type, addr, port
class Servers:
    def __init__(self):
        self.refresh()

    # refresh query server list
    def refresh(self):
        self.servers = self.load()

    # get servers data
    def load(self):
        with open('configs/servers.json', 'r') as file:
            data = file.read()

        return json.loads(data)

    # add a server
    def add(self, type, game, addr, port, channel):
        data = {}
        data['type'], data['game'] = type, game
        data['addr'], data['port'] = addr, int(port)
        data['channel'] = int(channel)

        servers = self.load()
        servers.append(data)

        with open('configs/servers.json', 'w', encoding='utf8') as file:
            json.dump(servers, file, ensure_ascii=False, indent=4)

    # delete a server by id
    def delete(self, id):
        servers = self.load()
        if 0 < int(id) <= len(servers):
            del servers[int(id) - 1]

            with open('configs/servers.json', 'w', encoding='utf8') as file:
                json.dump(servers, file, ensure_ascii=False, indent=4)
            
            return True
        return False

    # save the servers query data to cache/
    def query(self):
        for server in self.servers:
            if server['type'] == 'SourceQuery':
                query = SourceQuery(str(server['addr']), int(server['port']))
                result = query.getInfo()

                server_cache = ServerCache(server['addr'], server['port'])

                if result:
                    server_cache.set_status('Online')
                    server_cache.save_data(server['game'], result['GamePort'], result['Hostname'], result['Map'], result['MaxPlayers'], result['Players'], result['Bots'])
                else:
                    server_cache.set_status('Offline')

# Game Server Data
class ServerCache:
    def __init__(self, addr, port):
        self.addr, self.port = addr, port
        self.file_name = addr.replace(':', '.') + '-' + str(port)
        self.file_name = "".join(i for i in self.file_name if i not in "\/:*?<>|")

    def get_status(self):
        with open(f'cache/{self.file_name}-status.txt', 'r', encoding='utf8') as file:
            return file.read()

    def set_status(self, status):
        with open(f'cache/{self.file_name}-status.txt', 'w', encoding='utf8') as file:
            file.write(str(status))

    def get_data(self):
        try:
            with open(f'cache/{self.file_name}.json', 'r', encoding='utf8') as file:
                return json.load(file)
        except EnvironmentError:
            return False

    def save_data(self, game, gameport, name, map, maxplayers, players, bots):
        data = {}

        # save game name, ip address, query port
        data['game'], data['addr'], data['port'] = game, self.addr, gameport

        # save server name, map name, max players count
        data['name'], data['map'], data['maxplayers'] = name, map, maxplayers

        # save current players count, bots count
        data['players'], data['bots'] = players, bots

        with open(f'cache/{self.file_name}.json', 'w', encoding='utf8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)