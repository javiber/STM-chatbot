import redis
import json
import requests

class api:
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        self.db = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)

    def search_stops(self, lat, lon):
        return self.db.execute_command("GEORADIUS stops {} {} 500 m".format(lon, lat))

    def get_pases(self, line, stop):
        response = requests.get(
            "http://www.montevideo.gub.uy/transporteRest/pasadas/{}/HABIL/{}".format(stop, line))
        return json.loads(response.content)
