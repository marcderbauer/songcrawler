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
import csv



#----------------------------------------------------------------------------
#                               ARGPARSE
#----------------------------------------------------------------------------
# TODO: check best practices regarding spaces / underscores
parser = argparse.ArgumentParser(description='Gather Spotify statistics and Genius lyrics.')
parser.add_argument("query", metavar="Spotify URI, Genius ID or Songname", type=str, help="Either a Spotify uri, a songname or a genius id")
parser.add_argument("--filetype", type=str, default=".json", help="Filetype to save output as. Possible options: .json, .csv")
parser.add_argument("--genius", default=False, action='store_true', help="Lists alternative Genius ids when main argument is a songname")
parser.add_argument("--no_lyrics", default=False, action='store_true', help="Skips gathering lyrics and only queries spotify statistics.")
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
                    album = Album.from_spotify(request.query, request.lyrics_requested, request.features_wanted)
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

    @classmethod
    def album_folder(cls, base_folder, artist_name, album_name):
        """
        Creates artist/album/ folder it it doesn't exist yet.
        Returns the path to that folder
        """
        path = os.path.join(base_folder, artist_name, album_name)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

class Song(Music):
    def __init__(self, uri, song_name, album_name, artist_name, audio_features, feature_artists = None, lyrics=None) -> None:
        self.uri = uri
        self.song_name = song_name
        self.album_name = album_name
        self.artist_name = artist_name
        self.audio_features = audio_features
        self.feature_artists = feature_artists
        self.lyrics = lyrics
    
    def __repr__(self) -> str:
        printstring = f"""
        Name:           {self.song_name}
        Album:          {self.album_name}
        Artist:         {self.artist_name}
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

        song = Song(uri=uri, song_name=song_name, album_name=album_name, artist_name=artist_name, 
                    audio_features=audio_features, feature_artists=feature_artists)

        if lyrics_requested:
            if genius_id:
                song.lyrics = Song.get_lyrics(genius_id = genius_id)
            # Get song lyrics
            if not song.lyrics:
                song.lyrics = Song.get_lyrics(song_name=song_name, artist_name=artist_name)

        print(f"Retrieved Song: {song.song_name}")
        return song
    
    @classmethod
    def get_lyrics(cls, genius_id=None, song_name=None, artist_name=None, clean_lyrics=True):
        """
        Takes a genius_id or song name and returns the lyrics for it
        """
        if genius_id:
            pass
        elif (song_name == None or artist_name == None):
            raise Exception("requires either a genius_id or a songname and artist")
        
        if genius_id:
                lyrics = genius.search_song(song_id=genius_id).lyrics # TODO: should try without genius id if this fails
        else:
            name_filtered = re.sub(r" *(\(.*\)|feat\.?.*|ft\..*)", "", song_name)
            genius_song = genius.search_song(title=name_filtered, artist=artist_name)
            try:
                lyrics = genius_song.lyrics
            except:
                lyrics = ""

        if clean_lyrics:
            lyrics = Song.clean_lyrics(lyrics)

        return lyrics

    #TODO: would this make sense to not have as class method? Depends on genius class (i.e. without spotify i.g.)
    @classmethod
    def clean_lyrics(cls, lyrics):
        lyrics = re.sub(r"^.*Lyrics(\n)?", "", lyrics) # <Songname> "Lyrics" (\n)?
        lyrics = re.sub(r"\d*Embed$", "", lyrics) # ... <digits>"Embed"
        lyrics = re.sub("(\u205f|\u0435|\u2014|\u2019) ?", " ", lyrics) # Unicode space variants # TODO: check which characters they correspond to
        lyrics = re.sub(r"\n+", r"\n", lyrics) # squeezes multiple newlines into one
        lyrics = re.sub(r" +", r" ", lyrics) # squeezes multiple spaces into one
        return lyrics
    
    def __iter__(self):
        return iter([self.uri, self.song_name, self.album_name, self.artist_name, *self.audio_features.values(), self.feature_artists, self.lyrics])

    def _get_csv_header(self):
        return ["uri", "song_name", "album_name", "artist_name", *self.audio_features.keys(), "feature_artists", "lyrics"]

    # TODO: add some tests to this
    def save(self, folder, filetype, overwrite):
        """
        Saves a song using the same structure used when saving albums
        Overwrites the song if it already exists
        Caveat: lyrics will always be appended to the end (for .json), this may mess up song order
        """
        
        path = Music.album_folder(folder, artist_name = self.artist_name, album_name = self.album_name)
        album_path = os.path.join(path, f"{self.album_name}{filetype}")


        # if path exists -> Doesn't mean song exists!
        if os.path.exists(album_path):
            album = Album.from_file(album_path)
            if self.song_name in album.songs.keys():
                if not overwrite:
                    print(f"\nSong \"{self.song_name}\" exists already.\nPlease use the --overwrite flag to save it.\n")
                    quit()
            else:
                album.songs[self.song_name] = self
        else:
            album = Album(uri=None, album_name=self.album_name, artist_name=self.artist_name)
        
        # write album to file. Call album.save for this 
        album.save(folder=folder, filetype=filetype, overwrite=overwrite)


class Album(Music):
    def __init__(self, uri, album_name, artist_name, songs_to_uri=None, songs={}, missing_lyrics={}) -> None:
        self.uri = uri
        self.album_name = album_name
        self.artist_name = artist_name
        self.songs_to_uri = songs_to_uri
        self.songs = songs
        self.missing_lyrics = missing_lyrics # name:uri of missing songs

    @classmethod    # TODO: from a user standpoint it would be nice to switch lyrics_requested and features wanted (order)
    def from_spotify(cls, uri, lyrics_requested, features_wanted):

        spotify_album = spotify.album(uri)

        artist_name = spotify_album['artists'][0]['name']
        album_name = spotify_album['name']
        songs_to_uri = {entry["name"]:entry["uri"] for entry in spotify_album['tracks']['items']}

        album = Album(uri = uri, album_name = album_name, artist_name = artist_name, songs_to_uri = songs_to_uri, songs={})

        if PARALLELIZE:
            # TODO: add try/except/final(?)
            try:
                with Pool() as pool: #uri, lyrics_requested, features_wanted
                    results = pool.map(Song.multi_run_wrapper, list(zip(songs_to_uri.values(), repeat([lyrics_requested, features_wanted]))))
                    results = {song.song_name:song for song in results}
                    for songname in songs_to_uri.keys():
                        album.songs[songname] = results[songname]

            except Exception as e:
                # TODO This could be handled better in the future, but should do the trick for now
                print(f"Error while querying album {album_name}.\n Error message under errors.txt")
                with open ("errors.txt", "a") as f:
                    f.write(e)
                    
        else: # Keeping old method for debugging
            for name, song_uri in songs_to_uri.items():
                song = Song.from_spotify(uri=song_uri, lyrics_requested=lyrics_requested, 
                                        features_wanted=features_wanted)
                album.songs[name] = song
                if not song.lyrics:
                    album.missing_lyrics[name]= song_uri
    
        return album

    @classmethod
    def from_file(cls, path):
        assert os.path.exists(path)
        filetype = path.split(".")[-1]
        
        if filetype == "json":
            with open(path, "r") as f:
                album_file = f.read()
                album_json = json.loads(album_file)
                album = Album(**album_json)    
            return album

        elif filetype == "csv":
            with open(path, "r") as f:
                csv_reader = csv.reader(f, delimiter=",")
                header = next(csv_reader)
                features = header[header.index('artist_name')+1: header.index('feature_artists')]
                songs = {}
                for row in csv_reader:
                    songdict = dict(zip(header, row))
                    songdict["audio_features"] = {name: value for name, value in songdict.items() if name in features}
                    songdict = {name: value for name, value in songdict.items() if name not in features}
                    song = Song(**songdict)
                    songs[song.song_name] = song
            album = Album(uri=None, album_name=songdict["album_name"], artist_name=songdict["artist_name"])
            album.songs = songs
            return album

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)
    
    def save(self, folder, filetype, overwrite):
        path = Music.album_folder(base_folder=folder, artist_name = self.artist_name, album_name = self.album_name)
        album_path = os.path.join(path, f"{self.album_name}{filetype}")
        if filetype == ".json":
            #TODO: delattr is not a nice way to deal with this. What if I still want to use this class after?
            #      maybe create a copy of songs / the album that gets saved and then deleted after?
            lyrics = {}
            for name, song in self.songs.items():
                lyrics[name] = song.lyrics
                delattr(song, "lyrics")
            
            delattr(self, "songs_to_uri") 
            with open(album_path, "w") as f:
                f.write(self.to_json())
            
            with open(os.path.join(path, f"{self.album_name}_lyrics.json"), "w") as f:
                f.write(json.dumps(lyrics, indent=4)) 

        elif filetype == ".csv":
            header = list(self.songs.values())[0]._get_csv_header() # A bit ugly to retrieve it like this, but can't make it classmethod because features wanted is attribute
            with open(album_path, "w") as stream:
                writer = csv.writer(stream)
                writer.writerow(i for i in header)
                writer.writerows(self.songs.values())

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
        artist = Artist(uri=uri, artist_name=artist_name, albums_to_uri=albums_to_uri)
        return artist

    def get_albums(self, folder, filetype, lyrics_requested, features_wanted, limit=50):
        """
        retrieves albums using albums_to_uri
        In a seperate method as saving albums is included in this method too (safer in case of crash)
        """
        for album_number, (name, uri) in enumerate(self.albums_to_uri.items()):
            if album_number == limit:
                print("Reached maximum amount of albums that can be requested. Current limit: {limit}.\n Unfortunately the limit can't be raised past 50...")
                break

            print(f"\n {'-'*100}\n Album: {name}\n")
            album = Album.from_spotify(uri=uri, lyrics_requested=lyrics_requested, features_wanted=features_wanted)
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

    def save(self, folder, filetype, overwrite):
        #TODO Implement
        pass





#----------------------------------------------------------------------------
#                               Songcrawler
#----------------------------------------------------------------------------

class Songcrawler():
    def __init__(self, lyrics_requested=True, filetype="json", region="US", folder="data", overwrite=False, limit=50, album_type="album") -> None:
        self.lyrics_requested = lyrics_requested
        self.filetype = filetype
        self.features_wanted = ['danceability', 'energy', 'key', 'loudness',
                                'mode', 'speechiness', 'acousticness', 'instrumentalness',
                                'liveness', 'valence', 'tempo', 'time_signature', 'duration_ms']
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
                         features_wanted=self.features_wanted, limit=self.limit)
        else:
            result.save(self.folder, self.filetype, overwrite=self.overwrite)
        return result
        
#----------------------------------------------------------------------------
#                               Request
#----------------------------------------------------------------------------

class Request(Songcrawler):
    def __init__(self, query: str) -> None:
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
