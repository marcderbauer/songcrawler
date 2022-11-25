import os

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
        Path needs to be formatted like this:
        base_folder/artist_name/album_name/...
        """
        splitpath = string.split("/")
        assert len(splitpath) >= 3 and not '' in splitpath, "Path not long enough. The expected format is base_folder/artist_name/album_name/..."
        
        base_folder = splitpath[0]
        artist_name = splitpath[1]
        album_name  = splitpath[2]

        path = Path(base_folder, artist_name, album_name)
        return path

if __name__ == "__main__":
    path = Path.from_string('data/The 1975/') #Throws error (as desired)
    print(path)