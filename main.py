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

parser = argparse.ArgumentParser(description='Gather Spotify statistics and Genius lyrics.')
parser.add_argument("main_argument", type=str, help="Either a Spotify uri, a songname or a genius id")
parser.add_argument("--filetype", type=str, default="json", help="Filetype to save output as. Possible options: .json, .csv")
parser.add_argument("--genius", default=False, action='store_true', help="Lists alternative Genius ids when main argument is a songname")
# parser.add_argument("filename", type=str, default="data/combined.txt", help="Path of the input file.")
# parser.add_argument("--filter_lang", metavar="lang", type=str, default="en", help="Filters all lines not deemed to be of the given language.")
# parser.add_argument("--min_distance", type=int, default=3, help="Filters out all lines with a Levenshtein distance up to this value")
# parser.add_argument("--min_words", type=int, default=3, help="Filter all lines which have less than min_words.")
# parser.add_argument("--split", type=float, default=0.8, help="Splitpoint for train/test set.")
# parser.add_argument("--overwrite", default=False, action='store_true', help="Overwrite existing files")
# album type for artist request
args = parser.parse_args()


#print(args.filename)

#----------------------------------------------------------------------------
#                               Setup
#----------------------------------------------------------------------------

client_id = os.environ["SPOTIFY_CLIENT_ID"]
client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager) # Spotify object to access API

# Initialize Genius
genius = lyricsgenius.Genius(retries=1)

genius.verbose = False # Turn off status messages
genius.remove_section_headers = True # Remove section headers (e.g. [Chorus]) from lyrics when searching
genius.skip_non_songs = False # Include hits thought to be non-songs (e.g. track lists)
genius.excluded_terms = ["(Remix)", "(Live)"] # Exclude songs with these words in their title



song_regex = "edit(ed)?|clean|remix" # TODO: use excluded terms instead, or make the same at least


#----------------------------------------------------------------------------
#                               Functions
#----------------------------------------------------------------------------




    #±±±±±±±±±±±±±±±±±±±±±±±±#±±±±±±±±±±±±±±±±±±±±±±±±#±±±±±±±±±±±±±±±±±±±±±±±±#±±±±±±±±±±±±±±±±±±±±±±±±
    #
    # Would make sense to have --lyrics_only as a flag, but say it's only supported for single songs
    # Could then check if this flag is set if given a genius id or a songname
    #
    #±±±±±±±±±±±±±±±±±±±±±±±±#±±±±±±±±±±±±±±±±±±±±±±±±#±±±±±±±±±±±±±±±±±±±±±±±±#±±±±±±±±±±±±±±±±±±±±±±±±

def get_single_lyrics(genius_id):
    # gets lyrics for a single song from genius.
    # great for fixing missing lyrics
    pass

def main():
    # This is used only when accessing the program through the CLI
    # Keep in mind that the songcrawler class should also work independently as a python module
    pass
    main_arg_type = parse_main_argument(args.main_argument)
    match main_arg_type:
        case "genius_id":
            get_single_lyric(args.main_argument)
        case "spotify":
            if args.lyrics_only:
                pass

#----------------------------------------------------------------------------
#                               Request
#----------------------------------------------------------------------------

class Request():
    def __init__(self, query) -> None:
        self.query = query
        self.type = self.get_request_type(query)
    
    def get_request_type(self, query):
        """
        Differentiates whether the query is a genius_id, spotify_uri, or songname
        """
        if query.isdigit():
            return("genius")
        elif query.startswith("spotify:"):
            return("spotify")
        else:
            return("song")

    def get_spotify_type(self, uri):
        """
        Takes a spotify uri and returns the type of resource it requests i.e. song, album, artist, playlist
        """
        uri = uri.split(":")[1]    
        return uri

#----------------------------------------------------------------------------
#                               Music
#----------------------------------------------------------------------------
# TODO: Maybe save uri for each of these

class Song():
    def __init__(self, name, album, artist, features, lyrics=None) -> None:
        self.name = name
        self.album = album
        self.artist = artist
        self.features = features
        self.lyrics = lyrics


class Album():
    def __init__(self, name, artist, songs_to_uri=None) -> None:
        self.name = name
        self.artist = artist
        self.songs_to_uri = songs_to_uri
        self.songs = {}
        self.missing_lyrics = {} # name:uri of missing songs 


class Artist():
    def __init__(self, name, albums_to_uri=None) -> None:
        self.name = name
        self.albums_to_uri = albums_to_uri
        self.albums = {}
        self.missing_lyrics = {} # name:uri of missing songs 


class Playlist():
    def __init(self, name) -> None:
        self.name = name




#----------------------------------------------------------------------------
#                               Songcrawler
#----------------------------------------------------------------------------

