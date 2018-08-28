import json
import os
import random
import re
import sys
from urllib.request import Request
import urllib.request
from utillib import load_json
from utillib import load_list


def scrape_image(ids):
    while True:
        content = get_artworks()
        if len(content["data"]) > 0:
            break

    artwork = content["data"][random.randint(0,len(content["data"])-1)]
    while artwork["hash_id"] in ids:
        print ("Duplicate artwork.")
        artwork = content["data"][random.randint(0,len(content["data"])-1)]

    return artwork
# ---------------------- #
def get_artworks():
    categories = ["environments", "matte_painting", "mech", "storytelling", "science_fiction", "surreal"]
    sortings = ["trending", "picks"]
    
    category = categories[random.randint(0,5)]
    sorting = sortings[random.randint(0,1)]
    page = random.randint(1,10)

    try:
        request = Request("https://www.artstation.com/projects.json?category="+category+"&medium=digital2d&page="+str(page)+"&sorting="+sorting, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as err:
        print(err)
        exit()

    with response as r:
        return json.load(r)    
# ---------------------- #
def validate_image(artwork, ids, blacklist, r_dir, process_tags):
    bad_categories = ["Animation", "Architecture", "Architectural Visualization", "Comic Art", 
                        "Creatures", "Fantasy", "Game Art", "Industrial Design", 
                        "Motion Graphics", "Product Design", "Props", 
                        "Textures \u0026 Materials", "Transport \u0026 Vehicles", 
                        "Tutorial", "User Interface", "Visual Effects", 
                        "Weapons", "Whimsical"]

    # load the artwork's .json
    request = Request("https://www.artstation.com/projects/" + artwork["hash_id"] + ".json", headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(request)   

    with response as r:
        info = json.load(r)    

    for category in info["categories"]:
        if category["name"] in bad_categories:

            _file = open(r_dir+"permalinks.txt", "a")
            _file.write(artwork["permalink"] + "\n")

            title = re.sub('[^A-Za-z0-9]+', '_', artwork["title"].lower())
            urllib.request.urlretrieve(info["assets"][0]["image_url"], r_dir + title + ".jpg")

            if process_tags: 
                add_tags("./output/bad_tags", info)

            ids[artwork["hash_id"]] = artwork["id"]

            print ("Bad artwork.")

            return False    

    if info["adult_content"]:
        ids[artwork["hash_id"]] = artwork["id"]

        _file = open(r_dir+"permalinks.txt", "a")
        _file.write(artwork["permalink"] + "\n")

        title = re.sub('[^A-Za-z0-9]+', '_', artwork["title"].lower())
        urllib.request.urlretrieve(info["assets"][0]["image_url"], r_dir + title + ".jpg")

        print ("Bad artwork.")
        return False

    tags = get_tags(info)

    for tag in tags:
        if tag in blacklist:
            ids[artwork["hash_id"]] = artwork["id"]

            _file = open(r_dir+"permalinks.txt", "a")
            _file.write(artwork["permalink"] + "\n")

            title = re.sub('[^A-Za-z0-9]+', '_', artwork["title"].lower())
            urllib.request.urlretrieve(info["assets"][0]["image_url"], r_dir + title + ".jpg")

            if process_tags: 
                add_tags("./output/bad_tags", info)

            print ("Bad artwork.")
            return False

    print("Artwork validated.")
    return True
# ---------------------- #
def add_download_opener():
    opener=urllib.request.build_opener()
    opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
    urllib.request.install_opener(opener)
# ---------------------- # 
def get_tags(artinfo):
    return [tag.lower().strip('#') for tag in artinfo["tags"]]
# ---------------------- # 
def add_tags(filename, artinfo):
    j_tags = load_json(filename)
    
    # get the tags
    a_tags = [tag.lower().strip('#') for tag in artinfo["tags"]]

    for tag in a_tags:
        if tag in j_tags:
            j_tags[tag] += 1
        else:
            j_tags[tag] = 1

    with open (filename+".json", "w") as f:
        json.dump(j_tags, f, indent=4, sort_keys=True) 
# ---------------------- #
def parse_tags(filename, threshold):
    tags = load_json(filename)

    _file = open(filename+".txt", "a")

    for tag in tags:
        if tags[tag] >= threshold:
            _file.write(tag + "\n")

    _file.close() 