# -*- encoding: utf-8 -*-
import os
import logging
from param import param
from pprint import pformat

from excel2data.param import param

logger = logging.getLogger(__name__)
HEADER = """
# -*- encoding: utf-8 -*-

"""

CONTAINER = {list, tuple}

INDENT = "\t"

class PyExporter(object):
    def __init__(self, module_name, table):
        self.module_name = module_name
        self.table = table
        self.parts = [HEADER]
        self.build_comments()

    def run(self):
        self.write_columns()
        self.write_index()
        self.write_matrix()
        self.write_file()

    def get_tmp_path(self, dst_module):
        module_path = dst_module.replace(".", "/") + ".py"
        pth = os.path.join(param.tmp_dir, module_path)
        return pth

    def build_comments(self):
        self.comment_level = 2
        self.comments = [0, 0]
        kidx = self.table.key_column
        self.comments[0] = [str(r[kidx]) if type(r[kidx]) is not unicode else r[kidx].encode("u8") for r in self.table.matrix]
        self.comments[1] = [c.program_name.encode("u8") for c in self.table.columns]

    def write_columns(self):
        column_object = {}
        for i, c in enumerate(self.table.columns):
            k = c.program_name.encode("u8")
            column_object[k] = i
        self.parts.append("columns = ")
        self.parts.append(pformat(column_object))
        self.parts.append("\n")

    def write_index(self):
        index_object = {}
        kidx = self.table.key_column
        for i, row in enumerate(self.table.matrix):
            k = row[kidx]
            if type(k) is unicode:
                k = k.encode("u8")
            duplicated = k in index_object
            if duplicated:
                logger.fatal("duplicated keys (%s)" % k)
                logger.fatal("current row:%s" % str(row))
                previous_idx = index_object[k]
                logger.fatal("previous row:%s" % str(self.table.matrix[previous_idx]))
                assert(not duplicated)
            index_object[k] = i
        self.parts.append("index = ")
        self.parts.append(pformat(index_object))
        self.parts.append("\n")


    def write_matrix(self):
        self.parts.append("table = ")
        self.dump_list(self.table.matrix, 0)

    def write_tuple_with_comment(self, t, level):
        indent = level * INDENT
        self.parts.append(indent)

    def dump_basic(self, b, level):
        self.parts.append(level * INDENT)
        self.parts.append(b.__repr__())

    def dump_unicode(self, u, level):
        self.parts.append(level * INDENT)
        self.parts.append("\"\"\"")
        ur = u.replace('"""', '\\"\\"\\"')
        self.parts.append(ur.encode("utf-8"))
        self.parts.append("\"\"\"")

    def dump_list(self, l, level):
        indent = level * INDENT
        clevel = level + 1
        self.parts.append(indent)
        self.parts.append("(\n")
        for i, e in enumerate(l):
            # comment first
            # dump element
            self.dump_element(e, clevel)
            self.parts.append(",")
            if level < self.comment_level:
                self.parts.append("#%s" % self.comments[level][i])
            self.parts.append("\n")
        self.parts.append(indent)
        self.parts.append(")")

    def dump_element(self, e, level):
        if type(e) in CONTAINER:
            self.dump_list(e, level)
        elif type(e) is unicode:
            self.dump_unicode(e, level)
        else:
            self.dump_basic(e, level)

    def write_file(self):
        body = "".join(self.parts)
        if self.module_name is None:
            print(body)
            return
        file_path = self.get_tmp_path(self.module_name)
        file_dir = os.path.dirname(file_path)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        with open(file_path, "w") as target:
            target.write(body)


if __name__ == "__main__":
    from excel2data.table import Table
    t = Table()
    t.build_from_sheet(u"../test_input/调试.xlsx", u"一些例子")
    t.key_column = 0
    exp = PyExporter(None, t)
    exp.run()