class Songcrawler():
    def __init__(self, lyrics_requested=True, filetype="json", use_genius_album=False, region="US") -> None:
        self.lyrics_requested = lyrics_requested
        self.filetype = filetype
        self.features_wanted = ['danceability', 'energy', 'key', 'loudness',
                                'mode', 'speechiness', 'acousticness', 'instrumentalness',
                                'liveness', 'valence', 'tempo', 'time_signature', 'duration_ms']
        self.use_genius_album = use_genius_album
        self.no_lyrics = {} # trackname: spotify_uri for songs without lyrics # Todo: remember to reset after each request
        self.region = region #setting country to US arbitrarily to avoid duplicates across regions
        self.album_regex = "Deluxe|Edition"

    def request(self, query, lyrics_requested=True):
        """
        Make a request for a song, album, artist or playlist.
        Returns the spotify statistics and by default also the lyrics
        """
        # TODO instantiate request object from query
        request = Request(query)
        # do different things here depending on request type

        # code from here should work (with some adjustments) for request_type spotify
        # request_type = self.get_request_type(uri)
        # TODO: calling this method by default sets lyrics_requested to true, which may overwrite a global param
        self.lyrics_requested = lyrics_requested # does this make sense. So the lyrics_requested param doesn't need to get passed down
        if request.type == "spotify":
            match request.get_spotify_type(query):
                case "track":
                    result = self.get_song(query)
                case "album":
                    return self.get_album(query)
                case "artist":
                    return self.get_artist(query)
                case "playlist":
                    return self.get_playlist(query)
                case _:
                    raise Exception(f'Unknown request type: \"{request_type}\"')
        elif request.type == "genius":
            result = self.get_lyrics(query)
            print(result)
        else:
            if self.lyrics_only:
                self.get_lyrics(query)
            else:
                # try to find song_uri and get_song
                pass
        
        # check if length of result is two -> shows if you have lyrics and spotify / music
        # maybe a class would be better for that?

        # would be great if it didn't return yet
        # could print out missing songs here
        # reset missing songs after (or maybe at beginning of request function?)


    def get_lyrics(self, genius_id=None, song=None, artist=None):
        """
        Takes a genius_id or song name and returns the lyrics for it
        """
        if genius_id:
            pass
        elif (song == None or artist == None):
            raise Exception("requires either a genius_id or a songname and artist")
        
        if genius_id:
                lyrics = genius.search_song(song_id=genius_id).lyrics # TODO: should try without genius id if this fails
        else:
            name_filtered = re.sub(r" *(\(.*\)|feat\.?.*|ft\..*)", "", song)
            lyrics = genius.search_song(name_filtered, artist).lyrics
        return lyrics


    def get_song(self, song_uri, genius_id=None): # num retries should be part of the CLI
        # Get song from spotify
        spotify_song = spotify.track(song_uri)
        song_name = spotify_song['name']
        artist_name = spotify_song['artists'][0]['name']
        album_name = spotify_song['album']['name']
        features = spotify.audio_features(tracks=[song_uri])[0]
        features = dict(filter(lambda i:i[0] in self.features_wanted, features.items()))
        song = Song(song_name, album_name, artist_name, features)

        # TODO: This should be it's own function
        if self.lyrics_requested:
            if genius_id:
                song.lyrics = self.get_lyrics(genius_id = genius_id)
            # Get song lyrics
            if not song.lyrics:
                song.lyrics = self.get_lyrics(song=song_name, artist=artist_name)

        return song

        

    def get_album(self, album_uri): # TODO: flag for using genius albums?
        spotify_album = spotify.album(album_uri)

        artist_name = spotify_album['artists'][0]['name']
        album_name = spotify_album['name']
        songs_to_uri = {entry["name"]:entry["uri"] for entry in spotify_album['tracks']['items']}

        album = Album(album_name, artist_name, songs_to_uri)
        songs = {}

        # Solution isn't very pretty, could be reworked
        # Maybe seperate get_song function for genius_id and spotify_uri?
        if self.use_genius_album:
        # TODO: I can still use genius's albums, I just need to find a way to align it by song
        # genius albums do include the title, even if it's a bit different from the titles in spotify
        # Could maybe use that?
        
            genius_album = genius.search_album(album_name, artist_name)
            album.genius_ids = [track.id for track in genius_album.tracks]

            for index, (name, uri) in enumerate(songs_to_uri.items()):
                song = self.get_song(song_uri=uri, genius_id=album.genius_ids[index])
                songs[name] = song
                if not song.lyrics:
                    album.missing_lyrics[name]= uri # TODO: currently for logging, but could maybe find a better structure to automate
        else:
            for name, uri in songs_to_uri.items():
                song = self.get_song(uri)
                songs[name] = song
                if not song.lyrics:
                    album.missing_lyrics[name]= uri

        album.songs = songs
        return album



    def get_artist(self, artist_uri, album_type="album"):
        spotify_artist = spotify.artist_albums(artist_uri, album_type=album_type, country=self.region, limit=50)
        artist_name = spotify.artist(artist_uri)["name"]
        albums_to_uri = {album["name"]:album["uri"] for album in spotify_artist['items'] if not re.search(self.album_regex, album["name"], re.I)}
        artist = Artist(artist_name, albums_to_uri)
        albums = {}
        missing_lyrics = {}

        for name, uri in albums_to_uri.items():
            albums[name] = self.get_album(uri)
        
        # TODO: find all missing songs across albums
        artist.albums = albums
        return(albums)

            

if __name__=="__main__":
    sc = Songcrawler()
    artist = sc.request("spotify:artist:0fA0VVWsXO9YnASrzqfmYu")
    album = sc.request("spotify:album:6dVCpQ7oGJD1oYs2fv1t5M")#, lyrics_requested=False)
    song = sc.request("spotify:track:5CBEzaNEuv3OO32kZoXgOX")
    sc.request("8150537")
    sc.request("spotify:album:6dVCpQ7oGJD1oYs2fv1t5M")
    #print(artist)
    # BFIAFL genius_ids:
    # [8150565, 8150537, 8150538, 8099567, 8150539, 8150540, 8150541, 8150542, 8150543, 8150544, 8150545]

# If it doesn't find anything then the lyrics are just empty e.g. New York City Rage Fest on Indicud
# Would be cool if it included the song / album uri for debugging



