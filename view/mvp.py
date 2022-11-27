from __future__ import annotations

import sys

import pytermgui as ptg
from table import Table

PALETTE_LIGHT = "#FCBA03"
PALETTE_MID = "#8C6701"
PALETTE_DARK = "#4D4940"
PALETTE_DARKER = "#242321"


test_list1 = ["Love Story","Cavalcovers","black midi"]
test_list2 = ["A Tooth for an Eye", "Shaking The Habitual", "The Knife"]
test_list3 = ["Wolf", "Cool It Down", "Yeah Yeah Yeahs"]
test_lists = [test_list1, test_list2, test_list3]
this_list = [['Bonus Track: This Never Happened Before (feat. Jeremy Jordan, Laura Osnes & Frank Wildhorn)', 'Bonnie & Clyde', 'Original Broadway Cast Recording'], ['Jenny from the Block (feat. Jadakiss & Styles P.) - Track Masters Remix', 'This Is Me...Then', 'Jennifer Lopez'], ['Thus', 'Thus', 'Emancipator'], ['Sleep - Bonus Track', 'Young Mountain (10th Anniversary Edition)', 'This Will Destroy You'], ['It Has To Be This Way - Platinum Mix', 'METAL GEAR RISING REVENGEANCE Vocal Tracks Selection', 'Jimmy Gnecco'], ['This Night', 'This Night', 'Giuseppe Califano'], ['They Move on Tracks of Never-Ending Light', 'S/T', 'This Will Destroy You'], ['I Luv This Shit - Remix (Bonus Track)', 'Testimony (Deluxe)', 'August Alsina'], ['This Year', 'This Year', 'Sire'], ['They Move on Tracks of Never - Ending Light', 'S / T (10th Anniversary Edition)', 'This Will Destroy You']]

long_list = [['TIMESINK', 'DROWN THE TRAITOR WITHIN', 'Lorn'], ['On My Mind', 'Night and Day', 'Everything But The Girl'], ['Universe', 'Anicca', 'Teebs'], ['Tell Me the Ghost', 'Tell Me the Ghost', 'Tom Gallo'], ['The Other Lover (Little Dragon & Moses Sumney)', 'The Other Lover (Little Dragon & Moses Sumney)', 'Little Dragon'], ['Summertime', 'Take Care of You / Summertime', 'Charlotte Day Wilson'], ['Whale', 'Sen Am', 'Duval Timothy'], ['太陽さん', 'マホロボシヤ', 'Ichiko Aoba'], ['Ball', 'Sen Am', 'Duval Timothy'], ['Her Revolution', 'Her Revolution / His Rope', 'Burial'], ['Lone Wolf and Cub', 'The Beyond / Where the Giants Roam', 'Thundercat'], ['West', 'Indigo', 'River Tiber'], ['cellophane', 'MAGDALENE', 'FKA twigs'], ['Flume', 'For Emma, Forever Ago', 'Bon Iver'], ['Caroline', 'Hyper Romance', 'Jadu Heart'], ['Retrograde', 'Overgrown', 'James Blake'], ['All I Need', 'Instrumentals', 'Clams Casino'], ['Pink Salt Lake', 'True Care', 'James Vincent McMorrow'], ['Agony', 'Stranger', 'Yung Lean'], ['Unmoved (A Black Woman Truth)', 'Unmoved (A Black Woman Truth)', 'Ayoni'], ['Flamenco Sketches (feat. John Coltrane, Cannonball Adderley & Bill Evans)', 'Kind Of Blue (Legacy Edition)', 'Miles Davis'], ['Keep On', 'Antiphon', 'Alfa Mist'], ['Goodbye Blue', 'Goodbye Blue', 'BADBADNOTGOOD'], ['Glide (Goodbye Blue Pt. 2)', 'Goodbye Blue', 'BADBADNOTGOOD'], ['Fall Again', 'Help', 'Duval Timothy'], ['SHINSEN', 'Sakura', 'Susumu Yokota'], ['Rare', 'Rare', 'Blake Skowron'], ['Wondering in the Woods', 'Theory of Everything', 'Isak Strand vs. TOE'], ['Please Be Naked', 'I like it when you sleep, for you are so beautiful yet so unaware of it', 'The 1975'], ['Blue Ocean Floor', 'The 20/20 Experience (Deluxe Version)', 'Justin Timberlake'], ['Make Out in My Car - Sufjan Stevens Version', 'Make Out in My Car: Chameleon Suite', 'Moses Sumney'], ['Polly', 'græ', 'Moses Sumney'], ['Death & Taxes', "Pilgrim's Paradise", 'Daniel Caesar'], ['How Was Your Day?', 'Fake It Flowers', 'beabadoobee'], ['Movement 5', 'Promises', 'Floating Points'], ["Derrick's Beard", 'DEACON', 'serpentwithfeet'], ['Alone in Kyoto', 'Talkie Walkie', 'Air'], ['Back To Mars', 'Fake It Flowers', 'beabadoobee'], ['Mashita', 'Shiroi', 'Mansur Brown'], ['I Love Sloane', "Hangin' At The Beach", 'Delroy Edwards'], ['Rain Smell', 'Cerulean', 'Baths'], ['Hall', 'Cerulean', 'Baths'], ['billboard uwu', 'DPR ARCHIVES', 'DPR CREAM'], ['Merry Christmas Mr. Lawrence', 'Merry Christmas, Mr. Lawrence', 'Ryuichi Sakamoto'], ['Dawn Chorus', 'ANIMA', 'Thom Yorke'], ['Everything In Its Right Place', 'Kid A', 'Radiohead'], ['Jesus Christ 2005 God Bless America', 'Notes On a Conditional Form', 'The 1975'], ['Avril 14th', 'Drukqs', 'Aphex Twin'], ['A Sad Song About a Girl I No Longer Know', 'Bedside Kites', 'Bedside Kites'], ['Parallel 6', 'Parallel', 'Four Tet']]

