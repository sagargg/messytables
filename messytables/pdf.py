from messytables.core import RowSet, TableSet, Cell

from messytables.types import StringType

try:
    from pdftables import get_tables
except ImportError as exc:
    if "No module named" not in exc.args[0]:
        raise
    get_tables = None


class PDFCell(Cell):

    def __init__(self, pdftables_cell):

        self._cell = pdftables_cell

        if pdftables_cell.topleft:
            w, h = pdftables_cell.size
            self._properties = dict(
                colspan=w,
                rowspan=h,
            )
            self.value = pdftables_cell.content

        else:
            self._properties = {}
            self.value = ""

        self.column = None
        self.column_autogenerated = False
        self.type = StringType()

    @property
    def topleft(self):
        return self._cell.topleft

    @property
    def properties(self):
        return self._properties


class PDFTableSet(TableSet):
    """
    A TableSet from a PDF document.
    """
    def __init__(self, fileobj=None, filename=None, **kw):
        if get_tables is None:
            raise ImportError("pdftables is not installed")
        if filename is not None:
            self.fh = open(filename, 'r')
        elif fileobj is not None:
            self.fh = fileobj
        else:
            raise TypeError('You must provide one of filename or fileobj')
        self.raw_tables = get_tables(self.fh)

    def make_tables(self):
        """
        Return a listing of tables (as PDFRowSets) in the table set.
        """
        def table_name(table):
            return "Table {0} of {1} on page {2} of {3}".format(
                table.table_number_on_page,
                table.total_tables_on_page,
                table.page_number,
                table.total_pages)
        return [PDFRowSet(table_name(table), table)
                for table in self.raw_tables]


class PDFRowSet(RowSet):
    """
    A RowSet representing a PDF table.
    """
    def __init__(self, name, table):
        if get_tables is None:
            raise ImportError("pdftables is not installed")
        super(PDFRowSet, self).__init__()
        self.name = name
        self.table = table
        self.meta = dict(
            page_number=table.page_number + 1,
        )

    def raw(self, sample=False):
        """
        Yield one row of cells at a time
        """
        if hasattr(self.table, "cell_data"):
            # New style of cell data.
            for row in self.table.cell_data:
                yield [PDFCell(pdf_cell) for pdf_cell in row]
        else:
            for row in self.table:
                yield [Cell(pdf_cell) for pdf_cell in row]
