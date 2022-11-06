import re
import csv
import json
import os
import lyricsgenius
import spotipy
from itertools import repeat
from multiprocessing import Pool
from abc import ABC, abstractmethod
from spotipy.oauth2 import SpotifyClientCredentials
from copy import deepcopy
from utils import file_empty

##########################################################################################
#                                 ____       _               
#                                / ___|  ___| |_ _   _ _ __  
#                                \___ \ / _ \ __| | | | '_ \ 
#                                 ___) |  __/ |_| |_| | |_) |
#                                |____/ \___|\__|\__,_| .__/ 
#                                                     |_|                                         
# ########################################################################################   

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



# ########################################################################################   
#                                 __  __           _      
#                                |  \/  |_   _ ___(_) ___ 
#                                | |\/| | | | / __| |/ __|
#                                | |  | | |_| \__ \ | (__ 
#                                |_|  |_|\__,_|___/_|\___|
# ########################################################################################                             

# Each of those should have the method to convert them to strings (__repr__?) and how to save them to a file
# Could maybe actually use an abstract class and make them inherit this?

class Music(ABC):
    @abstractmethod
    def from_spotify(uri):
        print("implement me")
    
    @classmethod
    def request(cls, request):
        if request.type == "spotify": # if request.spotify_type ? 
            match request.get_spotify_type(): # TODO This should be an attribute of request really
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
                    playlist = Playlist.from_spotify(uri=request.query, save_every=request.save_every)
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
    
    
    #def _save_multi(self, )

# ########################################################################################   
#             __  __           _         ____      _ _           _   _             
#            |  \/  |_   _ ___(_) ___   / ___|___ | | | ___  ___| |_(_) ___  _ __  
#            | |\/| | | | / __| |/ __| | |   / _ \| | |/ _ \/ __| __| |/ _ \| '_ \ 
#            | |  | | |_| \__ \ | (__  | |__| (_) | | |  __/ (__| |_| | (_) | | | |
#            |_|  |_|\__,_|___/_|\___|  \____\___/|_|_|\___|\___|\__|_|\___/|_| |_|
#                                                                       
# ########################################################################################   

