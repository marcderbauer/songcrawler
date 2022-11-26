from pytermgui import Container, Splitter, Label, StyleManager, real_length, tim

# TODO:
# this class should inherit from class Container, but import rows and operate on the basis of them


class Table(Container):
    
    def __init__(self, header: Container = None, rows: list[Container]=None, **attrs) -> None:
        self.header = None
        self.rows = []
        self.index = 0
        super().__init__(**attrs)
    
    @staticmethod
    def list_to_row(l: list, box="EMPTY_VERTICAL"):
        containers = []
        for item in l:
            c = Container(
                    Label(str(item)),
                    box=box
                )
            containers.append(c)
        splitter = Splitter(*containers)
        return splitter
    
    def add_index(self, l:list):
        l.insert(0, str(self.index))
        self.index += 1
        return l
    
    def set_header(self, header: Container):
        self.header = header
    
    def append_row(self, row:Container):
        self.rows.append(row)

# TODO: Try if this works. SHould work for header and rows, variable length!
# Might have to adjust width and height
# Also missing index -> Maybe add that to list outside of function