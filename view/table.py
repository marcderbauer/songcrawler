from pytermgui import Container, Splitter, Label
# TODO:
# this class should inherit from class Container, but import rows and operate on the basis of them


class Table(Container):
    
    def __init__(self, header: Container = None, rows: list[Container]=None, use_index=True, **attrs) -> None:
        self.header = None
        self.rows = []
        self.use_index = use_index
        self.index = 0
        self.index_width = 0.1
        super().__init__(**attrs)
    
    @staticmethod
    def list_to_row(l: list, box="EMPTY", use_index=False, index_width=None):
        # TODO: if use_index: create seperate container index with width index_width, then combine by using splitter
        # seems like relative_width is not taken into account when putting the container in a splitter...
        # Maybe workaround by creating another window just for the indices?

        # TODO: Add text_align option

        
        containers = []
        for item in l:
            c = Container(
                    Label(str(item)),
                    box=box,
                    relative_width=0.1
                )
            containers.append(c)
        splitter = Splitter(*containers)
        return splitter
    
    def get_index(self) -> int:
        index = self.index
        self.index += 1
        return index

    def add_index(self, l:list):
        l.insert(0, str(self.get_index()))
        return l
    
    def set_header(self, header: Container|list, box="EMPTY_VERTICAL"):
        if isinstance(header, list):
            if self.use_index:
                header.insert(0,"Index")
            header = self.list_to_row(header, box=box)
        elif not isinstance(header, Container):
            raise TypeError("Header should be eiter of type list or Container")
        self.header = header
    
    def append_row(self, row:Container|list, box="EMPTY"):
        if isinstance(row, list):
            if self.use_index:
                row.insert(0,self.get_index())
            row = self.list_to_row(row, box=box)
        elif not isinstance(row, Container):
            raise TypeError("Header should be eiter of type list or Container")
        self.rows.append(row)
    
    def append_rows(self, rows:list[Container]|list[list], box="EMPTY"):
        assert len(set(map(len,rows))) == 1 # checks if all items in list are of the same length
        for row in rows:
            self.append_row(row=row, box=box)

# TODO: Try if this works. SHould work for header and rows, variable length!
# Might have to adjust width and height
# Also missing index -> Maybe add that to list outside of function