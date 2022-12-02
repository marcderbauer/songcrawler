from music.music_collection import MusicCollection
from music.setup import spotify
from music.song import Song
from songcrawler.utils import delete_dir
from songcrawler.path import Path

import glob
import os
import re

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
        self.collection_name = playlist_name
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

    @classmethod
    def save_song(cls, song: Song, playlist_name: str, filetype: str, overwrite: bool, base_folder="data"):
        path = Path(folder=base_folder, artist="_Playlist", album=playlist_name)
        return super().save_song(song, path, filetype, overwrite)
    
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
            playlist = Playlist.from_file(file)
            songs.update(playlist.songs)
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
                   
    def get_name(self):
        return self.playlist_name