import redis
import json
from pyproj import Proj, transform
r = redis.StrictRedis(host='localhost', port=6379, db=0)
command = "GEOADD stops "
with open("stops.json") as f:
    data = json.load(f)
    stops = data["features"]

outProj = Proj(init='epsg:4326')
inProj = Proj(init='epsg:32721')
for stop in stops:
    bad_lat, bad_lon = stop["geometry"]["coordinates"]
    lat, lon = transform(inProj, outProj, bad_lat, bad_lon)
    command += "{} {} {} ".format(lat, lon, stop["properties"]["COD_UBIC_P"])

r.execute_command(command.strip())
