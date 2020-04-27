import json
import os
import re
import string

import lyricsgenius
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

    def get_genius_lyrics(self):

        # for multiple artists on one song, if it doesn't find it with song artist, try album artist
        # TODO: use "Try except framework"
        for artist in self.artists:
            genius_song = genius.search_song(self.name, artist=artist,get_full_info=False)
        
            # TODO: better way to handle error messages?
            try:
                self.lyrics = genius_song.lyrics
                return
            except:
                continue
        
        print("\nNo lyrics found for song %s" % self.name)
        self.lyrics = " "
        return
            
            

    #######################
    # UNUSED!!!!!!!!!!!!!!!
    #######################
    def process_lyrics(self):
        # TODO: Do in a seperate program
        # TODO: Tokenize, lemmatize, wordfreq list
        self.tokens = [word for word in word_tokenize(self.lyrics) if word.isalpha()]
        self.lemmas = [lemmatizer.lemmatize(word.lower()) for word in self.tokens]





# TODO: check if song exists already, don't just overwrite
# TODO: better to get lyrics in bulk?
# TODO: Process lyrics
# ======>>> seperate class? in seperate file?
# TODO: get info on an album basis (TF_IDF, most used words, avg score for each spotify feature...)
# TODO: create a folder for all the statistics and one for all the lyrics of any given album
# TODO: make errors more visible, don't clutter up console



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

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer() 


def crawl_songs(input_artist_uri, overwrite = True, get_lyrics = True):
    # Instantiate artist object
    artist = Artist(input_artist_uri)

    # Setup correct path
    os.chdir("songcrawler")
    input_artist_path = "data/" + artist.name.replace(" ","_")

    # Check if artist directory exists already
    if not os.path.exists(input_artist_path):
        print("Artist folder does not exist, creating folder %s." % input_artist_path)
        try:
            os.mkdir(input_artist_path)
        except OSError:
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
                    print ("Creation of the directory %s failed" % album_path)
                else:
                    print ("Successfully created the directory %s \n " % album_path)
        else:
            print(album_path + " exists")
            # TODO: ask if overwrite fine?

        spotify_album = spotify.album(album.uri)["tracks"]["items"]

        for spotify_song in spotify_album:
            
            if re.search("edit(ed)?|clean|remix", spotify_song["name"], re.IGNORECASE): # filter for edited versions
                # TODO: improve match pattern, also match clean
                continue

            song = Song.from_spotify_song(spotify_song) # convert to song object from spotify song
            album.addsong(song)
            
            songpath = album_path + "/" + song.name.translate(str.maketrans('', '', string.punctuation))
            if not os.path.isfile(songpath):
                try:
                    # Get song info
                    song.get_audio_features()
                    if get_lyrics == True:
                        song.get_genius_lyrics()
                    else:
                        print(song.name, end=" ")

                    # Write to file
                    song_json = json.dumps(song.__dict__, indent=4)
                    with open (songpath, "w") as f:
                        f.write(song_json)

                except OSError: #TODO: right error?
                    print("\nFailed to save song %s.\n" % song.name)
            else: 
                #TODO: Ask to overwrite
                continue

if __name__ == "__main__":
    #input_artist = "Kanye" # TODO: find a way not to hardcode, maybe as cl-argument?
    input_artist_uri = 'spotify:artist:5K4W6rqBFWDnAN6FQUkS6x'

    crawl_songs(input_artist_uri, overwrite=False, get_lyrics=True)
