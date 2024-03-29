import argparse
from songcrawler import Songcrawler


# TODO: check best practices regarding spaces / underscores
parser = argparse.ArgumentParser(description='Gather Spotify statistics and Genius lyrics.')
parser.add_argument("query", type=str, help="Either a Spotify uri, a songname or a genius id")
parser.add_argument("--filetype", type=str, default=".json", help="Filetype to save output as. Possible options: .json, .csv")
parser.add_argument("--genius", default=False, action='store_true', help="Lists alternative Genius ids when main argument is a songname")
parser.add_argument("--no_lyrics", default=False, action='store_true', help="Skips gathering lyrics and only queries spotify statistics.")
parser.add_argument("--region", type=str, default="US", help="Region to query songs for Spotify API. Helps prevent duplicate album entries.")
parser.add_argument("--folder", type=str, default="data", help="Output folder")
parser.add_argument("--overwrite", default=False, action='store_true', help="Overwrites existing songs/albums/artists/playlists")
parser.add_argument("--album_type",type=str, default="album", help="Type of albums to retrieve when querying an album. Possible Values: album, ep")
parser.add_argument("--save_every", type=int, default=50, help="Incremental saving when querying playlists.")
parser.add_argument("--get_ids", default=False, action='store_true', help="Gathers genius_ids for a given search term and prints them to the terminal.")
args = parser.parse_args()

#TODO: add all possible album types to --album_type help
#print(args.filename)

def main():
    # This is used only when accessing the program through the CLI
    # Keep in mind that the songcrawler class should also work independently as a python module
    sc = Songcrawler(lyrics_requested=not args.no_lyrics,
                    filetype=args.filetype, 
                    region=args.region,
                    folder=args.folder,
                    overwrite=args.overwrite,
                    album_type=args.album_type,
                    save_every=args.save_every,
                    get_ids = args.get_ids,
                    interactive=True)
    sc.request(args.query)

if __name__=="__main__":
    main()
