import json
import os
import random
import re
import requests
import shutil
import sys
from utillib import load_json
from utillib import load_list

rcounter = 1

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
    sortings = ["&sorting=trending", "&sorting=picks", "&randomize=true"]
    
    category = categories[random.randint(0,5)]
    sorting = sortings[random.randint(0,2)]
    page = random.randint(1,10)

    try:
        response = requests.get("https://www.artstation.com/projects.json?category="+category+"&medium=digital2d&page="+str(page)+sorting)
    except requests.HTTPError as err:
        print(err)
        exit()  

    return response.json()
# ---------------------- #
def validate_image(artwork, ids, greenlist, blacklist, r_dir, rcounter, process_tags):
    bad_categories = ["Animation", "Architecture", "Architectural Visualization", "Comic Art", 
                        "Creatures", "Fantasy", "Game Art", "Industrial Design", 
                        "Motion Graphics", "Product Design", "Props", 
                        "Textures \u0026 Materials", "Transport \u0026 Vehicles", 
                        "Tutorial", "User Interface", "Visual Effects", "Whimsical"]

    # load the artwork's .json
    response = requests.get("https://www.artstation.com/projects/" + artwork["hash_id"] + ".json") 
    info = response.json()

    tags = get_tags(info)

    for tag in tags:
        if tag in greenlist:
            print("Artwork validated.")
            return True, info

    for category in info["categories"]:
        if category["name"] in bad_categories:
            
            download_artwork(info, r_dir, rcounter, ids)

            if process_tags: 
                add_tags("./output/bad_tags", info)

            print ("Bad artwork.")
            return False, info    

    if info["adult_content"]:
        download_artwork(info, r_dir, rcounter, ids)
        rcounter+=1

        print ("Bad artwork.")
        return False, info

    for tag in tags:
        if tag in blacklist:
            download_artwork(info, r_dir, rcounter, ids)

            if process_tags: 
                add_tags("./output/bad_tags", info)

            print ("Bad artwork.")
            return False, info

    print("Artwork validated.")
    return True, info
# ---------------------- #
def download_artwork(info, directory, counter, ids):
        ids[info["hash_id"]] = info["id"]

        _file = open(directory+"permalinks.txt", "a")
        _file.write(info["permalink"] + "\n")

        response = requests.get(info["assets"][0]["image_url"], stream=True)

        title = re.sub('[^A-Za-z0-9]+', '_', info["title"].lower())
        artist = re.sub('[^A-Za-z0-9]+', '_', info["user"]["full_name"].lower())
        
        with open(directory+str(counter)+"_"+artist+"-"+title+".jpg", "wb") as dl:
            shutil.copyfileobj(response.raw, dl)
# ---------------------- # 
def get_tags(artinfo):
    return [tag.lower().strip('#') for tag in artinfo["tags"]]
# ---------------------- # 
def add_tags(filename, artinfo):
    j_tags = load_json(filename)
    
    # get the tags
    a_tags = get_tags(artinfo)

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