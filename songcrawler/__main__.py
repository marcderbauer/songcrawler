import os
import json

from process import combine_json_dir_to_csv, song_statistics, combine_csvs, object_decoder
from scrape import crawl_songs, Song, find_missing_lyrics

input_artist_uri = 'spotify:artist:5RADpgYLOuS2ZxDq7ggYYH'

# Crawl Songs, return artist path
(input_artist_path, artist_name) = crawl_songs(input_artist_uri, overwrite=True, get_lyrics=True, regex_filter="edit(ed)?|clean")
find_missing_lyrics(artist_name)

for album in os.listdir(input_artist_path):
    
    album_dir = os.path.join(input_artist_path, album)
    if not os.path.isdir(album_dir):
        continue
    print("\n\nALBUM: " + album)

    for song in os.listdir(album_dir):
        if os.path.splitext(song)[1] == ".json": 
            song_path = os.path.join(album_dir, song)
            
            # Process Song
            with open (song_path, "r") as song_json: 

                # Load Song
                song = json.load(song_json ,object_hook=object_decoder)
                # Get Song Statistics
                song = song_statistics(song) #return anything?

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
#   honestly not sure yet, I'll give it some time to think about it