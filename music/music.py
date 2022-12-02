from music.setup import spotify
from music.search_result import SearchResult
from abc import ABC, abstractmethod
import re

class Music(ABC):

    @abstractmethod
    def from_spotify(uri):
        pass

    @abstractmethod
    def get_name(self):
        pass
            
    @classmethod
    def search(cls, query, region="US", limit=15, offset=0):
        """
        Searches spotify 
        """
        query_dict = Music.split_search(query)
        rows = []
        uris = []

        if "search" in query_dict or "track" in query_dict:
            if "search" in query_dict:
                print(f"No query parameters passed. Searching for track \"{query_dict['query']} ...\"\n")

            songs = spotify.search(q=query_dict["query"], market=region, limit=limit, offset=offset)
            header = ["Name", "Album", "Artist"]

            for song in songs['tracks']['items']:
                rows.append(
                    [
                        song['name'],
                        song['album']['name'],
                        song['artists'][0]['name']
                    ]
                )
                uris.append(song['uri'])
                     
        elif "album" in query_dict:
            albums = spotify.search(q=query_dict["query"], type="album", market=region, limit=limit, offset=offset)
            header = ["Name", "Artist"]
            for album in albums['albums']['items']:
                rows.append(
                    [
                        album['name'],
                        album['artists'][0]['name']
                    ]
                )
                uris.append(album['uri'])

        elif "playlist" in query_dict:
            playlists = spotify.search(q=query_dict["query"], type="playlist", market=region, limit=limit, offset=offset)
            header = ["Name", "User"]
            for playlist in playlists['playlists']['items']:
                rows.append(
                    [
                        playlist['name'],
                        playlist['owner']['display_name']
                    ]
                )
                uris.append(playlist['uri'])

        elif "artist" in query_dict:
            artists = spotify.search(q=query_dict["query"], type="artist", market=region, limit=limit, offset=offset)
            header = ["Artist", "Popularity"]
            for artist in artists['artists']['items']:
                rows.append(
                    [
                        artist['name'],
                        str(artist['popularity'])
                    ]
                )
                uris.append(artist['uri'])
            # Sort by popularity
            #uri_to_rows = {uri:rows for uri, rows in sorted((zip(uris, rows)), key=lambda x: int(x[1][1]), reverse=True)}

        else:
            raise Exception(f"Invalid query dict passed to Music.search():\n{query_dict}")
        
        search_result = SearchResult(header=header, rows=rows, uris=uris)
        return search_result


    @classmethod
    def split_search(cls, s):
        """
        Takes a search string and splits it by keywords
        Returns a dictionary {keyword: value}
        If no keywords are found it returns a dictionary with a single element "search" and the query as value.
        d["query"] is the original query s.
        Loosely based on this:
        https://stackoverflow.com/questions/61056453/split-string-based-on-given-words-from-list
        """
        l = ["artist", "track", "album", "playlist"]
        s = re.sub(":", " ", s)
        m = re.split(rf"({'|'.join(l)})", s, re.I)
        m = [i.strip() for i in m if i] # removes empty strings and whitespaces
        keyword = m[::2]
        value = m[1::2]
        if value:
            d = dict(zip(keyword, value))
        else:
            d = {"search":keyword[0]}
        d["query"] = s
        return d