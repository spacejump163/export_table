# -*- encoding: utf-8 -*-
import xlrd
import logging
import copy

from excel2data.types import get_type

HEADER_HINTS = {u"Id", u"ID", u"id", u"iD", u"名称", u"编号"}

logger = logging.getLogger(__name__)

class Table(object):
    def __init__(self):
        self.matrix = []
        self.columns = []
        self.key_column = 0

    def build_from_sheet(self, file_name, sheet_name):
        self.signature = file_name, sheet_name
        book = xlrd.open_workbook(file_name)
        sh = book.sheet_by_name(sheet_name)
        self.sh = sh
        self.cols = sh.ncols
        self.rows = sh.nrows
        self.start_row = self.find_start_row()
        self.build_columns()
        self.build_matrix()
        self.sh = None

    def find_start_row(self):
        for row in range(0, 100):
            value = self.sh.cell_value(row, 0)
            if self.is_valid_header(value):
                logger.info("found valid header at row %d" % row)
                return row
        raise KeyError("I have tried 100 row and still haven't found a header that seems to work")

    def is_valid_header(self, value):
        if type(value) is not unicode:
            return False
        for i in HEADER_HINTS:
            if i in value:
                return True

    def build_columns(self):
        self.columns = []
        program_names = set()
        for i in range(self.cols):
            logger.info(">start building column %d" % i)
            pn = self.sh.cell_value(self.start_row + 1, i)
            pn_duplicated = pn in program_names
            if pn_duplicated:
                logger.info("program name duplicated")
            assert(not pn_duplicated)
            program_names.add(pn)
            dn = self.sh.cell_value(self.start_row + 0, i)
            tn = self.sh.cell_value(self.start_row + 2, i)
            citem = ColumnItem(dn, pn, tn)
            if not citem.type_info.is_comment():
                citem.cidx = i
                self.columns.append(citem)
            logger.info("<finished building column %d" % i)

    def build_matrix(self):
        self.matrix = []
        for row in range(self.start_row + 3, self.rows):
            data_row = []
            for column_item in self.columns:
                col = column_item.cidx
                logger.info(">start processing cell %d:%d" % (row, col))
                v = self.get_cell_value(row, column_item)
                data_row.append(v)
                logger.info("<finished processing cell %d:%d" % (row, col))
            self.matrix.append(data_row)
        for i, c in enumerate(self.columns):
            c.cidx = i

    def get_cell_value(self, row, column_item):
        value = self.sh.cell_value(row, column_item.cidx)
        if value is u"":
            return None
        parse_value = column_item.parse(unicode(value))
        return parse_value

    @classmethod
    def merge(cls, tables):
        assert(len(tables) > 0)
        if len(tables) == 1:
            return tables[0]
        logger.info(">begin merging table")
        for i in tables:
            logger.info("merge %s" % (i.signature,))
        merged_columns = cls.merge_columns(tables)
        merged_table = Table()
        merged_table.columns = merged_columns
        for t in tables:
            merged_table.add_from_table(t)
        merged_table.signature = frozenset([t.signature for t in tables])
        logger.info("<end merging table")
        return merged_table

    @classmethod
    def merge_columns(cls, tables):
        merged_column_list = []
        merged_column_set = set()
        merged_column_program_names = {}
        for t in tables:
            columns = t.columns
            for c in columns:
                if c not in merged_column_set:
                    # column not seen, but make sure program name is not used
                    program_name_used = c.program_name in merged_column_program_names
                    if program_name_used:
                        logger.fatal("program name used by 2 different columns, they are:")
                        logger.fatal("%s" % c)
                        logger.fatal("and")
                        logger.fatal("%s" % merged_column_program_names[c.program_name])
                    assert(not program_name_used)
                    merged_column_program_names[c.program_name] = c
                    merged_column_set.add(c)
                    merged_column_list.append(c)
        for i, c in enumerate(merged_column_list):
            c.cidx = i
        return merged_column_list

    def column_to_index(self, column):
        try:
            return self.columns.index(column)
        except ValueError:
            return -1

    def add_from_table(self, to_be_added):
        for ridx, row in enumerate(to_be_added.matrix):
            new_row = []
            for column in self.columns:
                cidx = to_be_added.column_to_index(column)
                if cidx == -1:
                    new_row.append(None)
                else:
                    new_row.append(row[cidx])
            self.matrix.append(new_row)



class ColumnItem(object):
    def __init__(self, design_name, program_name, type_def):
        self.design_name = design_name
        self.program_name = program_name
        self.type_info = get_type(type_def)

    def parse(self, cell_value):
        return self.type_info.parse(cell_value)

    def __eq__(self, other):
        if other is self:
            return True
        dmatch = self.design_name == other.design_name
        pmatch = self.program_name == other.program_name
        tmatch = self.type_info == other.type_info
        if dmatch and pmatch and tmatch:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.design_name) ^ hash(self.program_name) ^ id(self.type_info)

    def __str__(self):
        return "(%s, %s, %s)" % (self.design_name, self.program_name, self.type_info.to_declaration())

    def __repr__(self):
        return str(self)

    def clone(self):
        return copy.copy(self)
