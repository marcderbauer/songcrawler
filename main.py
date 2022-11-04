import argparse
from music import Music, Artist


# ASCII Art: https://patorjk.com/software/taag/#p=display&v=0&f=Standard
##########################################################################################
#                            _                                        
#                           / \   _ __ __ _ _ __   __ _ _ __ ___  ___ 
#                          / _ \ | '__/ _` | '_ \ / _` | '__/ __|/ _ \
#                         / ___ \| | | (_| | |_) | (_| | |  \__ \  __/
#                        /_/   \_\_|  \__, | .__/ \__,_|_|  |___/\___|
#                                     |___/|_|                                          
# ########################################################################################    

# TODO: check best practices regarding spaces / underscores
parser = argparse.ArgumentParser(description='Gather Spotify statistics and Genius lyrics.')
parser.add_argument("query", metavar="Spotify URI, Genius ID or Songname", type=str, help="Either a Spotify uri, a songname or a genius id")
parser.add_argument("--filetype", type=str, default=".json", help="Filetype to save output as. Possible options: .json, .csv")
parser.add_argument("--genius", default=False, action='store_true', help="Lists alternative Genius ids when main argument is a songname")
parser.add_argument("--no_lyrics", default=False, action='store_true', help="Skips gathering lyrics and only queries spotify statistics.")
parser.add_argument("--region", type=str, default="US", help="Region to query songs for Spotify API. Helps prevent duplicate album entries.")
parser.add_argument("--folder", type=str, default="data", help="Output folder")
parser.add_argument("--overwrite", default=False, action='store_true', help="Overwrites existing songs/albums/artists/playlists")
parser.add_argument("--album_type",type=str, default="album", help="Type albums to retrieve when querying an album. Possible Values: album, ep")
args = parser.parse_args()

#TODO: add all possible album types to --album_type help
#print(args.filename)




##########################################################################################
#                                 __  __       _       
#                                |  \/  | __ _(_)_ __  
#                                | |\/| |/ _` | | '_ \ 
#                                | |  | | (_| | | | | |
#                                |_|  |_|\__,_|_|_| |_|
#                                                                                           
# ########################################################################################   

def main():
    # This is used only when accessing the program through the CLI
    # Keep in mind that the songcrawler class should also work independently as a python module
    sc = Songcrawler(lyrics_requested=not args.no_lyrics,
                    filetype=args.filetype, 
                    region=args.region,
                    folder=args.folder,
                    overwrite=args.overwrite,
                    album_type=args.album_type)
    sc.request(args.query)



##########################################################################################
#                 ____                                            _           
#                / ___|  ___  _ __   __ _  ___ _ __ __ ___      _| | ___ _ __ 
#                \___ \ / _ \| '_ \ / _` |/ __| '__/ _` \ \ /\ / / |/ _ \ '__|
#                 ___) | (_) | | | | (_| | (__| | | (_| |\ V  V /| |  __/ |   
#                |____/ \___/|_| |_|\__, |\___|_|  \__,_| \_/\_/ |_|\___|_|   
#                                  |___/                                                                              
# ########################################################################################  

class Songcrawler():
    def __init__(self, lyrics_requested=True, filetype="json", region="US", folder="data", overwrite=False, limit=50, album_type="album") -> None:
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
            result.save(self.folder, self.filetype, overwrite=self.overwrite)
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


if __name__=="__main__":
    main()
    # sc = Songcrawler()
    # artist = sc.request("spotify:artist:0fA0VVWsXO9YnASrzqfmYu")
    # album = sc.request("spotify:album:6dVCpQ7oGJD1oYs2fv1t5M")#, lyrics_requested=False)
    # song = sc.request("spotify:track:5CBEzaNEuv3OO32kZoXgOX")
    # sc.request("8150537")
    # sc.request("spotify:album:6dVCpQ7oGJD1oYs2fv1t5M")
    #print(artist)
    # BFIAFL genius_ids:
    # [8150565, 8150537, 8150538, 8099567, 8150539, 8150540, 8150541, 8150542, 8150543, 8150544, 8150545]

# If it doesn't find anything then the lyrics are just empty e.g. New York City Rage Fest on Indicud
# Would be cool if it included the song / album uri for debugging
