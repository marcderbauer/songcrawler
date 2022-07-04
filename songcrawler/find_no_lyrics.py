import json, os, re
from types import SimpleNamespace as Namespace
from scrape import get_single_song

# TODO: integrate into __main__.py (?)

os.chdir("/home/mabs/Documents/songcrawler/songcrawler/data/WZRD") # TODO: make relative
print(os.getcwd())
for album in os.listdir(os.getcwd()): # Iterate through albums

    # Skip if not folder
    if not os.path.isdir(album):
        continue

    for songname in os.listdir(album):# Iterate through songs in given album

        # Check if format .json
        if os.path.splitext(songname)[1] != ".json": 
            continue

        # Concatenate songpath
        songpath = os.path.join(os.getcwd(), album, songname)

        # Open song and create json object
        with open(songpath) as song_file:
            song_json = json.load(song_file,object_hook=lambda d: Namespace(**d))

        # If no song lyrics, then get them
        if song_json.lyrics == None or song_json.lyrics == "":
        #try:
        #    song_json.album_name
        #except:
            print(song_json._name + "    " + song_json._uri)
            song = get_single_song(song_json._uri)
        
            # Write to file
            song_json = json.dumps(song.__dict__, indent=4)
            with open (songpath, "w") as f:
                f.write(song_json)


#TODO:
# Current Objective: find songs that do not have lyrics, then fill in lyrics
# Generally: get errors.json
# for index[1] in errors:        index[1] is uri
# get single song(scrape.py)
        
            