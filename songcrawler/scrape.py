import json
import os
import re
import string

import lyricsgenius
import spotipy
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
        self.__type__ = "song"
    
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
    
    def get_single_album(whatever_input):
        # TODO: implement
        pass

class Song(object):
    def __init__(self, name, uri, artists = None, disc_number = None, track_number = None, duration_ms = None, explicit = False, lyrics = None):
        self.__type__ = "song"
        self._name = name
        self._uri = uri
        self._artists = artists
        self._disc_number = disc_number
        self._track_number = track_number
        self._duration_ms = duration_ms
        self._explicit = explicit
        self.lyrics = lyrics
    
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
    
    @property
    def danceability(self):
        return self._danceablilty
    
    @property
    def energy(self):
        return self._energy

    @property
    def key(self):
        return self._key
    
    @property
    def loudness(self):
        return self._loudness
    
    @property
    def mode(self):
        return self._mode
    
    @property
    def speechiness(self):
        return self._speechiness
    
    @property
    def acousticness(self):
        return self._acousticness

    @property
    def instrumentalness(self):
        return self._instrumentalness
    
    @property
    def liveness(self):
        return self._liveness

    @property
    def valence(self):
        return self._valence
    
    @property
    def tempo(self):
        return self._tempo

    def set_name(self, new_name):
        self._name = new_name

    @classmethod
    def from_spotify_song(cls,spotify_song):
        return cls(name = spotify_song["name"],
                    uri = spotify_song["uri"],
                    artists =  [artist["name"] for artist in spotify_song["artists"]],
                    disc_number = spotify_song["disc_number"],
                    track_number = spotify_song["track_number"],
                    duration_ms = spotify_song["duration_ms"],
                    explicit = spotify_song["explicit"]
                    )
    
    @classmethod
    def from_json(cls, json_path):
        json_dict = json.load(json_path)
        return cls(**json_dict)

    def to_json(self,json_path):
        if not os.path.splitext(json_path)[1] == ".json": 
            json_path += ".json"
            
        song_json = json.dumps(self.__dict__, indent=4)
        with open(json_path, "w" ) as song_file:
            song_file.write(song_json)

    # TODO: USED ANYWHERE?
    def fill_from_file(self,json_input):
        try:
                #json_dict = json.load(song_json)
                self.__dict__ =  dict(**json_input)
        except:
            print("couldn't fill from json")
        
    
    def get_audio_features(self):
        audio_features = spotify.audio_features(self.uri)[0]
        self._danceablilty = audio_features["danceability"]
        self._energy = audio_features["energy"]
        self._key = audio_features["key"]
        self._loudness = audio_features["loudness"]
        self._mode = audio_features["mode"]
        self._speechiness = audio_features["speechiness"]
        self._acousticness = audio_features["acousticness"]
        self._instrumentalness = audio_features["instrumentalness"]
        self._liveness = audio_features["liveness"]
        self._valence = audio_features["valence"]
        self._tempo = audio_features["tempo"]

    def get_genius_lyrics(self, name = None, artist_name = None):
        # Get lyrics for a certain song, name overwrites song name, arist_name overwrites artist name

        for artist in self.artists:
            if name:
                genius_song = genius.search_song(name, artist=artist, get_full_info=False)
            else:
                genius_song = genius.search_song(self.name, artist=artist, get_full_info=False)
            try:
                self.lyrics = genius_song.lyrics
                if genius_song == None:
                    # Does a weird loop sometimes ???
                    return "No lyrics found for song %s,\n" % self.name
                return
            except:
                continue
        
        print("\nNo lyrics found for song %s" % self.name)
        self.lyrics = None 
        return "No lyrics found for song %s,\n" % self.name
    
    def set_lyrics(self, lyrics):
        self.lyrics = lyrics


# TODO: check if song exists already, don't just overwrite
# TODO: better to get lyrics in bulk?
# ======>>> seperate class? in seperate file?

#################################
############ M A I N ############
#################################

# Get envvars
client_id = os.environ["SPOTIFY_CLIENT_ID"]
client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]
genius_token = os.environ["GENIUS_TOKEN"]

# Initialize spotipy client
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager) # Spotify object to access API

# Initialize Genius
genius = lyricsgenius.Genius(genius_token)

