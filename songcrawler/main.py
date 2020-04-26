import json
import os
import re

import spotipy
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from spotipy.oauth2 import SpotifyClientCredentials

class Artist(object):
    """ An Artist based on the Info provided by the Spotify API

    Attributes:
    name: (str) Artist name
    id: (str) Artist ID
    genres: (list) List of genres the artist is active in

    """
    def __init__(self, artist_uri):
        spotify_artist_info = spotify.artist(artist_uri)
        self._uri = artist_uri
        self._name = spotify_artist_info["name"] # add conditional statement if name not given
        self._id = spotify_artist_info["id"]
        self._genres = spotify_artist_info["genres"]
        self._albums = self.get_spotify_albums(artist_uri)
    
    @property
    def name(self):
        return self._name

    @property
    def genres(self):
        return self._genres

    @property
    def id(self):
        return self._id
    
    @property
    def albums(self):
        return self._albums
    
    @staticmethod # good as that?
    def get_spotify_albums(uri, filtered = True, max_albums = 50): # returns list of spotify albums
        # input: artist uri, output list of album objects
        name = spotify.artist(uri)["name"]
        # get albums
        # TODO: Find a better way to deal with duplicates
        #       -> use albumsAreSame method?
        if filtered:
            albums = [album for album in spotify.artist_albums(uri, album_type='album', limit= max_albums)["items"] if len(album['available_markets']) > 10]
        else:
            albums = spotify.artist_albums(uri, album_type='album', limit= max_albums)["items"]
        
        return [Album.from_spotify_album(album, name, uri) for album in albums]

class Album(object):
    def __init__ (self, album_name, album_uri, artist_name, artist_uri, release_date, total_tracks):
        self._name = album_name
        self._uri = album_uri
        self._artist_name = artist_name
        self._artist_uri = artist_uri
        self._release_date =  release_date
        self._total_tracks = total_tracks
        self._songs = []
    
    @property
    def name(self):
        return self._name
    
    @property
    def uri(self):
        return self._uri

    @property
    def artist_name(self):
        return self._artist_name
    
    @property
    def artist_uri(self):
        return self._artist_uri
    
    @property
    def release_date(self):
        return self._release_date
    
    @property
    def total_tracks(self):
        return self._total_tracks

    @classmethod
    def from_spotify_album(cls, album, artist_name, artist_uri):
        album_name   = album["name"]
        album_uri    = album["uri"] 
        release_date = album["release_date"]
        total_tracks = album["total_tracks"]
        return cls(album_name, album_uri, artist_name, artist_uri, release_date, total_tracks)

    
    @classmethod
    def albumsAreSame(a1, a2):
        """ Check if albums are the same, by looking at the sequence of strings and songs in the album
            return album with more songs?
            Ways to handle censored albums -> automatically available in less markets, right
            Include market availability filter?"""

        #from difflib import SequenceMatcher as sm  # For comparing similarity of albums
        #name_ratio = sm(None, a1[],), 
        #seqA = sm(None, s1.lyrics, s2['lyrics'])
        #seqB = sm(None, s2['lyrics'], s1.lyrics)
        #return seqA.ratio() > 0.5 or seqB.ratio() > 0.5
    
    def addsong(self, song):
        # Takes song instance and adds it to list of songs
        self._songs.append(song)

class Song(object):
    def __init__(self, name, uri, artists, disc_number, track_number, duration_ms, explicit):
        self._name = name
        self._uri = uri
        self._artists = [artist["name"] for artist in artists]
        self._disc_number = disc_number
        self._track_number = track_number
        self._duration_ms = duration_ms
        self._explicit = explicit
    
    @property
    def name(self):
        return self._name
    
    @property
    def uri(self):
        return self._uri
    
    @property
    def artists(self):
        return self._artists
    
    @property
    def disc_number(self):
        return self._disc_number
    
    @property
    def track_number(self):
        return self._track_number
    
    @property
    def duration_ms(self):
        return self._duration_ms
    
    @property
    def explicit(self):
        return self._explicit

    @classmethod
    def from_spotify_song(cls,spotify_song):
        return cls(name = spotify_song["name"],
                    uri = spotify_song["uri"],
                    artists =  spotify_song["artists"],
                    disc_number = spotify_song["disc_number"],
                    track_number = spotify_song["track_number"],
                    duration_ms = spotify_song["duration_ms"],
                    explicit = spotify_song["explicit"]
                    )
    
    def get_genius_lyrics(self, song):
        #TODO: Do something
        return


#################################
############ M A I N ############
#################################

# Get envvars
client_id = os.environ["SPOTIFY_CLIENT_ID"]
client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]
genius_token = os.environ["GENIUS_TOKEN"]

# Artist
input_artist = "Kid Cudi" # TODO: find a way not to hardcode, maybe as cl-argument?
input_artist_uri = 'spotify:artist:0fA0VVWsXO9YnASrzqfmYu'

# Initialize spotipy client
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager) # Spotify object to access API

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Setup correct path
os.chdir("songcrawler")
input_artist_path = "data/" + input_artist.replace(" ","_") 

# Check if artist directory exists already
if not os.path.exists(input_artist_path):
    print("Artist folder does not exist, creating folder %s." % input_artist_path)
    try:
        os.mkdir(input_artist_path)
    except OSError:
        print ("Creation of the directory %s failed" % input_artist_path)
    else:
        print ("Successfully created the directory %s " % input_artist_path)
else:
    print(input_artist_path + " directory exists already. Overwrite?")
    # TODO: Ask if overwrite fine

# Instantiate artist object
artist = Artist(input_artist_uri)

for album in artist.albums: # artist.albums are album objects
    album_path = input_artist_path + "/" + album.name

    # Check if album path exists
    if not os.path.exists(album_path):
            print("album folder does not exist, creating folder %s." % album_path)
            try:
                os.mkdir(album_path)
            except OSError:
                print ("Creation of the directory %s failed" % album_path)
            else:
                print ("Successfully created the directory %s " % album_path)
    else:
        print(album_path + " exists")
        # TODO: ask if overwrite fine?
        
    spotify_album = spotify.album(album.uri)["tracks"]["items"]

    for spotify_song in spotify_album:
        # TODO: check if song exists already, don't just overwrite
        
        song = Song.from_spotify_song(spotify_song) # convert to song object from spotify song
        album.addsong(song) # add song object to list of songs
        song.get_genius_lyrics(song) # TODO: fetch song lyrics
