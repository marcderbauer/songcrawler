import os
import pathlib
import shutil
def file_empty(path):
    return not (os.path.isfile(path) and os.path.getsize(path) > 0)

def delete_dir(path, verbose=False):
    path = pathlib.Path(path)
    if path.exists() and path.is_dir():
        shutil.rmtree(path)
    if verbose:
        print(f"Deleted dir {path}")

def overwrite_dir(path, verbose=False):
    """
    Overwrites a directory no matter the contents. Primarily used for temp directories
    """
    delete_dir(path)
    os.makedirs(path)
    if verbose:
        print(f"Force created directory {path}")

class Path():
    def __init__(self, folder, artist, album) -> None:
        self.folder = folder
        self.artist_name = artist
        self.album_name = album
        self.artist = os.path.join(folder, artist)
        self.album = os.path.join(self.artist, album)
        self.album_base = os.path.join(self.album, album) # folder/artist/album/album
        self.json = f"{self.album_base}.json"
        self.lyrics = f"{self.album_base}_lyrics.json"
        self.csv = f"{self.album_base}.csv"
        self.temp = os.path.join(self.album, ".tmp")
        self.temp_index = 0
    
    def get_temp_paths(self):
        file = os.path.join(self.temp, f"{self.album_name}{self.temp_index}.json")
        lyrics = os.path.join(self.temp, f"{self.album_name}{self.temp_index}_lyrics.json")
        self.temp_index += 1
        return file, lyrics
            
    @classmethod
    def from_string(cls, string):
        """
        Instanciates a path object from a string path
        TODO: is this necessary?
        """
        pass