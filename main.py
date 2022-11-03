import argparse
import os
import lyricsgenius
import spotipy
import re
from spotipy.oauth2 import SpotifyClientCredentials
import json
from abc import ABC, abstractmethod
from multiprocessing import Pool
from itertools import repeat



#----------------------------------------------------------------------------
#                               ARGPARSE
#----------------------------------------------------------------------------

parser = argparse.ArgumentParser(description='Gather Spotify statistics and Genius lyrics.')
parser.add_argument("query", metavar="Spotify URI, Genius ID or Songname", type=str, help="Either a Spotify uri, a songname or a genius id")
parser.add_argument("--filetype", type=str, default="json", help="Filetype to save output as. Possible options: .json, .csv")
parser.add_argument("--genius", default=False, action='store_true', help="Lists alternative Genius ids when main argument is a songname")
parser.add_argument("--no_lyrics", default=False, action='store_true', help="Skips gathering lyrics and only queries spotify statistics.")
parser.add_argument("--use_genius_album", default=False, action='store_true', help="Uses Genius albums, experimental feature for artists who have different tracks with the same name.")
parser.add_argument("--region", type=str, default="US", help="Region to query songs for Spotify API. Helps prevent duplicate album entries.")
parser.add_argument("--folder", type=str, default="data", help="Output folder")
parser.add_argument("--overwrite", default=False, action='store_true', help="Overwrites existing songs/albums/artists/playlists")
parser.add_argument("--album_type",type=str, default="album", help="Type albums to retrieve when querying an album. Possible Values: album, ep")
args = parser.parse_args()

#TODO: add all possible album types to --album_type help
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

PARALLELIZE = True

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



def main():
    # This is used only when accessing the program through the CLI
    # Keep in mind that the songcrawler class should also work independently as a python module
    sc = Songcrawler(lyrics_requested=not args.no_lyrics,
                    filetype=args.filetype, 
                    use_genius_album=args.use_genius_album, 
                    region=args.region,
                    folder=args.folder,
                    overwrite=args.overwrite,
                    album_type=args.album_type)
    sc.request(args.query)

#----------------------------------------------------------------------------
#                               Music
#----------------------------------------------------------------------------
# TODO: Maybe save uri for each of these

# Each of those should have the method to convert them to strings (__repr__?) and how to save them to a file
# Could maybe actually use an abstract class and make them inherit this?

class Music(ABC):
    @abstractmethod
    def from_spotify(uri):
        print("implement me")
    
    @classmethod
    def request(cls, request):
        if request.type == "spotify": # if request.spotify_type ? 
            match request.get_spotify_type(): # This should be an attribute of request really
                case "track":
                    song = Song.from_spotify(request.query, lyrics_requested=request.lyrics_requested, 
                                features_wanted=request.features_wanted)#, genius_id=genius_id) TODO: figure out genius ID here
                    return song
                case "album":
                    album = Album.from_spotify(request.query, request.lyrics_requested, request.features_wanted,
                                                request.use_genius_album)
                    return album
                case "artist":
                    # saving within get_artist method after every album in case program crashes
                    artist = Artist.from_spotify(request.query, album_type=request.album_type, regex_filter=request.album_regex,
                                                region=request.region, limit=request.limit)
                    return artist
                case "playlist":
                    playlist = Playlist.from_spotify(uri=request.query)
                    return playlist
                case _:
                    raise Exception(f'Unknown request type: \"{request.type}\"')
        elif request.type == "genius":
            result = Song.get_lyrics(genius_id=request.query)
            print(result)
            # TODO: Figure out how to save this
        else:
            if request.lyrics_only:
                result = Song.get_lyrics(request.query)
                # TODO: figure out how to save this
            else:
                # try to find song_uri and get_song
                pass

