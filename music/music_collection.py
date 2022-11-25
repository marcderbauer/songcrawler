from music.music import Music
from music.song import Song
from itertools import repeat
from music.setup import PARALLELIZE

from songcrawler.utils import file_empty, overwrite_dir
from songcrawler.path import Path

from copy import deepcopy
from multiprocessing import Pool
from abc import abstractmethod

import os
import json
import csv

class MusicCollection(Music):
    def __init__(self, songs_to_uri, songs, missing_lyrics, collection_name) -> None:
        self.songs_to_uri = songs_to_uri
        self.songs = songs
        self.missing_lyrics = missing_lyrics
        self.collection_name = collection_name
        super().__init__()
    
    @classmethod
    def from_file(cls, path):
        assert os.path.exists(path)
        filepath, filetype = os.path.splitext(path)
        
        if filetype == ".json":
            # Collection
            with open(path, "r") as f:
                collection_file = f.read()
                collection_json = json.loads(collection_file)
                songs = {name: Song(song["uri"], song["song_name"], song["album_name"], 
                        song["artist_name"], song["audio_features"]) for name,song in collection_json["songs"].items()}
                collection_json["songs"] = songs
                collection = cls(**collection_json)    
            
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
            collection = cls(uri=None, album_name=songdict["album_name"], artist_name=songdict["artist_name"])
            collection.songs = songs
            return collection
        
        else:
            raise Exception(f'Unknown file type: \"{filetype}\". Please select either \".json\" or \".csv\"')
    
    @classmethod
    def save_song(cls, song: Song, path:Path, filetype: str, overwrite: bool):# base_folder="data", filetype = ".json", overwrite=False, playlist_name = None): #TODO: maybe define base_folder in setup?
        """
        Saves a song to an album or playlist. If the album/playlist exists already it will look if the song exists and overwrite it in that case
        """
        if not os.path.isdir(path.album):
            os.makedirs(path.album)

        filepath = path.csv if filetype == ".csv" else path.json

        if os.path.exists(filepath):
            collection = cls.from_file(filepath)
            collection = collection[0] if isinstance(collection, tuple) else collection # collection turns into tuple after return?
            if song.song_name in collection.songs.keys() and not overwrite:
                print(f"\nSong \"{song.song_name}\" exists already.\nPlease use the --overwrite flag to save it.\n")
                quit()
            else:
                collection.songs[song.song_name] = song
        else:
            collection = cls(uri=None, album_name=song.album_name, artist_name=song.artist_name, songs={song.song_name:song})
        
        collection.save(folder=path.folder, filetype=filetype, overwrite=overwrite)
        


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