def _create_aliases() -> None:
    """Creates all the TIM aliases used by the application.

    Aliases should generally follow the following format:

        namespace.item

    For example, the title color of an app named "myapp" could be something like:

        myapp.title
    """
    ptg.tim.alias("app.text", "#cfc7b0")

    ptg.tim.alias("app.header", f"bold @{PALETTE_MID} #d9d2bd")
    ptg.tim.alias("app.header.fill", f"@{PALETTE_LIGHT}")

    ptg.tim.alias("app.title", f"bold {PALETTE_LIGHT}")
    ptg.tim.alias("app.button.label", f"bold @{PALETTE_DARK} app.text")
    ptg.tim.alias("app.button.highlight", "inverse app.button.label")

    ptg.tim.alias("app.footer", f"@{PALETTE_DARKER}")


def _configure_widgets() -> None:
    """Defines all the global widget configurations.

    Some example lines you could use here:

        ptg.boxes.DOUBLE.set_chars_of(ptg.Window)
        ptg.Splitter.set_char("separator", " ")
        ptg.Button.styles.label = "myapp.button.label"
        ptg.Container.styles.border__corner = "myapp.border"
    """

    ptg.boxes.DOUBLE.set_chars_of(ptg.Window)
    # ptg.boxes.ROUNDED.set_chars_of(ptg.Container)
    ptg.Splitter.set_char("separator", " ")

def _define_layout() -> ptg.Layout:
    """Defines the application layout.

    Layouts work based on "slots" within them. Each slot can be given dimensions for
    both width and height. Integer values are interpreted to mean a static width, float
    values will be used to "scale" the relevant terminal dimension, and giving nothing
    will allow PTG to calculate the corrent dimension.
    """

    layout = ptg.Layout()

    # A header slot with a height of 1
    layout.add_slot("Header", height=1)
    layout.add_break()

    # A body slot that will fill the entire width, and the height is remaining
    layout.add_slot("Body") # width=0.9?

    layout.add_break()

    # A footer with a static height of 1
    layout.add_slot("Footer", height=1)

    return layout


def get_music_container(music_dict: dict) -> ptg.Container:
    labels = []
    for k, v in music_dict.items():
        label = ptg.Label(f"{k}:   {v}",parent_align=0)
        labels.append(label)
    c = ptg.Container(*labels, relative_width=0.7)
    return c


def main() -> None:
    """Runs the application."""

    _create_aliases()
    _configure_widgets()
    table = Table()
    table.set_header(["Song", "Album", "Artist"])
    table.append_rows(long_list)
    # table.append_rows(test_lists)#, box="EMPTY_VERTICAL")
    # table.append_rows(this_list)#, box="EMPTY_VERTICAL")

    with ptg.WindowManager() as manager:

        # containers = [get_music_container(d) for d in test_dicts]
        manager.layout = _define_layout()

        header = ptg.Window(
            "[app.header] SongCrawler",
            box="EMPTY",
            is_persistant=True
        )
        
        header.styles.fill = "app.header.fill"

        # Since header is the first defined slot, this will assign to the correct place
        manager.add(header)

        footer = ptg.Window(
            ptg.Button("Quit", lambda *_: manager.stop()), 
            box="EMPTY"
            )
        footer.styles.fill = "app.footer"

        # Since the second slot, body was not assigned to, we need to manually assign
        # to "footer"
        manager.add(footer, assign="footer")

        manager.add(
            ptg.Window(
                table.header,
                *table.rows,
                overflow=ptg.Overflow.SCROLL
                ),
            assign="body",
            )

    ptg.tim.print("\n[!gradient(210)]Goodbye!")


if __name__ == "__main__":
    main()