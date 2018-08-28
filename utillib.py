import json
import os
import string

def make_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)
    
    return d
# ---------------------- #
def load_json(filename):
    if not os.path.isfile(filename+".json"):
        _file = open(filename+".json", "w")
        _file.write("{}")
        _file.close()

    with open(filename+".json") as f:
        return json.load(f)
# ---------------------- #
def load_list(filename):
    if not os.path.isfile(filename+".txt"):
        _file = open(filename+".txt", "a")
        _file.close()

    with open(filename+".txt") as f:
        _list = f.readlines()
        
    return [x.strip() for x in _list] 