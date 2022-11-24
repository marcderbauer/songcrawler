from music.music_collection import MusicCollection
from music.song import Song
from music.setup import spotify
from utils import delete_dir

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