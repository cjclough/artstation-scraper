import string
from scrape_api import *
from utillib import *
from time import sleep

### setup ###

run_dir = input("Enter name of test directory: ")
# make directories 
main_dir = ("./tests/"+run_dir+"/")
a_dir = make_dir(main_dir+"accepted/")
r_dir = make_dir(main_dir+"rejected/")
output_dir = make_dir("./output/")
ids = load_json(output_dir+"scraped")
add_download_opener()

### main ###
def main():
    counter = 1
    process_tags = False
    parse_tags = False
    blacklist = load_list(output_dir+"blacklist")
    
    while True:
        valid = False
        while not valid:
            artwork = scrape_image(ids)
            valid, info = validate_image(artwork, ids, blacklist, r_dir, process_tags) 

        with open(a_dir + "permalinks.txt", 'a') as f:
            f.write(artwork["permalink"] + "\n")

        artist = re.sub('[^A-Za-z0-9]+', '_', info["user"]["full_name"].lower())
        title = re.sub('[^A-Za-z0-9]+', '_', info["title"].lower())
        urllib.request.urlretrieve(info["assets"][0]["image_url"], a_dir+str(counter)+"_"+artist+"-"+title+".jpg")
        counter += 1

        ids[artwork["hash_id"]] = artwork["id"]
        
        if process_tags:
            add_tags(output_dir+"good_tags", info)
        
        sleep(500)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Terminating...")

        with open(output_dir+"scraped.json", 'w') as f:
            json.dump(ids, f, indent= 4, sort_keys=True)

        if parse_tags:
            parse_tags(output_dir+"bad_tags", 3)
            parse_tags(output_dir+"good_tags", 7)

        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)