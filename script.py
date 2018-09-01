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

### main ###
def main():
    gcounter = 1
    rcounter = 1
    process_tags = False
    parse_tags = False
    blacklist = load_list(output_dir+"blacklist")
    
    while True:
        artwork = scrape_image(ids)
        valid, info = validate_image(artwork, ids, blacklist, r_dir, rcounter, process_tags) 
        while not valid:
            rcounter+=1
            artwork = scrape_image(ids)
            valid, info = validate_image(artwork, ids, blacklist, r_dir, rcounter, process_tags) 

        with open(a_dir + "permalinks.txt", 'a') as f:
            f.write(artwork["permalink"] + "\n")

        download_artwork(info, a_dir, gcounter, ids)
        gcounter+=1

        if process_tags:
            add_tags(output_dir+"good_tags", info)
        
        sleep(5)

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