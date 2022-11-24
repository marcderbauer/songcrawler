from abc import ABC, abstractmethod
from music.setup import spotify, lyricsgenius, genius, song_regex, PARALLELIZE

from utils import get_int_input

class Music(ABC):

    @abstractmethod
    def from_spotify(uri):
        pass
    
    @classmethod
    def _pretty_print_search(cls, item_list, max_len=35):
        """
        Method to pretty print results from the search output
        """

        for l in item_list:
            l = [entry[:max_len] for entry in l]
    
        dashes = [f'{"-"*max_len}'] * len(item_list[0])
        item_list.insert(1, dashes)

        widths = [max(map(len, col)) for col in zip(*item_list)]
        for i, row in enumerate(item_list):
            print(f"[{i-2}]" if i >=2 else "   ", end= "    ")
            print("  ".join((val.ljust(width)[:max_len] for val, width in zip(row, widths))))

        print("\n") 
    
    @classmethod
    def _user_select_spotify(cls, item_list, max_len):
        """
        Prints the first 10 search results. The user can select one of the items or type get the next batch.
        ">/n/next" for next, "</p/previous" for previous
        0-9 for selection
        """
        pass
            
    @classmethod
    def search(cls, query, region="US"):
        """
        Searches spotify 
        """
        query_dict = Music.split_search(query)

        if "search" in query_dict or "track" in query_dict:
            if "search" in query_dict:
                print(f"No query parameters passed. Searching for track \"{query_dict['query']} ...\"\n")

            songs = spotify.search(q=query_dict["query"], market=region)
            search_result = [["Name", "Album", "Artist"]]
            for song in songs['tracks']['items']:
                search_result.append(
                    [
                        song['name'],
                        song['album']['name'],
                        song['artists'][0]['name']
                    ]
                )
            Music._pretty_print_search(search_result)

            index = get_int_input(num_results=len(search_result))
            uri = songs['tracks']['items'][index]['uri']

            return uri
            
        elif "album" in query_dict:
            albums = spotify.search(q=query_dict["query"], type="album", market=region)
            search_result = [["Name", "Artist"]]
            for album in albums['albums']['items']:
                search_result.append(
                    [
                        album['name'],
                        album['artists'][0]['name']
                    ]
                )
            Music._pretty_print_search(search_result)

            index = get_int_input(num_results=len(search_result))
            uri = albums['albums']['items'][index]['uri']

            return uri

        elif "playlist" in query_dict:
            playlists = spotify.search(q=query_dict["query"], type="playlist", market=region)
            search_result = [["Name", "User"]]
            for playlist in playlists['playlists']['items']:
                search_result.append(
                    [
                        playlist['name'],
                        playlist['owner']['display_name']
                    ]
                )
            Music._pretty_print_search(search_result)

            index = get_int_input(num_results=len(search_result))
            uri = playlists['playlists']['items'][index]['uri']

            return uri

        elif "artist" in query_dict:
            artists = spotify.search(q=query_dict["query"], type="artist", market=region)
            search_result = [["Artist", "Popularity"]]
            for artist in artists['artists']['items']:
                search_result.append(
                    [
                        artist['name'],
                        str(artist['popularity'])
                    ]
                )
            Music._pretty_print_search(search_result)

            index = get_int_input(num_results=len(search_result))
            uri = artists['artists']['items'][index]['uri']

            return uri

        else:
            raise Exception(f"Invalid query dict passed to Music.search():\n{query_dict}")
