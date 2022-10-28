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
parser.add_argument("--filetype", type="str", default="json", help="Filetype to save output as. Possible options: .json, .csv")
parser.add_argument("--genius", default=False, action='store_true', help="Lists alternative Genius ids when main argument is a songname")
# parser.add_argument("filename", type=str, default="data/combined.txt", help="Path of the input file.")
# parser.add_argument("--filter_lang", metavar="lang", type=str, default="en", help="Filters all lines not deemed to be of the given language.")
# parser.add_argument("--min_distance", type=int, default=3, help="Filters out all lines with a Levenshtein distance up to this value")
# parser.add_argument("--min_words", type=int, default=3, help="Filter all lines which have less than min_words.")
# parser.add_argument("--split", type=float, default=0.8, help="Splitpoint for train/test set.")
# parser.add_argument("--overwrite", default=False, action='store_true', help="Overwrite existing files")
# album type for artist request
args = parser.parse_args()


print(args.filename)

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
album_regex = "Deluxe|Edition"

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
    main_arg_type = parse_main_argument(args.main_argument)
    match main_arg_type:
        case "genius_id":
            get_single_lyric(args.main_argument)
        case "spotify":
            if args.lyrics_only

class Request()
    def __init__(self, query) -> None:
        self.query = query
        self 
    
    def request_type(query):
        """
        Differentiates whether the query is a genius_id, spotify_uri, or songname
        """
        if query.isdigit():
            return("genius_id")
        elif query.startswith("spotify_uri"):
            return("spotify")
        else:
            return("song")

    def get_spotify_request_type(self, uri):
        """
        Takes a spotify uri and returns the type of resource it requests i.e. song, album, artist, playlist
        """
        uri = uri.split(":")[1]    
        return uri

class Songcrawler():
    def __init__(self, lyrics_requested=True, filetype="json", use_genius_album=False) -> None:
        self.lyrics_requested = lyrics_requested
        self.filetype = filetype
        self.features_wanted = ['danceability', 'energy', 'key', 'loudness',
                                'mode', 'speechiness', 'acousticness', 'instrumentalness',
                                'liveness', 'valence', 'tempo', 'time_signature', 'duration_ms']
        self.use_genius_album = use_genius_album
        self.no_lyrics = {} # trackname: spotify_uri for songs without lyrics # Todo: remember to reset after each request


    def reques_backup(self, uri, genius_id=None, lyrics_requested=True):
        """
        Make a request for a song, album, artist or playlist.
        Returns the spotify statistics and by default also the lyrics
        """
        request_type = self.get_request_type(uri)
        self.lyrics_requested = lyrics_requested # does this make sense. So the lyrics_requested param doesn't need to get passed down
        match request_type:
            case "track":
                return self.get_song(uri, genius_id)
            case "album":
                return self.get_album(uri)
            case "artist":
                return self.get_artist(uri)
            case "playlist":
                return self.get_playlist(uri)
            case _:
                raise Exception(f'Unknown request type: \"{request_type}\"')
        # would be great if it didn't return yet
        # could print out missing songs here
        # reset missing songs after (or maybe at beginning of request function?)

    def request(self, query, lyrics_requested=True):
        """
        Make a request for a song, album, artist or playlist.
        Returns the spotify statistics and by default also the lyrics
        """
        # TODO instantiate request object from query

        # do different things here depending on request type

        # code from here should work (with some adjustments) for request_type spotify
        request_type = self.get_request_type(uri)
        self.lyrics_requested = lyrics_requested # does this make sense. So the lyrics_requested param doesn't need to get passed down
        match request_type:
            case "track":
                return self.get_song(uri, genius_id)
            case "album":
                return self.get_album(uri)
            case "artist":
                return self.get_artist(uri)
            case "playlist":
                return self.get_playlist(uri)
            case _:
                raise Exception(f'Unknown request type: \"{request_type}\"')
        # would be great if it didn't return yet
        # could print out missing songs here
        # reset missing songs after (or maybe at beginning of request function?)


    def get_lyrics(self, )

    def get_song(self, song_uri, genius_id=None): # num retries should be part of the CLI
        # Get song from spotify
        spotify_song = spotify.track(song_uri)
        song = spotify_song['name']
        artist = spotify_song['artists'][0]['name']
        album = spotify_song['album']['name']
        features = spotify.audio_features(tracks=[song_uri])[0]
        features = dict(filter(lambda i:i[0] in self.features_wanted, features.items()))

        # TODO: This should be it's own function
        if self.lyrics_requested:
            # Get song lyrics
            if genius_id:
                lyrics = genius.search_song(song_id=genius_id).lyrics # TODO: should try without genius id if this fails
            else:
                name_filtered = re.sub(r" *(\(.*\)|feat\.?.*|ft\..*)", "", song)
                lyrics = genius.search_song(name_filtered, artist).lyrics
                
            return {"artist": artist, "album" : album, **features}, lyrics
        else:
            return {"artist": artist, "album" : album, **features}
        

    def get_album(self, album_uri): # TODO: flag for using genius albums?
        spotify_album = spotify.album(album_uri)

        artist = spotify_album['artists'][0]['name']
        album = spotify_album['name']
        songs_to_uri = {entry["name"]:entry["uri"] for entry in spotify_album['tracks']['items']}

        if self.lyrics_requested:
            
            # TODO: if self.use_genius_album
            genius_album = genius.search_album(album, artist)
            genius_ids = [track.id for track in genius_album.tracks]
            songs = {}
            lyrics = {}
            missing_lyrics = []
            for index, (name, uri) in enumerate(songs_to_uri.items()):
                songs[name], lyrics[name] = self.get_song(song_uri=uri, genius_id=genius_ids[index])
                if not lyrics[name]:
                    missing_lyrics.append(set([name, uri])) # TODO: currently for logging, but could maybe find a better structure to automate
            return songs, lyrics
        else:
            songs = {name:self.get_song(uri) for name, uri in songs_to_uri.items()}
            return songs


    def get_artist(self, artist_uri, regex_filter = None, album_type="album"):
        spotify_artist = spotify.artist_albums(artist_uri, album_type=album_type, country="US", limit=50, offset=0) #setting country to US arbitrarily to avoid duplicates across regions
        artist = spotify.artist(artist_uri)["name"]
        album_to_uri = {album["name"]:album["uri"] for album in spotify_artist['items'] if not re.search(regex_filter, album["name"], re.I)}
        
        if self.lyrics_requested:
            albums = {}
            lyrics = {}
            for name, uri in album_to_uri.items():
                albums[name], lyrics[name] = self.get_album(uri)
            return(albums)
        else:
            albums = {name:self.get_album(uri) for name, uri in album_to_uri.items()}
            return albums
            

if __name__=="__main__":
    sc = Songcrawler()
    sc.request("spotify:album:6dVCpQ7oGJD1oYs2fv1t5M")
    #song = get_song("spotify:track:5CBEzaNEuv3OO32kZoXgOX")
    #album = get_album("spotify:album:6dVCpQ7oGJD1oYs2fv1t5M")#, lyrics_requested=False)
    #artist = get_artist("spotify:artist:0fA0VVWsXO9YnASrzqfmYu", album_regex)
    #print(artist)
    

# If it doesn't find anything then the lyrics are just empty e.g. New York City Rage Fest on Indicud
# Would be cool if it included the song / album uri for debugging



