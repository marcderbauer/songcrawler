from __future__ import annotations
import pytermgui as ptg
from table import Table

PALETTE_LIGHT = "#FCBA03"
PALETTE_MID = "#8C6701"
PALETTE_DARK = "#4D4940"
PALETTE_DARKER = "#242321"

class View():

    def __init__(self) -> None:
        self.table = Table()
    
    def _create_aliases(self) -> None:
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


    def _configure_widgets(self) -> None:
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

    def _define_layout(self) -> ptg.Layout:
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


    def get_music_container(self, music_dict: dict) -> ptg.Container:
        labels = []
        for k, v in music_dict.items():
            label = ptg.Label(f"{k}:   {v}",parent_align=0)
            labels.append(label)
        c = ptg.Container(*labels, relative_width=0.7)
        return c


    def start(self) -> None:
        """Runs the application."""

        self._create_aliases()
        self._configure_widgets()
        table = Table()
        table.set_header(["Song", "Album", "Artist"])
        table.append_rows(long_list)
        # table.append_rows(test_lists)#, box="EMPTY_VERTICAL")
        # table.append_rows(this_list)#, box="EMPTY_VERTICAL")

        with ptg.WindowManager() as manager:

            # containers = [get_music_container(d) for d in test_dicts]
            manager.layout = self._define_layout()

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
    v = View
    v.start()