class MusicCollection(Music):
    def __init__(self, songs_to_uri, songs, missing_lyrics, collection_name) -> None:
        # Not a very nice solution, but want to keep name as self.playlist_name and self.album name
        if collection_name:
            self.collection_name = collection_name
        else:
            self.collection_name = self.playlist_name if isinstance(self, Playlist) else self.album_name 
        super().__init__()
    
    @classmethod
    def from_file(cls, path, Class):
        assert os.path.exists(path)
        assert issubclass(Class, cls)
        filepath, filetype = os.path.splitext(path)
        
        if filetype == ".json":
            # Collection
            with open(path, "r") as f:
                collection_file = f.read()
                collection_json = json.loads(collection_file)
                songs = {name: Song(song["uri"], song["song_name"], song["album_name"], 
                        song["artist_name"], song["audio_features"]) for name,song in collection_json["songs"].items()}
                collection_json["songs"] = songs
                collection = Class(**collection_json)    
            
            # Lyrics
            lyric_path = filepath + f"_lyrics.json"
            with open(lyric_path, "r") as f:
                lyrics_file = f.read()
                lyric_json = json.loads(lyrics_file)
            
            for song_name in collection.songs.keys():
                if song_name not in lyric_json:
                    print(f"Lyrics for {song_name} missing.")
                    continue
                collection.songs[song_name].lyrics = lyric_json[song_name]


            return collection

        elif filetype == ".csv":
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
            collection = Class(uri=None, album_name=songdict["album_name"], artist_name=songdict["artist_name"])
            collection.songs = songs
            return collection
    
    def _pool(self, lyrics_requested, features_wanted):
        """
        Takes a song_to_uri dict and returns {song_name: Song} 
        """
        songs = {}
        if PARALLELIZE:      
            try:
                with Pool() as pool: #uri, lyrics_requested, features_wanted
                    results = pool.map(Song.multi_run_wrapper, list(zip(self.songs_to_uri.values(), repeat([lyrics_requested, features_wanted]))))
                    results = {song.song_name:song for song in results}
                    for songname in self.songs_to_uri.keys():
                        songs[songname] = results[songname]

            except Exception as e:
                # TODO This could be handled better in the future, but should do the trick for now
                self.missing_lyrics.update(self.songs_to_uri)
                print(f"Error while querying album {playlist_name}.\n Error message under errors.txt")
                with open ("errors.txt", "a") as f:
                    f.write(str(e))

        else: # Keeping old method for debugging
            for playlist_name, song_uri in self.songs_to_uri.items():
                song = Song.from_spotify(uri=song_uri, lyrics_requested=lyrics_requested, 
                                        features_wanted=features_wanted)
                songs[playlist_name] = song
                #TODO figure out how to handle missing lyrics? maybe return them too?
                if not song.lyrics:
                    self.missing_lyrics[playlist_name]= song_uri
        
        return songs
    
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)
    

    def _init_files(self, album_path, filetype, overwrite):
        """
        Initialises empty files / an empty file if set to overwrite.
        If it succeeds: returns True, else False.
        """
        if filetype == ".csv":
            paths = [f"{album_path}.csv"]
        elif filetype == ".json":
            paths = [f"{album_path}.json", f"{album_path}_lyrics.json"]
        else:
            raise Exception(f'Unknown file type: \"{filetype}\". Please select either \".json\" or \".csv\"')

        for path in paths:
            if not file_empty(path=path):
                if not overwrite:
                    print(f"\n{path} already exists.\n\nUse '--overwrite' to overwrite\n")
                    return False
            open(path, "w").close()
        return True
    

    def _write(self, path, mode, filetype):
        assert mode in ["w", "a"], "Filemode needs to be either 'a' for append or 'w' for write"
        album_path = os.path.join(path, f"{self.collection_name}{filetype}")
        if filetype == ".json":
            # Using a copy to remove attributes for saving to file while keeping original intact
            copy = deepcopy(self)
            lyrics = {}

            for name, song in copy.songs.items():
                lyrics[name] = song.lyrics
                delattr(song, "lyrics")
            delattr(copy, "songs_to_uri")

            with open(album_path, mode=mode) as f:
                f.write(copy.to_json())
            
            with open(os.path.join(path, f"{self.collection_name}_lyrics.json"), "w") as f:
                f.write(json.dumps(lyrics, indent=4)) 
            
            del copy #likely don't need this, but doesn't hurt

        elif filetype == ".csv":
            header = list(self.songs.values())[0]._get_csv_header() # A bit ugly to retrieve it like this, but can't make it classmethod because features wanted is attribute
            with open(album_path, mode=mode) as stream:
                writer = csv.writer(stream)
                writer.writerow(i for i in header)
                writer.writerows(self.songs.values())

        else:
            raise Exception(f'Unknown file type: \"{filetype}\". Please select either \".json\" or \".csv\"')




# ########################################################################################   
#                                 ____                    
#                                / ___|  ___  _ __   __ _ 
#                                \___ \ / _ \| '_ \ / _` |
#                                 ___) | (_) | | | | (_| |
#                                |____/ \___/|_| |_|\__, |
#                                                   |___/ 
# ########################################################################################   

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
        Found Lyrics:   {f"{self.lyrics[:50]}..." if self.lyrics else "No :("}    
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
    def save(self, folder, filetype, overwrite, lyrics_requested=None, features_wanted=None):
        """
        Saves a song using the same structure used when saving albums
        Overwrites the song if it already exists
        Caveat: lyrics will always be appended to the end, this may mess up song order
        """
        
        path = Music.album_folder(folder, artist_name = self.artist_name, album_name = self.album_name)
        album_path = os.path.join(path, f"{self.album_name}{filetype}")


        # if path exists -> Doesn't mean song exists!
        if os.path.exists(album_path):
            album = MusicCollection.from_file(album_path, Class=Album)
            if self.song_name in album.songs.keys() and not overwrite:
                print(f"\nSong \"{self.song_name}\" exists already.\nPlease use the --overwrite flag to save it.\n")
                quit()
            else:
                album.songs[self.song_name] = self
        else:
            album = Album(uri=None, album_name=self.album_name, artist_name=self.artist_name)
        
        # write album to file. Call album.save for this 
        album.save(folder=folder, filetype=filetype, overwrite=overwrite)


