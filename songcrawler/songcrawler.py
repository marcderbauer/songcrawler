from music import Song, Album, Playlist, Artist, Music, SearchResult
from view import View

class Songcrawler():
    def __init__(self, lyrics_requested=True, filetype="json", region="US", folder="data", overwrite=False, 
                    limit=50, album_type="album", save_every=50, get_ids=False, interactive=False, page_limit=15) -> None:
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
        self.page_limit = page_limit
        self.interactive = interactive
        if interactive:
            self.view = View()

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
            offset = 0
            while(True):
                search_result = Music.search(query=query, limit=self.page_limit, offset=offset)
                if self.interactive:
                    # prevent scrolling past end of spotify results
                    if len(search_result) == 0:
                        offset -= self.page_limit
                        continue
                    self.view.fill_table(search_result.header, search_result.rows)
                    view_return = self.view.display_table()
                    # scrolling 
                    if view_return in ["n","next",">","+"]:
                        offset += self.page_limit
                        self.view.reset()
                    elif view_return in ["p","prev", "prev.", "previous", "<", "-"]:
                        offset = max(0, offset-self.page_limit)
                        self.view.reset()
                    elif view_return in ["h", "help"]:
                        print("Enter an index corresponding to one of the rows.\nScroll through pages with (p)revious/(n)ext, '>'/'<' or '+'/'-'")
                    else:
                        query = search_result.uris[view_return]
                        request_type = self.get_request_type(query)
                        break
                else:
                    return search_result

        # Query request from spotify
        result = self.query_spotify(request_type=request_type, query=query)

        # Save request
        self._save_result(result, lyrics_requested=lyrics_requested)
        
        return result

    def query_spotify(self, request_type, query):
        if request_type == "spotify":
            match self.get_spotify_type(query=query):
                case "track":
                    song = Song.from_spotify(query, lyrics_requested=self.lyrics_requested, 
                                features_wanted=self.features_wanted)#, genius_id=genius_id) TODO: figure out genius ID here
                    return song

                case "album":
                    album = Album.from_spotify(query, self.lyrics_requested, self.features_wanted)
                    return album

                case "artist":
                    artist = Artist.from_spotify(query, album_type=self.album_type, regex_filter=self.album_regex,
                                                region=self.region, limit=self.limit)
                    return artist

                case "playlist":
                    playlist = Playlist.from_spotify(uri=query, save_every=self.save_every)
                    return playlist

                case _:
                    raise Exception(f'Unknown request type: \"{request_type}\"')
                    
        elif request_type == "genius":
            result = Song.get_lyrics(genius_id=query)
            print(result)
            # TODO: Figure out how to save this

        elif self.get_ids:
            # Would make sense to move this to setup, but only really required in this specific case
            """
            api = lyricsgenius.API(os.environ["GENIUS_ACCESS_TOKEN"])
            search = api.search_songs(request.query)
            id_to_artist_song = {hit['result']['id']:(hit['result']['artist_names'], hit['result']['title']) for hit in search['hits']}
            print(json.dumps(id_to_artist_song, indent=4, ensure_ascii=False))
            quit()
            """

        else:
            result = Song.get_lyrics(query)
                # TODO: figure out how to save this

    def _save_result(self, result, lyrics_requested):
        """
        Calls each Music class' respecive save function
        """
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

    def get_spotify_type(self, query):
        """
        Returns the type of resource the query requests i.e. song, album, artist, playlist
        """
        uri = query.split(":")[1]    
        return uri
