import os
import json
import string

from process import combine_json_dir_to_csv, song_statistics, combine_csvs, object_decoder
from scrape import crawl_songs, Song, find_missing_lyrics, Error

input_artist_uri = 'spotify:artist:0fA0VVWsXO9YnASrzqfmYu'

# Crawl Songs, return artist path
(input_artist_path, artist_name) = crawl_songs(input_artist_uri, overwrite=False, get_lyrics=True, regex_filter="edit(ed)?|clean")
find_missing_lyrics(artist_name)

lyrics_path = os.path.join(input_artist_path, "lyrics")

# TODO: Create folder for additional info
# Check if album path exists
word_info_path = os.path.join(input_artist_path,"word_info")
if not os.path.exists(word_info_path):
        print("Folder %s does not exist, creating folder..." % word_info_path)
        try:
            os.mkdir(word_info_path)
        except OSError:
            # TODO: Implement Errors
            #error = Error("AlbumCreationError", word_song_info_path, album.uri)
            #errors_all.append(error)
            print ("Creation of the directory %s failed" % word_info_path)
        else:
            print ("Successfully created the directory %s \n " % word_info_path)
else:
    print(word_info_path + " exists")
    # TODO: ask if overwrite fine?
    ##if overwrite == True:
    #    pass
    #else:
    #    print("skipping album")
    #    continue

for album in os.listdir(input_artist_path):
    
    # Set current album directory
    album_dir = os.path.join(input_artist_path, album)

    # Skip non-albums
    if album == "lyrics" or album == "lyrics_statistics" or album == "word_info":
        continue
    if not os.path.isdir(album_dir):
        continue
    print("\n\nALBUM: " + album)

    # Create additional info album path
    word_info_path_album = os.path.join(word_info_path, album)
    if not os.path.exists(word_info_path_album):
        print("Folder %s does not exist, creating folder..." % word_info_path_album)
        try:
            os.mkdir(word_info_path_album)
        except OSError:
            print ("Creation of the directory %s failed" % word_info_path_album)
        else:
            print ("Successfully created the directory %s \n " % word_info_path_album)
    else:
        print(word_info_path_album + " exists")
        continue

    #TODO: Open album lyrics file
    
    with open (os.path.join(lyrics_path,(album + ".json")), "r+") as album_lyrics_all_file:
        album_lyrics_all = json.load(album_lyrics_all_file)
    #album_lyrics_all_file = os.path.join(lyrics_path,(album + ".json"))

    for song_listed in os.listdir(album_dir):
        if os.path.splitext(song_listed)[1] == ".json": 
            song_path = os.path.join(album_dir, song_listed)
            
            # Process Song
            with open (song_path, "r") as song_json: 

                # Load Song
                
                song = json.load(song_json ,object_hook=object_decoder)
                # Get Song Statistics
                song, word_info_song = song_statistics(song, album_lyrics_all[song.name]) #return anything?
                
                # Write additional info
                word_info_path_song = os.path.join(word_info_path_album, (song.name + ".json")) 
                word_info_song_json = json.dumps(word_info_song, indent=4)
                try:
                    with open(word_info_path_song, "w" ) as song_file:
                        song_file.write(word_info_song_json)
                except:
                    # Try with out punctuation
                    song_name_simplified = song.name.translate(str.maketrans('', '', string.punctuation))
                    word_info_path_song = os.path.join(word_info_path_album, (song_name_simplified + ".json")) 
                    with open(word_info_path_song, "w" ) as song_file:
                        song_file.write(word_info_song_json)

            # Write to file
            song.to_json(song_path)

            print("SONG: " + song.name)
        
    combine_json_dir_to_csv(album_dir, overwrite=True)

combine_csvs(input_artist_path)

######################################
#    _______ ____  _____   ____      # 
#   |__   __/ __ \|  __ \ / __ \     # 
#      | | | |  | | |  | | |  | |    # 
#      | | | |  | | |  | | |  | |    # 
#      | | | |__| | |__| | |__| |    # 
#      |_|  \____/|_____/ \____/     #
#                                    #
######################################  

# Folder structure is now completely different
# Song doesn't include lyrics anymore. Lyrics are all in one folder now

# Iterate through lyrics folder
# For every song (dict: song,lyric):
#   process as before
#   create a new folder? make structure as with albums but with just the processed info?
#   => Call it lyrics_statistics
#   honestly not sure yet, I'll give it some time to think about it

# TODO: Make matching of Songname and songfile name more forgiving
#       fuzzy matching?
#       example: In Lyrics File: "Flight at First Sight/Advanced"
#                In Folder:      "Flight at First SightAdvanced"
#       Also mismatch for upper and lowercase
#       USE TRY/EXCEPT? TRY NORMAL, EXCEPT with the same translations as when saving the song