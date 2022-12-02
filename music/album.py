from music.music_collection import MusicCollection
from music.song import Song
from music.setup import spotify
from songcrawler.utils import delete_dir
from songcrawler.path import Path

class Album(MusicCollection):
    def __init__(self, uri, album_name, artist_name, songs_to_uri=None, songs={}, missing_lyrics={}, collection_name=None) -> None:
        self.uri = uri
        self.album_name = album_name
        self.artist_name = artist_name
        self.songs_to_uri = songs_to_uri
        self.songs = songs
        self.missing_lyrics = missing_lyrics # name:uri of missing songs
        self.collection_name = album_name
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

    @classmethod
    def save_song(cls, song:Song, filetype, overwrite=False, base_folder="data"):
        path = Path(folder=base_folder, artist=song.artist_name, album=song.album_name)
        super().save_song(song, path, filetype=filetype, overwrite=overwrite)

    def _write_csv(self, path):
        return super()._write_csv(path=path, mode="w")

    def save(self, folder, filetype, overwrite):
        """
        Tries to save the album. If files exist and overwriting is not allowed returns False.
        """
        path = self.get_path(folder)
        # TODO: Don't create files like that....
        write_allowed = self._init_files(path=path, filetype=filetype, overwrite=overwrite)
        if write_allowed:
            self._write(path=path, filetype=filetype)
        else:
            return False
        delete_dir(path.temp) # TODO shouldn't be generated for Albums, need to figure out how to avoid this
    
    def get_name(self):
        return self.album_name