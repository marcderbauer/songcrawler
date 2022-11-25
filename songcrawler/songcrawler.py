from music import Song, Album, Playlist, Artist, Music


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

        # Handle request
        if not lyrics_requested:
            lyrics_requested = self.lyrics_requested # global override in case not specified

        request_type = self.get_request_type(query)

        if request_type == "search":
            query = Music.search(query)
            request_type = self.get_request_type(query)

        if request_type == "spotify":
            self.spotify_type = self.get_spotify_type()
        else:
            self.spotify_type = None
        
        # Query request from spotify
        result = self.query_spotify()

        # Save request
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
            raise Exception(f"Result is not of a known instance. Result type: {request_type(result)}")

        return result

    @classmethod
    def query_spotify(cls, request):
        if request.type == "spotify":
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

    
    def get_request_type(self, query):
        """
        Differentiates whether the query is a genius_id, spotify_uri, or songname
        """
        if query.isdigit():
            return("genius")
        elif query.startswith("spotify:"):
            return("spotify")
        else:
            return("search")

    def get_spotify_type(self):
        """
        Returns the type of resource the self.query requests i.e. song, album, artist, playlist
        """
        uri = self.query.split(":")[1]    
        return uri
