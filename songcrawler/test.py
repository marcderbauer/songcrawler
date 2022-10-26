
# testing function, needs to be removed
import json

from scrape import Song, get_single_song
from process import song_statistics


song = get_single_song("spotify:track:3tzMl05JCzmXG4VGLbOruw")


song.set_lyrics("""lyrics_go_here""")
song = song_statistics(song)

song.to_json("songcrawler/data/Kid_Cudi/Speedin' Bullet 2 Heaven/Judgmental Ct.json")

#TODO: Manually Fix Wrong Entries in CSV
#       Fix Problems some other time...
