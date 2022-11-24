
import os
import lyricsgenius
import spotipy
from multiprocessing import Pool

from spotipy.oauth2 import SpotifyClientCredentials

from utils import delete_dir, file_empty, overwrite_dir, Path, get_int_input
import glob


client_id = os.environ["SPOTIFY_CLIENT_ID"]
client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Initialize Genius
genius = lyricsgenius.Genius(retries=1)

genius.verbose = False # Turn off status messages
genius.remove_section_headers = True # Remove section headers (e.g. [Chorus]) from lyrics when searching
genius.skip_non_songs = False # Include hits thought to be non-songs (e.g. track lists)
genius.excluded_terms = ["(Remix)", "(Live)"] # Exclude songs with these words in their title

PARALLELIZE = True
song_regex = "edit(ed)?|clean|remix" # TODO: use excluded terms instead, or make the same at least