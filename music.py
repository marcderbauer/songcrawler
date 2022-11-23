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
from utils import delete_dir, file_empty, overwrite_dir, Path
import glob

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
        pass
    
    @classmethod
    def request(cls, request):
        if request.type == "spotify": # if request.spotify_type ? 
            match request.get_spotify_type():
                case "track":
                    song = Song.from_spotify(request.query, lyrics_requested=request.lyrics_requested, 
                                features_wanted=request.features_wanted)#, genius_id=genius_id) TODO: figure out genius ID here
                    return song

                case "album":
                    album = Album.from_spotify(request.query, request.lyrics_requested, request.features_wanted)
                    return album

                case "artist":
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

        elif request.get_ids:
            # Would make sense to move this to setup, but only really required in this specific case
            api = lyricsgenius.API(os.environ["GENIUS_ACCESS_TOKEN"])
            search = api.search_songs(request.query)
            id_to_artist_song = {hit['result']['id']:(hit['result']['artist_names'], hit['result']['title']) for hit in search['hits']}
            print(json.dumps(id_to_artist_song, indent=4, ensure_ascii=False))
            quit()

        else:
            result = Song.get_lyrics(request.query)
                # TODO: figure out how to save this
            
    @classmethod
    def search(cls, query, region="US"):
        """
        Searches spotify 
        """
        query_dict = Music.split_search(query)
        
        if "search" in query_dict:
            print(f"No query parameters passed. Searching for track {query_dict['query']} ...\n")
            songs = spotify.search(q=query_dict["query"], market=region)
            song = songs['tracks']['items'][0] # Picking first song, TODO: make interactive at some point
            uri = song['uri']
            song_name = song['name']
            album_name = song['album']['name']
            artist_name = song['artists'][0]['name']
            print_string = f"""
                song:   {song_name}
                album:  {album_name}
                artist: {artist_name}
                uri:    {uri}
                """ 
            print(print_string)
            return uri

        elif "track" in query_dict:
            songs = spotify.search(q=query_dict["query"], type="track", market=region)
            print(f"Retrieved URI of song \"{songs['tracks']['items'][0]['name']}\"")
            return songs['tracks']['items'][0]['uri']
            
        elif "album" in query_dict:
            albums = spotify.search(q=query_dict["query"], type="album", market=region)
            print(f"Retrieved URI of album \"{albums['albums']['items'][0]['name']}\"")
            return albums['albums']['items'][0]['uri']

        elif "playlist" in query_dict:
            playlists = spotify.search(q=query_dict["query"], type="playlist", market=region)
            print(f"Retrieved URI of playlist \"{playlists['playlists']['items'][0]['name']}\"")
            return playlists['playlists']['items'][0]['uri']

        elif "artist" in query_dict:
            artists = spotify.search(q=query_dict["query"], type="artist", market=region)
            print(f"Retrieved URI of artist \"{artists['artists']['items'][0]['name']}\"")
            return artists['artists']['items'][0]['uri']
        else:
            raise Exception(f"Invalid query dict passed to Music.search():\n{query_dict}")

        return #spotify.search(query, type=type, market=region)
    
    # @classmethod
    # def search_dict(cls, sd, region="US"):
    #     if "artist" in sd.keys():
    #         result = spotify.search(sd["artist"], type="artist", market=region)
    #         artist_uri = ['artists']['items'][0]['uri']

    @classmethod
    def split_search(cls, s):
        """
        Takes a search string and splits it by keywords
        Returns a dictionary {keyword: value}
        If no keywords are found it returns a dictionary with a single element "search" and the query as value.
        d["query"] is the original query s.
        Loosely based on this:
        https://stackoverflow.com/questions/61056453/split-string-based-on-given-words-from-list
        """
        l = ["artist", "track", "album", "playlist"]
        s = re.sub(":", " ", s)
        m = re.split(rf"({'|'.join(l)})", s, re.I)
        m = [i.strip() for i in m if i] # removes empty strings and whitespaces
        keyword = m[::2]
        value = m[1::2]
        if value:
            d = dict(zip(keyword, value))
        else:
            d = {"search":keyword[0]}
        d["query"] = s
        return d

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
        # TODO: logic can probably be cleaned up a bit
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
        Caveat: lyrics will always be appended to the end, this may mess up song order
        """
        path = Path(folder=folder, artist=self.artist_name, album=self.album_name)
        filepath = path.csv if filetype == ".csv" else path.json

        if os.path.exists(filepath):
            album = MusicCollection.from_file(filepath, Class=Album)
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
        # TODO: currently have three attributes passed here which are unused. What to do?
        # TODO: can this be removed?
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
        
        else:
            raise Exception(f'Unknown file type: \"{filetype}\". Please select either \".json\" or \".csv\"')
    
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
                print(f"Error while querying album {self.collection_name}.\nError message under errors.txt")
                with open ("errors.txt", "a") as f:
                    f.write(str(e))

        else: # Keeping old method for debugging
            for playlist_name, song_uri in self.songs_to_uri.items():
                song = Song.from_spotify(uri=song_uri, lyrics_requested=lyrics_requested, 
                                        features_wanted=features_wanted)
                songs[playlist_name] = song
                if not song.lyrics:
                    self.missing_lyrics[playlist_name]= song_uri
        
        return songs
    
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    
    @abstractmethod
    def get_path(self, base_folder, artist_name, album_name):
        return Path(folder=base_folder, artist=artist_name, album=album_name)

    def _init_files(self, path, filetype, overwrite):
        """
        Initialises empty files / an empty file if set to overwrite.
        If it succeeds: returns True, else False.
        # TODO: check if empty files still need to be initialised. Especially if it's not overwrite!!!
        """
        if filetype == ".csv":
            filepaths = [path.csv]
        elif filetype == ".json":
            overwrite_dir(path.temp)
            filepaths = [path.json, path.lyrics]
        else:
            raise Exception(f'Unknown file type: \"{filetype}\". Please select either \".json\" or \".csv\"')

        if not os.path.exists(path.album):
            os.makdirs(path.album)

        for filepath in filepaths:
            if not file_empty(path=filepath):
                if not overwrite:
                    print(f"\n{filepath} already exists.\n\nUse '--overwrite' to overwrite\n")
                    return False
            open(filepath, "w").close() # overwrites all contents
        return True
    
    @abstractmethod
    def _write_csv(self, path, mode):
        header = list(self.songs.values())[0]._get_csv_header() # A bit ugly to retrieve it like this, but can't make it classmethod because features wanted is attribute
        with open(path.csv, mode=mode) as stream:
            writer = csv.writer(stream)
            if file_empty(path.csv): #Only writes the first time
                writer.writerow(i for i in header)
            writer.writerows(self.songs.values())

    def _write(self, path: Path, filetype, temp=False):
        if filetype == ".json":
            # Using a copy to remove attributes for saving to file while keeping original intact
            copy = deepcopy(self)
            lyrics = {}

            for name, song in copy.songs.items():
                lyrics[name] = song.lyrics
                delattr(song, "lyrics")
            delattr(copy, "songs_to_uri")

            if temp:
                album_path, lyrics_path = path.get_temp_paths()
            else:
                album_path = path.json
                lyrics_path= path.lyrics

            with open(album_path, mode="w") as f:
                f.write(copy.to_json())
            
            with open(lyrics_path, "w") as f:
                f.write(json.dumps(lyrics, indent=4, ensure_ascii=False)) 
            
            del copy #likely don't need this, but doesn't hurt

        elif filetype == ".csv":
            self._write_csv(path=path)

        else:
            raise Exception(f'Unknown file type: \"{filetype}\". Please select either \".json\" or \".csv\"')



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
        collection_name = collection_name if collection_name else album_name
        super().__init__(songs_to_uri=songs_to_uri, songs=songs, missing_lyrics=missing_lyrics, collection_name=collection_name)

    def get_path(self, folder):
        return super().get_path(base_folder=folder, artist_name=self.artist_name, album_name=self.album_name)

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

    def _write_csv(self, path):
        return super()._write_csv(path=path, mode="w")

    def save(self, folder, filetype, overwrite):
        path = self.get_path(folder)
        write_allowed = self._init_files(path=path, filetype=filetype, overwrite=overwrite)
        if write_allowed:
            self._write(path=path, filetype=filetype)
        delete_dir(path.temp) # TODO shouldn't be generated for Albums, need to figure out how to avoid this


# ########################################################################################   
#                            ____  _             _ _     _   
#                           |  _ \| | __ _ _   _| (_)___| |_ 
#                           | |_) | |/ _` | | | | | / __| __|
#                           |  __/| | (_| | |_| | | \__ \ |_ 
#                           |_|   |_|\__,_|\__, |_|_|___/\__|
#                                          |___/                                                                
# ########################################################################################               

class Playlist(MusicCollection):
    def __init__(self, uri, playlist_name, save_every, offset, songs_to_uri=None, songs={}, missing_lyrics={}, songs_to_uri_all={}, collection_name=None) -> None:
        self.uri = uri
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
        

        playlist = Playlist(uri=uri, playlist_name=playlist_name, save_every=save_every, offset=0, 
                            songs_to_uri=songs_to_uri, songs={}, missing_lyrics={}, songs_to_uri_all={})
        
        return playlist
    
    def get_path(self, base_folder):
        return super().get_path(base_folder, artist_name="_Playlists", album_name=self.playlist_name)

    def _combine_temp(self, path):
        """
        Combines the files saved in path/.tmp/ into one big playlist and writes it to a file
        """
        files = glob.glob(os.path.join(path, f".tmp/*{self.playlist_name}[!_lyrics]*")) #!_lyrics doesn't seem to work
        files = [file for file in files if not re.search("_lyrics.*", file)]
        files = sorted(files)

        songs = {}
        for file in files:
            mc = MusicCollection.from_file(file, Playlist)
            songs.update(mc.songs)
        playlist_final = Playlist(uri=self.uri, playlist_name=self.playlist_name, save_every=self.save_every, offset=self.offset, songs_to_uri=self.songs_to_uri_all,
                                    songs = songs, missing_lyrics=self.missing_lyrics, songs_to_uri_all=self.songs_to_uri_all, collection_name=self.playlist_name)
        return playlist_final
        
    def _write_csv(self, path):
        return super()._write_csv(path, mode="a")


    def save(self, folder, filetype, overwrite, lyrics_requested, features_wanted):
        """
        Queries and saves songs of a playlist.
        Songs are queried in batches of size self.save_every and saved in path/.tmp.
        Finally they are all merged to a regular .json or .csv file
        """
        path = self.get_path(folder)
        save = self._init_files(path = path, filetype=filetype, overwrite=overwrite)
        
        while save:
            songs = self._pool(features_wanted=features_wanted, lyrics_requested=lyrics_requested)
            self.songs = songs 
            self.songs_to_uri_all.update(self.songs_to_uri)
            
            if filetype == ".json":
                self._write(path=path, filetype=filetype, temp=True)
            else:
                self._write(path=path, filetype=filetype)
            self._next()

            if not self.songs_to_uri:
                delete_tmp = True
                break
        
        if filetype == ".json":
            combined = self._combine_temp(path.album)
            combined._write(path = path, filetype=filetype)
            if delete_tmp:
                delete_dir(path.temp)
    

    def _next(self):
        self.offset += self.save_every
        spotify_playlist_items = spotify.playlist_items(self.uri, limit=self.save_every, offset=self.offset) # gather the next set of tracks
        self.songs_to_uri = {entry["track"]["name"]:entry["track"]["uri"] for entry in spotify_playlist_items['items']}
                   