import argparse
from operator import ge
import os
import lyricsgenius
import spotipy
import re
from spotipy.oauth2 import SpotifyClientCredentials

#----------------------------------------------------------------------------
#                               ARGPARSE
#----------------------------------------------------------------------------
# parser = argparse.ArgumentParser(description='Clean a file to remove duplicates and foreign sentences')
# parser.add_argument("filename", type=str, default="data/combined.txt", help="Path of the input file.")
# parser.add_argument("--filter_lang", metavar="lang", type=str, default="en", help="Filters all lines not deemed to be of the given language.")
# parser.add_argument("--min_distance", type=int, default=3, help="Filters out all lines with a Levenshtein distance up to this value")
# parser.add_argument("--min_words", type=int, default=3, help="Filter all lines which have less than min_words.")
# parser.add_argument("--split", type=float, default=0.8, help="Splitpoint for train/test set.")
# parser.add_argument("--overwrite", default=False, action='store_true', help="Overwrite existing files")

# args = parser.parse_args()

# print(args.filename)

#----------------------------------------------------------------------------
#                               Setup
#----------------------------------------------------------------------------

client_id = os.environ["SPOTIFY_CLIENT_ID"]
client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]
#genius_token = os.environ["GENIUS_ACCESS_TOKEN"]

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager) # Spotify object to access API

# Initialize Genius
genius = lyricsgenius.Genius(retries=1)

genius.verbose = False # Turn off status messages
genius.remove_section_headers = True # Remove section headers (e.g. [Chorus]) from lyrics when searching
genius.skip_non_songs = False # Include hits thought to be non-songs (e.g. track lists)
genius.excluded_terms = ["(Remix)", "(Live)"] # Exclude songs with these words in their title

features_wanted = ['danceability', 'energy', 'key', 'loudness',
                    'mode', 'speechiness', 'acousticness', 'instrumentalness',
                    'liveness', 'valence', 'tempo', 'time_signature', 'duration_ms']

song_regex = "edit(ed)?|clean|remix" # TODO: use excluded terms instead, or make the same at least
album_regex = "Deluxe|Edition"

#----------------------------------------------------------------------------
#                               Functions
#----------------------------------------------------------------------------

#TODO: You can automatically differentiate the type of spotify uri
# e.g. spotify:playlist:37i9dQZF1DXa9Q01E86Ntt -> playlist
#      spotify:artist:0fA0VVWsXO9YnASrzqfmYu -> artist
#      the type of request that is made from songcrawler can be automatically determined by the URI

def get_song(song_uri, genius_id=None, get_lyrics=True): # num retries should be part of the CLI
    # Get song from spotify
    spotify_song = spotify.track(song_uri)
    song = spotify_song['name']
    artist = spotify_song['artists'][0]['name']
    album = spotify_song['album']['name']
    features = spotify.audio_features(tracks=[song_uri])[0]
    features = dict(filter(lambda i:i[0] in features_wanted, features.items()))

    if get_lyrics:
        # Get song lyrics
        if genius_id:
            lyrics = genius.search_song(song_id=genius_id).lyrics # TODO: should try without genius id if this fails
        else:
            name_filtered = re.sub(r" *(\(.*\)|feat\.?.*|ft\..*)", "", song)
            lyrics = genius.search_song(name_filtered, artist).lyrics
            
        return {"artist": artist, "album" : album, **features}, lyrics
    else:
        return {"artist": artist, "album" : album, **features}
    




###############################################################

#### TODO:
# First big next feature should be the argparse, as this lays the groundwork / framework for how this programme should be designed
# Would be great to have this as a class
#   songscraper or smth like that
#   could have the artist name in there
#   error handling could be done there e.g. keeping track of missing songs 
###############################################################
# use_genius_albums could be a self parameter


def get_album(album_uri, get_lyrics=True): # TODO: flag for using genius albums?
    spotify_album = spotify.album(album_uri)

    artist = spotify_album['artists'][0]['name']
    album = spotify_album['name']
    songs_to_uri = {entry["name"]:entry["uri"] for entry in spotify_album['tracks']['items']}

    if get_lyrics:
        # TODO: seperate lyrics from songs
        # Necessary if the artist has multiple songs with the same name (e.g. The 1975)
        genius_album = genius.search_album(album, artist)
        genius_ids = [track.id for track in genius_album.tracks]
        songs = {}
        lyrics = {}
        missing_lyrics = []
        for index, (name, uri) in enumerate(songs_to_uri.items()):
            songs[name], lyrics[name] = get_song(song_uri=uri, genius_id=genius_ids[index])
            if not lyrics[name]:
                missing_lyrics.append(set([name, uri])) # TODO: currently for logging, but could maybe find a better structure to automate
        return songs, lyrics
    else:
        songs = {name:get_song(uri, get_lyrics=False) for name, uri in songs_to_uri.items()}
        return songs



def get_artist(artist_uri, regex_filter = None, album_type="album", get_lyrics=True):
    spotify_artist = spotify.artist_albums(artist_uri, album_type=album_type, country="US", limit=50, offset=0) #setting country to US arbitrarily to avoid duplicates across regions
    artist = spotify.artist(artist_uri)["name"]
    album_to_uri = {album["name"]:album["uri"] for album in spotify_artist['items'] if not re.search(regex_filter, album["name"], re.I)}
    
    if get_lyrics:
        albums = {}
        lyrics = {}
        for name, uri in album_to_uri.items():
            albums[name], lyrics[name] = get_album(uri)
        return(albums)
    else:
        albums = {name:get_album(uri) for name, uri in album_to_uri.items()}
        return albums
        

if __name__=="__main__":
    #song = get_song("spotify:track:5CBEzaNEuv3OO32kZoXgOX")
    album = get_album("spotify:album:6dVCpQ7oGJD1oYs2fv1t5M", get_lyrics=False)
    artist = get_artist("spotify:artist:0fA0VVWsXO9YnASrzqfmYu", album_regex)
    #print(artist)
    

# If it doesn't find anything then the lyrics are just empty e.g. New York City Rage Fest on Indicud
# Would be cool if it included the song / album uri for debugging



