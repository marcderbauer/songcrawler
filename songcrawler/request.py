from songcrawler.songcrawler import Songcrawler
from music.music import Music
class Request(Songcrawler):
    def __init__(self, query: str, parent:Songcrawler) -> None:
        if parent:
            for key, val in vars(parent).items():
                setattr(self, key, val)
        else:
            super().__init__()

        # TODO: add param for: genius_id
        self.type = self.get_request_type(query)

        if self.type == "search":
            query = Music.search(query)
            self.type = self.get_request_type(query)

        self.query = query

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



    ########################################################################################
    ########################################################################################
    ###################### TODO MERGE REQUEST CLASS WITH SONGCRAWLER CLASS!!!    ###########
    ########################################################################################
    ########################################################################################