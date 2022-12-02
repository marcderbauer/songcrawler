from music.music import Music
from music.setup import spotify, genius
import re


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

    def get_name(self):
        return self.song_name