class Song(Music):
    def __init__(self, uri, name, album, artist, audio_features, feature_artists = None, lyrics=None) -> None:
        self.uri = uri
        self.name = name
        self.album = album
        self.artist = artist
        self.audio_features = audio_features
        self.feature_artists = feature_artists
        self.lyrics = lyrics
    
    def __repr__(self) -> str:
        printstring = f"""
        Name:           {self.name}
        Album:          {self.album}
        Artist:         {self.artist}
        Found Lyrics:   {f"Yes -- {self.lyrics[:50]}..." if self.lyrics else "No :("}    
        """
        return printstring
    
    @classmethod
    def multi_run_wrapper(cls, input_args):
        uri, (lyrics_requested, features_wanted) = input_args
        return Song.from_spotify(uri=uri, lyrics_requested=lyrics_requested, features_wanted=features_wanted)
        
    @classmethod
    def from_spotify(cls, uri, lyrics_requested, features_wanted, genius_id=None):
        spotify_song = spotify.track(uri)
        song_name = spotify_song['name']
        artist_name = spotify_song['artists'][0]['name']
        album_name = spotify_song['album']['name']
        feature_artists = [artist["name"] for artist in spotify_song['artists']][1:]
        audio_features = spotify.audio_features(tracks=[uri])[0]
        audio_features = dict(filter(lambda i:i[0] in features_wanted, audio_features.items()))
        song = Song(uri, song_name, album_name, artist_name, audio_features, feature_artists=feature_artists)

        # TODO: Either make this a classmethod or move this to song
        if lyrics_requested:
            if genius_id:
                song.lyrics = Song.get_lyrics(genius_id = genius_id)
            # Get song lyrics
            if not song.lyrics:
                song.lyrics = Song.get_lyrics(song=song_name, artist=artist_name)

        print(f"Retrieved Song: {song.name}")
        return song

    @classmethod
    def get_lyrics(cls, genius_id=None, song=None, artist=None, clean_lyrics=True):
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
            genius_song = genius.search_song(name_filtered, artist)
            try:
                lyrics = genius_song.lyrics
            except:
                lyrics = ""
        if clean_lyrics:
            lyrics = Song.clean_lyrics(lyrics)
        return lyrics

    @classmethod
    def clean_lyrics(cls, lyrics):
        # TODO: This would make more sense as part of the song class?
        #       -> Would this work with non-spotify songs? Could just be a classmethod 
        # TODO: filter lyrics for tags using regex
        lyrics = re.sub(r"^.*Lyrics(\n)?", "", lyrics) # <Songname> "Lyrics" (\n)?
        lyrics = re.sub(r"\d*Embed$", "", lyrics) # ... <digits>"Embed"
        lyrics = re.sub("(\u205f|\u0435|\u2014|\u2019|) ?", " ", lyrics) # Unicode space variants # TODO: check if those are all unicode
        lyrics = re.sub(r"\n+", r"\n", lyrics) # squeezes multiple newlines into one
        lyrics = re.sub(r" +", r" ", lyrics) # squeezes multiple spaces into one
        return lyrics

    def save(self, folder, filetype):
        """
        Saves a song using the same structure used when saving albums
        Overwrites the song if it already exists
        Caveat: lyrics will always be appended to the end (for .json), this may mess up song order
        """

        path = os.path.join(folder, self.artist, self.album)
        if not os.path.exists(path):
            os.makedirs(path)
        
        if filetype == "json":
            album_path = os.path.join(path, f"{self.album}.json")
            lyrics_path = album_path.split(".json")[0] + "_lyrics.json" # TODO: probably a nicer way to do this

            if self.lyrics:
                if os.path.exists(lyrics_path):
                    try:
                        with open(lyrics_path, "r") as f:
                            lyrics_file = f.read()
                            lyrics = json.loads(lyrics_file)
                    except json.JSONDecodeError:
                        raise("Issue when trying to read .json file.") # TODO: make more descriptive
                else:
                    lyrics = {}

                lyrics[self.name] = self.lyrics
                delattr(self, "lyrics")
                with open(lyrics_path, "w") as f:
                    f.write(json.dumps(lyrics, indent=4))

            # Song / Album
            if os.path.exists(album_path):
                with open(album_path, "r") as f:
                    album_file = f.read()
                
                album_json = json.loads(album_file)
                album = Album(**album_json)    
                album.songs[self.name] = self
            else:
                # TODO: would be nice to include song_to_uri here, but need to save song_uri for that first
                # TODO: uses the wrong uri here if request is of type song. Can only get the right uri if I modify song class
                album = Album(self.uri, self.album, self.artist, songs={self.name:self})

            with open(album_path, "w") as f:
                f.write(album.toJSON())
        elif self.filetype == "csv":
            pass
        else:
            raise Exception(f'Unknown file type: \"{self.filetype}\". Please select either \"json\" or \"csv\"')



