from music.music import Music
from music.song import Song
from itertools import repeat
from copy import deepcopy
from music.setup import PARALLELIZE

from multiprocessing import Pool
from abc import ABC, abstractmethod

import os
import json
import csv
from utils import Path, file_empty, overwrite_dir

class MusicCollection(Music):
    def __init__(self, songs_to_uri, songs, missing_lyrics, collection_name) -> None:
        # Not a very nice solution, but want to keep name as self.playlist_name and self.album name
        # TODO: currently have three attributes passed here which are unused. What to do?
        # TODO: can this be removed?
        if collection_name:
            self.collection_name = collection_name
        else:
            pass
            #self.collection_name = self.playlist_name if isinstance(self, Playlist) else self.album_name 
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