# ########################################################################################   
#                                _    _ _                     
#                               / \  | | |__  _   _ _ __ ___  
#                              / _ \ | | '_ \| | | | '_ ` _ \ 
#                             / ___ \| | |_) | |_| | | | | | |
#                            /_/   \_\_|_.__/ \__,_|_| |_| |_|
#                                                           
# ########################################################################################   

class Album(MusicCollection):
    def __init__(self, uri, album_name, artist_name, songs_to_uri=None, songs={}, missing_lyrics={}, collection_name=None) -> None:
        self.uri = uri
        self.album_name = album_name
        self.artist_name = artist_name
        self.songs_to_uri = songs_to_uri
        self.songs = songs
        self.missing_lyrics = missing_lyrics # name:uri of missing songs
        super().__init__(songs_to_uri=songs_to_uri, songs=songs, missing_lyrics=missing_lyrics, collection_name=collection_name)

    @classmethod    # TODO: from a user standpoint it would be nice to switch lyrics_requested and features wanted (order)
    def from_spotify(cls, uri, lyrics_requested, features_wanted):

        spotify_album = spotify.album(uri)

        artist_name = spotify_album['artists'][0]['name']
        album_name = spotify_album['name']
        songs_to_uri = {entry["name"]:entry["uri"] for entry in spotify_album['tracks']['items']}

        album = Album(uri = uri, album_name = album_name, artist_name = artist_name, songs_to_uri = songs_to_uri, songs={})
        songs = album._pool(lyrics_requested=lyrics_requested, features_wanted=features_wanted)
        album.songs.update(songs)
    
        return album

    @classmethod
    def from_file(cls, path):
        assert os.path.exists(path)
        filepath, filetype = os.path.splitext(path)
        
        if filetype == ".json":
            # Album
            with open(path, "r") as f:
                album_file = f.read()
                album_json = json.loads(album_file)
                songs = {name: Song(song["uri"], song["song_name"], song["album_name"], 
                        song["artist_name"], song["audio_features"]) for name,song in album_json["songs"].items()}
                album_json["songs"] = songs
                album = Album(**album_json)    
            
            # Lyrics
            lyric_path = filepath + f"_lyrics.json"
            with open(lyric_path, "r") as f:
                lyrics_file = f.read()
                lyric_json = json.loads(lyrics_file)
            
            for song_name in album.songs.keys():
                if song_name not in lyric_json:
                    print(f"Lyrics for {song_name} missing.")
                    continue
                album.songs[song_name].lyrics = lyric_json[song_name]


            return album

        elif filetype == ".csv":
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


    def save(self, folder, filetype, overwrite, lyrics_requested=None, features_wanted=None):
        path = Music.album_folder(base_folder=folder, artist_name = self.artist_name, album_name = self.album_name)
        base_path = os.path.join(path, self.album_name) # TODO: could get merged into Music.album_folder if the funciton isn't used anywhere else (should rename tho)
        write_allowed = self._init_files(album_path=base_path, filetype=filetype, overwrite=overwrite)
        if write_allowed:
            self._write(path=path, mode="w", filetype=filetype)
        


# ########################################################################################   
#                                 _         _   _     _   
#                                / \   _ __| |_(_)___| |_ 
#                               / _ \ | '__| __| / __| __|
#                              / ___ \| |  | |_| \__ \ |_ 
#                             /_/   \_\_|   \__|_|___/\__|
#                                                        
# ########################################################################################   

