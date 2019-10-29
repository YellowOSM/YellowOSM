# coding: utf-8
# Find Geo-Coordinates of Cities based on OSM Data
#
# converted from an JupyterNotebook


import csv
import sys
import pandas as pd
import numpy as np
import json


def check_coords(cities):
    for city in cities:
        x, y = city["x"], city["y"]
        yield "https://yellowosm.com/map/14/{}/{}#{}".format(x, y, city["name"])


csv.field_size_limit(sys.maxsize)
labels = []
# read data from dump.osm
with open("dump.osm", newline="") as f:
    reader = csv.reader(f, delimiter=",", quotechar='"')
    for line in reader:
        if not line[6]:
            continue
        else:
            labels.append([line[1], line[2], line[6]])


data = pd.DataFrame(labels, columns=["y", "x", "city"], dtype=float)


if not np.array_equal(data.x, data.x.astype(float)):
    print("we have a problem!")


groups = data.groupby("city")
len(groups.get_group("Graz"))

cities = {}
for name, group in groups:
    if len(group) > 5:
        # print(name)
        max_x = group["x"].agg(np.max)
        min_x = group["x"].agg(np.min)
        max_y = group["y"].agg(np.max)
        min_y = group["y"].agg(np.min)
        cities[name.lower()] = {
            "name": name,
            "x": group["x"].agg(np.mean),
            "y": group["y"].agg(np.mean),
            "stddev_x": group["x"].agg(np.std),
            "stddev_y": group["y"].agg(np.std),
            #             "min_x": min_x,
            #             "min_y": min_x,
            #             "max_x": max_x,
            #             "max_y": max_y,
            "bb": (max_x, min_y, min_x, max_y),
        }


# test
for city in ["Graz", "Stuttgart", "Bregenz", "Berlin", "Frankfurt am Main", "Wien"]:
    print(next(check_coords([cities[city.lower()]])))
    print(cities[city.lower()])


with open("data/cities_bb.json", "w") as f:
    f.write(json.dumps(cities))