class Album(Music):
    def __init__(self, uri, name, artist, songs_to_uri=None, songs={}, missing_lyrics={}) -> None:
        self.uri = uri
        self.name = name
        self.artist = artist
        self.songs_to_uri = songs_to_uri
        self.songs = songs
        self.missing_lyrics = missing_lyrics # name:uri of missing songs

    @classmethod    # TODO: from a user standpoint it would be nice to switch lyrics_requested and features wanted (order)
    def from_spotify(cls, uri, lyrics_requested, features_wanted, use_genius_album=False):

        spotify_album = spotify.album(uri)

        artist_name = spotify_album['artists'][0]['name']
        album_name = spotify_album['name']
        songs_to_uri = {entry["name"]:entry["uri"] for entry in spotify_album['tracks']['items']}

        album = Album(uri, album_name, artist_name, songs_to_uri, songs={})

        if use_genius_album:
        # TODO: I can still use genius's albums, I just need to find a way to align it by song
        # genius albums do include the title, even if it's a bit different from the titles in spotify
        # Could maybe use that?
            genius_album = genius.search_album(album_name, artist_name)
            album.genius_ids = [track.id for track in genius_album.tracks]

            for index, (name, song_uri) in enumerate(songs_to_uri.items()):
                song = Song.from_spotify(uri=song_uri, lyrics_requested=lyrics_requested, 
                                        features_wanted=features_wanted, genius_id=album.genius_ids[index])
                album.songs[name] = song
                if not song.lyrics:
                    album.missing_lyrics[name]= song_uri # TODO: currently for logging, but could maybe find a better structure to automate
        else:
            if PARALLELIZE:
                with Pool() as pool: #uri, lyrics_requested, features_wanted
                    results = pool.map(Song.multi_run_wrapper, list(zip(songs_to_uri.values(), repeat([lyrics_requested, features_wanted]))))
                    for songname in songs_to_uri.keys():
                        album.songs[songname] = list(filter(lambda x: x.name == songname, results))[0]
                        
            else: # Keeping old method for debugging
                for name, song_uri in songs_to_uri.items():
                    song = Song.from_spotify(uri=song_uri, lyrics_requested=lyrics_requested, 
                                            features_wanted=features_wanted)
                    album.songs[name] = song
                    if not song.lyrics:
                        album.missing_lyrics[name]= song_uri
            

        return album

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)
    
    def save(self, folder, filetype):
        path = os.path.join(folder, self.artist, self.name)
        if not os.path.exists(path):
            os.makedirs(path)

        if filetype == "json":
            #TODO: not a nice way to deal with this. What if I still want to use this class after?
            #      maybe create a copy of songs / the album that gets saved and then deleted after?
            lyrics = {}
            for name, song in self.songs.items():
                lyrics[name] = song.lyrics
                delattr(song, "lyrics")
            
            delattr(self, "songs_to_uri") 
            with open(os.path.join(path, f"{self.name}.json"), "w") as f:
                f.write(self.toJSON())
            
            with open(os.path.join(path, f"{self.name}_lyrics.json"), "w") as f:
                f.write(json.dumps(lyrics, indent=4))      
        elif filetype == "csv":
            pass
        else:
            raise Exception(f'Unknown file type: \"{filetype}\". Please select either \"json\" or \"csv\"')

    


class Artist(Music):
    def __init__(self, uri, name, albums_to_uri=None, albums={}, missing_lyrics=None) -> None:
        self.uri = uri
        self.name = name
        self.albums_to_uri = albums_to_uri
        self.albums = {}
        self.missing_lyrics = {} # name:uri of missing songs 
    
    @classmethod
    def from_spotify(cls, uri, album_type, regex_filter=None, region="US", limit=50):
        spotify_artist = spotify.artist_albums(uri, album_type=album_type, country=region, limit=limit)
        artist_name = spotify.artist(uri)["name"]
        if regex_filter:
            albums_to_uri = {album["name"]:album["uri"] for album in spotify_artist['items'] if not re.search(regex_filter, album["name"], re.I)}
        else:
            albums_to_uri = {album["name"]:album["uri"] for album in spotify_artist['items']}
        artist = Artist(uri, artist_name, albums_to_uri)
        return artist

    def get_albums(self, folder, filetype, lyrics_requested, features_wanted, use_genius_album=False, limit=50):
        """
        retrieves albums using albums_to_uri
        In a seperate method as saving albums is included in this method too (safer in case of crash)
        """
        for album_number, (name, uri) in enumerate(self.albums_to_uri.items()):
            if album_number == limit:
                print("Reached maximum amount of albums that can be requested. Current limit: {limit}.\n Unfortunately the limit can't be raised past 50...")
                break

            print(f"\n {'-'*100}\n Album: {name}\n")
            album = Album.from_spotify(uri=uri, lyrics_requested=lyrics_requested, features_wanted=features_wanted,
                                        use_genius_album=use_genius_album)
            album.save(folder, filetype)
            self.albums[name] = album
            # TODO: find all missing songs across albums
                      
            