def get_single_song(song_uri):
    """
    gets single song and creates song object with audio features and lyrics
    """
    spotify_song = spotify.track(song_uri)
    song = Song.from_spotify_song(spotify_song)
    song.get_audio_features()
    song.album_name = spotify_song['album']['name']

    if song.get_genius_lyrics() != None:
        # TODO: maybe move to get_genius_lyrics ?
        new_name = re.sub(r" *(\(.*\)|feat\.?.*|ft\..*)", "", song.name)
        #song.set_name(new_name) # TODO: Better: don't change name, give name as an argument or move to get_genius_lyrics?
        if song.get_genius_lyrics(name=new_name) != None:\
            print("Couldn get lyrics for %s" % song.name)

    return song


def crawl_songs(input_artist_uri, overwrite = True, get_lyrics = True):
    """
    Crawls Spotify for audio features and Genius for lyrics
    Creates a Artist folder with album subfolders, each containing the respective songs in JSON format
    Returns the artist folder path upon completition
    """
    # Instantiate artist object
    artist = Artist(input_artist_uri)

    # Setup correct path
    #os.chdir("songcrawler") # TODO: include in input_artist_path ?
    input_artist_path = "songcrawler/data/" + artist.name.replace(" ","_")

    ####FOR DEBUGGING#########
    #return input_artist_path

    errors = []

    # Check if artist directory exists already
    if not os.path.exists(input_artist_path):
        print("Artist folder does not exist, creating folder %s." % input_artist_path)
        try:
            os.mkdir(input_artist_path)
        except OSError:
            errors.append((artist.name, "error creating artist"))
            print ("Creation of the directory %s failed" % input_artist_path)
        else:
            print ("Successfully created the directory %s \n" % input_artist_path)
    else:
        print(input_artist_path + " directory exists already. Overwrite?")
        if overwrite == True:
            # TODO: overwrite album
            pass

    for album in artist.albums: # iterate through album objects
        album_path = input_artist_path + "/" + album.name

        # Check if album path exists
        if not os.path.exists(album_path):
                print("Folder %s does not exist, creating folder..." % album_path)
                try:
                    os.mkdir(album_path)
                except OSError:
                    errors.append((album.name, "error creating album"))
                    print ("Creation of the directory %s failed" % album_path)
                else:
                    print ("Successfully created the directory %s \n " % album_path)
        else:
            print(album_path + " exists")
            # TODO: ask if overwrite fine?
            if overwrite == True:
                pass
            else:
                print("skipping album")
                continue

        spotify_album = spotify.album(album.uri)["tracks"]["items"]

        for spotify_song in spotify_album:
            
            if re.search("edit(ed)?|clean|remix", spotify_song["name"], re.IGNORECASE): # filter for edited versions
                # TODO: improve match pattern
                print("Skipping song: %s" % spotify_song["name"])
                continue

            song = Song.from_spotify_song(spotify_song) # convert to song object from spotify song
            song.album_name = album.name
            album.addsong(song)
            
            songpath = album_path + "/" + song.name.translate(str.maketrans('', '', string.punctuation))
            if not os.path.isfile(songpath):
                try:
                    # Get song info
                    song.get_audio_features()
                    if get_lyrics == True:
                        if song.get_genius_lyrics() != None: # Ugly solution, but it works, maybe use a for loop in range 3?
                            if song.get_genius_lyrics() != None: # Try again, sometimes takes more than one try
                                errors.append((song.name, song.uri, "missing lyrics"))
                    else:
                        print(song.name, end=" ")

                    # Write to file
                    song.to_json(songpath + ".json")

                except OSError:
                    errors.append((song.name, "OSError"))
                    print("\nFailed to save song %s.\n" % song.name)
            else: 
                #TODO: Ask to overwrite
                continue
    
    with open("errors.txt", "w") as error_file:
        error_file.write(str(errors))
        print(errors)

    return input_artist_path

def find_missing_lyrics(errors=None):
    """
    Takes a list of tuples with the songname, the uri and the error type.
    Attempts to fix the missing Lyrics.

    Some lyrics seem to not be found without any reason, just trying to scrape them again
    fixes the problem.
    It's caused by the dependency on the Lyricscraper by LyricGenius...
    TODO: Remove dependencies and restructure parts of the program...
    """

    if errors == None:
        errors = "songcrawler/errors.txt"
    
    # TODO: Fill out rest of Function
    # TODO: Use Glob to find songs with errors
    #       Alternatively: Change Error Messages, so they include the songpath        


# TODO: Change how folders are managed, don't change dir to songcrawler...
# TODO: Save artist level info in artist folder
# TODO: average songs
# TODO: add function get_playlist(playlist_uri)
#######################################################
# TODO: create list of failed songs, print out at end##
#######################################################