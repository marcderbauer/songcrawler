from music import Music, Artist, Playlist
import re

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
        result = Music.request(r)

        if isinstance(result, Artist):
            result.get_albums(folder=self.folder, filetype=self.filetype, lyrics_requested=lyrics_requested,
                         features_wanted=self.features_wanted, overwrite=self.overwrite, limit=self.limit)

        elif isinstance(result, Playlist):
            result.save(folder=self.folder, filetype=self.filetype, overwrite=self.overwrite, lyrics_requested=lyrics_requested, 
                        features_wanted=self.features_wanted)

        else:
            result.save(folder=self.folder, filetype=self.filetype, overwrite=self.overwrite)
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
    def __init__(self, query: str, parent:Songcrawler) -> None:
        if parent:
            for key, val in vars(parent).items():
                setattr(self, key, val)
        else:
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
            return("search")

    def get_spotify_type(self):
        """
        Returns the type of resource the self.query requests i.e. song, album, artist, playlist
        """
        uri = self.query.split(":")[1]    
        return uri

    def split_search(self,s):
        """
        Takes a search string and splits it by keywords
        Returns a dictionary {keyword: value}
        If no keywords are found it returns a dictionary with a single element "search" and the query as value.
        Loosely based on this:
        https://stackoverflow.com/questions/61056453/split-string-based-on-given-words-from-list
        """
        l = ["artist", "track", "album", "playlist"]
        s = re.sub(":", "", s)
        m = re.split(rf"({'|'.join(l)})", s, re.I)
        m = [i.strip() for i in m if i] # removes empty strings and whitespaces
        keyword = m[::2]
        value = m[1::2]
        if value:
            d = dict(zip(keyword, value))
        else:
            d = {"search":keyword[0]}
        return d