class Playlist(Music):
    def __init__(self, name) -> None:
        self.name = name
    
    @classmethod
    def from_spotify(cls, uri):
        spotify_playlist = spotify.playlist(uri)
        # TODO: implement the rest
        name = "put_spotify_playlist_name_here"
        playlist = Playlist(name)
        return playlist

    def save(self, folder, filetype):
        #TODO Implement
        pass





#----------------------------------------------------------------------------
#                               Songcrawler
#----------------------------------------------------------------------------

class Songcrawler():
    def __init__(self, lyrics_requested=True, filetype="json", use_genius_album=False, region="US", folder="data", overwrite=False, limit=50, album_type="album") -> None:
        self.lyrics_requested = lyrics_requested
        self.filetype = filetype
        self.features_wanted = ['danceability', 'energy', 'key', 'loudness',
                                'mode', 'speechiness', 'acousticness', 'instrumentalness',
                                'liveness', 'valence', 'tempo', 'time_signature', 'duration_ms']
        self.use_genius_album = use_genius_album
        self.no_lyrics = {} # trackname: spotify_uri for songs without lyrics # Todo: remember to reset after each request
        self.region = region #setting country to US arbitrarily to avoid duplicates across regions
        self.album_regex = "Deluxe|Edition"
        self.folder = folder
        self.overwrite = overwrite
        self.limit = limit
        self.album_type = album_type

    def request(self, query, lyrics_requested=None):
        """
        Make a request for a song, album, artist or playlist.
        Returns the spotify statistics and by default also the lyrics
        """
        if not lyrics_requested:
            lyrics_requested = self.lyrics_requested
        r = Request(query)
        result = Music.request(r)
        # TODO: flesh logic out here
        if isinstance(result, Artist):
            result.get_albums(folder=self.folder, filetype=self.filetype, lyrics_requested=lyrics_requested,
                         features_wanted=r.features_wanted, use_genius_album=self.use_genius_album, limit=self.limit)
        else:
            result.save(self.folder, self.filetype)
        return result
        
#----------------------------------------------------------------------------
#                               Request
#----------------------------------------------------------------------------

class Request(Songcrawler):
    def __init__(self, query) -> None:
        super().__init__()
        # TODO: add param for: genius_id
        self.query = query
        self.type = self.get_request_type(query)
        
        if self.type == "spotify":
            self.spotify_type = self.get_spotify_type()
        else:
            self.spotify_type = None
    
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

    def get_spotify_type(self):
        """
        Returns the type of resource the self.query requests i.e. song, album, artist, playlist
        """
        uri = self.query.split(":")[1]    
        return uri


if __name__=="__main__":
    main()
    # sc = Songcrawler()
    # artist = sc.request("spotify:artist:0fA0VVWsXO9YnASrzqfmYu")
    # album = sc.request("spotify:album:6dVCpQ7oGJD1oYs2fv1t5M")#, lyrics_requested=False)
    # song = sc.request("spotify:track:5CBEzaNEuv3OO32kZoXgOX")
    # sc.request("8150537")
    # sc.request("spotify:album:6dVCpQ7oGJD1oYs2fv1t5M")
    #print(artist)
    # BFIAFL genius_ids:
    # [8150565, 8150537, 8150538, 8099567, 8150539, 8150540, 8150541, 8150542, 8150543, 8150544, 8150545]

# If it doesn't find anything then the lyrics are just empty e.g. New York City Rage Fest on Indicud
# Would be cool if it included the song / album uri for debugging
