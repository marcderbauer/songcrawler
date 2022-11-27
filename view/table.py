from pytermgui import Container, Splitter, Label, Widget, Layout
# TODO:
# this class should inherit from class Container, but import rows and operate on the basis of them


class Table(Container):

    def __init__(self, header: Container = None, rows: list[Container]=None, use_index=True, **attrs) -> None:
        self.header = None
        self.rows = []
        self.use_index = use_index
        self.index = 0
        super().__init__(**attrs)

    @classmethod
    def from_lists(cls, header: list = None, rows: list[list]=None, use_index=True, **attrs):
        h = "x" # TODO: maybe change set_header to make_header (or just seperate method)
        # TODO: also, when is this method called? This is before creating a table, but doesn't the view instantiate a table already?
        # Maybe pass all the necessary lists to view, which in turn calls self.table = Table.from_lists(...)

    @staticmethod
    def list_to_row(l: list, box="EMPTY", index = None, is_header=False):
        """
        Takes a list and converts it into a row which can be added to the table.
        """
        assert isinstance(index, None|int), "Index needs to be a valid integer or None."

        align = 1 if is_header else 0
        containers = []

        for item in l:   
            c = Container(
                    Label(
                        str(item),
                        parent_align=align,
                        ),
                    box=box
                )
            containers.append(c)

        # Index Container
        if index or index == 0:
            i = Container(
                Label(
                    str(index),
                    parent_align=1
                ),
                box = box
            )
            containers.insert(0, i)

        splitter = Splitter(*containers)
        return splitter
    
    def get_index(self) -> int:
        """
        Gets current index and adds 1 to it.
        """
        index = self.index
        self.index += 1
        return index

    def set_header(self, header: Container|list, box="DOUBLE_BOTTOM"):
        """
        Sets the header of the current table given a container or list.
        If it is handed a list it will construct the Container and before setting it to self.header.
        """
        if isinstance(header, list):
            if self.use_index:
                header.insert(0,"Index")
            header = self.list_to_row(header, box=box, is_header=True)
        elif not isinstance(header, Container):
            raise TypeError("Header should be eiter of type list or Container")
        self.header = header
    
    def append_row(self, row:Container|list, box="EMPTY"):
        """
        Appends a row to the table. Either takes a Container or constructs one from a list
        """
        assert isinstance(row, Container|list), TypeError("Header should be eiter of type list or Container")
        if self.use_index:
            row = self.list_to_row(row, box=box, index=self.get_index())
        else:
            row = self.list_to_row(row, box=box)
        self.rows.append(row)
    
    def append_rows(self, rows:list[Container]|list[list], box="EMPTY"):
        """
        Constructs and appends multiple rows to the table.
        """
        assert len(set(map(len,rows))) == 1, "Rows are not of equal length" # checks if all items in list are of the same length
        for row in rows:
            self.append_row(row=row, box=box)