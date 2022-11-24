from music.music import Music
from music.setup import spotify
from music.album import Album

import re

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
   
