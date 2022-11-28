from rich.console import Console
from rich.table import Table
import json
  
class View():

    def __init__(self, table=None, use_index = True, stylepath="view/styles.json") -> None:
        self.styles = self._load_styles(stylepath)
        self.table = table if table else Table(title="Songcrawler")
        self.console = Console()
        self.use_index = use_index
        if use_index:
            self.table.add_column("Index", **self.styles["Index"])
    
    def _load_styles(self, path):
        with open(path, "r") as f:
            return json.load(f)

    def set_table_columns(self, col_names:list[str]):
        for col_name in col_names:
            self.table.add_column(col_name, **self.styles[col_name])
    
    def add_rows(self, rows:list[list]):
        # TODO: assert if same length in list
        #       assert if same length as headers (maybe handeled within library?)
        for i, row in enumerate(rows):
            if self.use_index:
                row.insert(0, str(i))
            self.table.add_row(*row)
    
    def fill_table(self, headers:list[str], rows:list[list[str]]):
        """
        Populates a table with a given list of headers and a matrix of rows
        """
        self.set_table_columns(col_names=headers)
        self.add_rows(rows=rows)

    def run(self):
        self.console.print(self.table)
        while(True):
            try:
                index = self.console.input("Use '>'/'<' or '+'/'-' to scroll and '(q)uit' to exit.\nPlease select an item index:  ")
                if index in ["q", "quit", "exit"]:
                    quit()
                elif index in ["h", "help", "p", "prev", "prev.", "previous", "<", "-", "n","next", ">", "+"]:
                    return index
                elif index.isdigit():
                    index = int(index)
                    if index in range(self.table.row_count-1):
                        return index
                    else:
                        print(f"Index needs to be in range [0-{self.table.row_count-1}]\n")
                else:
                    print(f"Index needs to be a valid Integer in range [0-{self.table.row_count-1}]\n")
            except KeyboardInterrupt:
                quit()
    
    def reset(self):
        """
        Purges content from rows/columns. Used when after scrolling through pages.
        # TODO: This seems like something that you shouldn't have to manually call every time you move onto the next table
        #       Redesign this. Maybe make scrolling a feature of view?
        """
        self.table = Table(title="Songcrawler")

if __name__ == "__main__":
    long_list = [['TIMESINK', 'DROWN THE TRAITOR WITHIN', 'Lorn'], ['On My Mind', 'Night and Day', 'Everything But The Girl'], ['Universe', 'Anicca', 'Teebs'], ['Tell Me the Ghost', 'Tell Me the Ghost', 'Tom Gallo'], ['The Other Lover (Little Dragon & Moses Sumney)', 'The Other Lover (Little Dragon & Moses Sumney)', 'Little Dragon'], ['Summertime', 'Take Care of You / Summertime', 'Charlotte Day Wilson'], ['Whale', 'Sen Am', 'Duval Timothy'], ['太陽さん', 'マホロボシヤ', 'Ichiko Aoba'], ['Ball', 'Sen Am', 'Duval Timothy'], ['Her Revolution', 'Her Revolution / His Rope', 'Burial'], ['Lone Wolf and Cub', 'The Beyond / Where the Giants Roam', 'Thundercat'], ['West', 'Indigo', 'River Tiber'], ['cellophane', 'MAGDALENE', 'FKA twigs'], ['Flume', 'For Emma, Forever Ago', 'Bon Iver'], ['Caroline', 'Hyper Romance', 'Jadu Heart'], ['Retrograde', 'Overgrown', 'James Blake'], ['All I Need', 'Instrumentals', 'Clams Casino'], ['Pink Salt Lake', 'True Care', 'James Vincent McMorrow'], ['Agony', 'Stranger', 'Yung Lean'], ['Unmoved (A Black Woman Truth)', 'Unmoved (A Black Woman Truth)', 'Ayoni'], ['Flamenco Sketches (feat. John Coltrane, Cannonball Adderley & Bill Evans)', 'Kind Of Blue (Legacy Edition)', 'Miles Davis'], ['Keep On', 'Antiphon', 'Alfa Mist'], ['Goodbye Blue', 'Goodbye Blue', 'BADBADNOTGOOD'], ['Glide (Goodbye Blue Pt. 2)', 'Goodbye Blue', 'BADBADNOTGOOD'], ['Fall Again', 'Help', 'Duval Timothy'], ['SHINSEN', 'Sakura', 'Susumu Yokota'], ['Rare', 'Rare', 'Blake Skowron'], ['Wondering in the Woods', 'Theory of Everything', 'Isak Strand vs. TOE'], ['Please Be Naked', 'I like it when you sleep, for you are so beautiful yet so unaware of it', 'The 1975'], ['Blue Ocean Floor', 'The 20/20 Experience (Deluxe Version)', 'Justin Timberlake'], ['Make Out in My Car - Sufjan Stevens Version', 'Make Out in My Car: Chameleon Suite', 'Moses Sumney'], ['Polly', 'græ', 'Moses Sumney'], ['Death & Taxes', "Pilgrim's Paradise", 'Daniel Caesar'], ['How Was Your Day?', 'Fake It Flowers', 'beabadoobee'], ['Movement 5', 'Promises', 'Floating Points'], ["Derrick's Beard", 'DEACON', 'serpentwithfeet'], ['Alone in Kyoto', 'Talkie Walkie', 'Air'], ['Back To Mars', 'Fake It Flowers', 'beabadoobee'], ['Mashita', 'Shiroi', 'Mansur Brown'], ['I Love Sloane', "Hangin' At The Beach", 'Delroy Edwards'], ['Rain Smell', 'Cerulean', 'Baths'], ['Hall', 'Cerulean', 'Baths'], ['billboard uwu', 'DPR ARCHIVES', 'DPR CREAM'], ['Merry Christmas Mr. Lawrence', 'Merry Christmas, Mr. Lawrence', 'Ryuichi Sakamoto'], ['Dawn Chorus', 'ANIMA', 'Thom Yorke'], ['Everything In Its Right Place', 'Kid A', 'Radiohead'], ['Jesus Christ 2005 God Bless America', 'Notes On a Conditional Form', 'The 1975'], ['Avril 14th', 'Drukqs', 'Aphex Twin'], ['A Sad Song About a Girl I No Longer Know', 'Bedside Kites', 'Bedside Kites'], ['Parallel 6', 'Parallel', 'Four Tet']]
    v = View()
    v.fill_table(["Song", "Album", "Artist"], long_list)
    v.run()