class Artist(Music):
    def __init__(self, uri, artist_name, albums_to_uri=None, albums={}, missing_lyrics=None) -> None:
        self.uri = uri
        self.artist_name = artist_name
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

    def get_albums(self, folder, filetype, lyrics_requested, features_wanted, overwrite, limit=50):
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
            album.save(folder, filetype, overwrite=overwrite)
            self.albums[name] = album
            # TODO: find all missing songs across albums
                      
# ########################################################################################   
#                            ____  _             _ _     _   
#                           |  _ \| | __ _ _   _| (_)___| |_ 
#                           | |_) | |/ _` | | | | | / __| __|
#                           |  __/| | (_| | |_| | | \__ \ |_ 
#                           |_|   |_|\__,_|\__, |_|_|___/\__|
#                                          |___/                                                                
# ########################################################################################               

class Playlist(MusicCollection):
    def __init__(self, playlist_name, save_every, offset, songs_to_uri=None, songs={}, missing_lyrics={}, songs_to_uri_all={}) -> None:
        self.playlist_name = playlist_name
        self.save_every = save_every
        self.offset = offset
        self.songs_to_uri = songs_to_uri
        self.songs = songs
        self.missing_lyrics = missing_lyrics # name:uri of missing songs
        self.songs_to_uri_all = songs_to_uri_all
        super().__init__(songs_to_uri=songs_to_uri, songs=songs, missing_lyrics=missing_lyrics, collection_name=playlist_name)

    @classmethod
    def from_spotify(cls, uri, save_every):
        spotify_playlist = spotify.playlist(playlist_id=uri)
        spotify_playlist_items = spotify.playlist_items(uri, limit=save_every)
        playlist_name = spotify_playlist['name']
        songs_to_uri =  {entry["track"]["name"]:entry["track"]["uri"] for entry in spotify_playlist_items['items']}
        

        playlist = Playlist(playlist_name=playlist_name, save_every=save_every, offset=save_every, 
                            songs_to_uri=songs_to_uri, songs={}, missing_lyrics={}, songs_to_uri_all={})
        
        return playlist

    def save(self, folder, filetype, overwrite, lyrics_requested, features_wanted):

        path = Music.album_folder(base_folder=folder, artist_name="_Playlists", album_name=self.playlist_name)
        base_path = os.path.join(path, self.playlist_name) # TODO: could get merged into Music.album_folder if the funciton isn't used anywhere else (should rename tho)
        save = self._init_files(album_path=base_path, filetype=filetype, overwrite=overwrite)
        #TODO Implement
        # Would be nice to have some mechanism to deal with long playlists
        # maybe save every 50 songs?

        # seems like spotify has a limit of requesting 100 songs?

        # TODO: Would be nice if this included all the iterating through the playlist
        # No need to handle this on the outside 
        # while True
        while save:
        #   query songs from song_to_uri using pool
        #   Maybe make Music.pool(song_to_uri, lyrics_requested, features_wanted) -> {song.song_name: song}
            songs = self._pool(features_wanted=features_wanted, lyrics_requested=lyrics_requested)
            self.songs.update(songs) 
            self.songs_to_uri_all.update(self.songs_to_uri)
        #   save songs to file in append mode
            self._write(path=path, filetype=filetype, mode="a")
            self._next()
        #   rest here as Playlist.next?
        #   increment self.offset
        #   get next batch from spotify playlist
        #       makes sense to have a local song_to_uri and a general self.song_to_uri for all songs?
        #   
        #   if len(songs_to_uri) == self.save_every:
        #   some other error criterium maybe? if no songs in next batch?
            if not self.songs_to_uri:
                break
        # TODO: almost identical as in Album(), maybe could make this a method in Music class?
    

    def _next(self):
        # increments self.offset by self.limit
        self.offset += self.save_every
        # gathers the next set of tracks
        self.songs_to_uri = spotify.playlist_items(self.uri, limit=self.save_every, offset=self.offset)
