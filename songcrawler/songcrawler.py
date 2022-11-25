from music import Song, Album, Playlist, Artist
from songcrawler.request import Request


class Songcrawler():
    def __init__(self, lyrics_requested=True, filetype="json", region="US", folder="data", overwrite=False, limit=50, album_type="album", save_every=50, get_ids=False) -> None:
        self.lyrics_requested = lyrics_requested
        self.filetype = filetype
        self.features_wanted = ['danceability', 'energy', 'key', 'loudness',
                                'mode', 'speechiness', 'acousticness', 'instrumentalness',
                                'liveness', 'valence', 'tempo', 'time_signature', 'duration_ms']
        self.no_lyrics = {} # trackname: spotify_uri for songs without lyrics # TODO: remember to reset after each request
        self.region = region #setting country to US arbitrarily to avoid duplicates across regions
        self.album_regex = "Deluxe|Edition"
        self.folder = folder
        self.overwrite = overwrite
        self.limit = limit
        self.album_type = album_type
        self.save_every = 50
        self.get_ids = get_ids

    def request(self, query, lyrics_requested=None):
        """
        Make a request for a song, album, artist or playlist.
        Returns the spotify statistics and by default also the lyrics
        """
        if not lyrics_requested:
            lyrics_requested = self.lyrics_requested

        r = Request(query, self)
        result = Request.query_result(r)

        if isinstance(result, Song):
            Album.save_song(result, base_folder= self.folder, filetype=self.filetype, overwrite=self.overwrite)

        elif isinstance(result, Album):
            result.save(folder=self.folder, filetype=self.filetype, overwrite=self.overwrite)

        elif isinstance(result, Artist):
            result.get_albums(folder=self.folder, filetype=self.filetype, lyrics_requested=lyrics_requested,
                         features_wanted=self.features_wanted, overwrite=self.overwrite, limit=self.limit)

        elif isinstance(result, Playlist):
            result.save(folder=self.folder, filetype=self.filetype, overwrite=self.overwrite, lyrics_requested=lyrics_requested, 
                        features_wanted=self.features_wanted)
        else:
            raise Exception(f"Result is not of a known instance. Result type: {type(result)}")

        return result


    ########################################################################################
    ########################################################################################
    ###################### TODO ChANGE THIS METHODS NAME, MAYBE MERGE WITH ABOVE?###########
    ########################################################################################
    ########################################################################################

    @classmethod
    def query_result(cls, request):
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
            """
            api = lyricsgenius.API(os.environ["GENIUS_ACCESS_TOKEN"])
            search = api.search_songs(request.query)
            id_to_artist_song = {hit['result']['id']:(hit['result']['artist_names'], hit['result']['title']) for hit in search['hits']}
            print(json.dumps(id_to_artist_song, indent=4, ensure_ascii=False))
            quit()
            """

        else:
            result = Song.get_lyrics(request.query)
                # TODO: figure out how to save this

