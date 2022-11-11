from music import Music, Artist

# ASCII Art: https://patorjk.com/software/taag/#p=display&v=0&f=Standard
##########################################################################################
#                 ____                                            _           
#                / ___|  ___  _ __   __ _  ___ _ __ __ ___      _| | ___ _ __ 
#                \___ \ / _ \| '_ \ / _` |/ __| '__/ _` \ \ /\ / / |/ _ \ '__|
#                 ___) | (_) | | | | (_| | (__| | | (_| |\ V  V /| |  __/ |   
#                |____/ \___/|_| |_|\__, |\___|_|  \__,_| \_/\_/ |_|\___|_|   
#                                  |___/                                                                              
# ########################################################################################  

class Songcrawler():
    def __init__(self, lyrics_requested=True, filetype="json", region="US", folder="data", overwrite=False, limit=50, album_type="album", save_every=50) -> None:
        self.lyrics_requested = lyrics_requested
        self.filetype = filetype
        self.features_wanted = ['danceability', 'energy', 'key', 'loudness',
                                'mode', 'speechiness', 'acousticness', 'instrumentalness',
                                'liveness', 'valence', 'tempo', 'time_signature', 'duration_ms']
        self.no_lyrics = {} # trackname: spotify_uri for songs without lyrics # Todo: remember to reset after each request
        self.region = region #setting country to US arbitrarily to avoid duplicates across regions
        self.album_regex = "Deluxe|Edition"
        self.folder = folder
        self.overwrite = overwrite
        self.limit = limit
        self.album_type = album_type
        self.save_every = 50

    def request(self, query, lyrics_requested=None):
        """
        Make a request for a song, album, artist or playlist.
        Returns the spotify statistics and by default also the lyrics
        """
        if not lyrics_requested:
            lyrics_requested = self.lyrics_requested
        r = Request(query)
        result = Music.request(r)
        # TODO: flesh logic out here
        if isinstance(result, Artist):
            result.get_albums(folder=self.folder, filetype=self.filetype, lyrics_requested=lyrics_requested,
                         features_wanted=self.features_wanted, overwrite=self.overwrite, limit=self.limit)
        else:
            result.save(folder=self.folder, filetype=self.filetype, overwrite=self.overwrite, lyrics_requested=lyrics_requested, 
                        features_wanted=self.features_wanted)
        return result



# ########################################################################################   
#                            ____                            _   
#                           |  _ \ ___  __ _ _   _  ___  ___| |_ 
#                           | |_) / _ \/ _` | | | |/ _ \/ __| __|
#                           |  _ <  __/ (_| | |_| |  __/\__ \ |_ 
#                           |_| \_\___|\__, |\__,_|\___||___/\__|
#                                         |_|                    
# ########################################################################################     

class Request(Songcrawler):
    def __init__(self, query: str) -> None:
        super().__init__()
        # TODO: add param for: genius_id
        self.query = query
        self.type = self.get_request_type(query)
        
        if self.type == "spotify":
            self.spotify_type = self.get_spotify_type()
        else:
            self.spotify_type = None
    
    def get_request_type(self, query):
        """
        Differentiates whether the query is a genius_id, spotify_uri, or songname
        """
        if query.isdigit():
            return("genius")
        elif query.startswith("spotify:"):
            return("spotify")
        else:
            return("song")

    def get_spotify_type(self):
        """
        Returns the type of resource the self.query requests i.e. song, album, artist, playlist
        """
        uri = self.query.split(":")[1]    
        return uri