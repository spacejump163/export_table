# -*- encoding: utf-8 -*-
import os
import imp
from collections import namedtuple
import argparse
import re

import logging

import xlrd

logger = logging.getLogger("export_table")
logger.addHandler(logging.StreamHandler())

ColumnItem = namedtuple("ColumnItem", ("program_name", "column_name", "type_name"))
ColumnName = namedtuple("ColumnName", ("program_name", "column_name"))

NodeList = namedtuple("NodeList", ("etype", "num"))
NodeTuple = namedtuple("NodeTuple", ("etypes"))

tint = type(1)
tfloat = type(1.0)
tbool = type(True)
tunicode = type(u"")
tstr = type("")

class App(object):
    def __init__(self, input_dir, output_dir, rule_dir, use_comment, verbose):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.rule_dir = rule_dir
        self.use_comment = use_comment
        self.debug_level = logging.INFO if verbose else logging.WARNING
        logger.setLevel(self.debug_level)
        self.converters = {}
        self.structs = {}
        self.coercing = {
            tfloat: {tfloat, tint},
            tint: {tint},
            tbool: {tbool},
            tunicode: {tstr, tunicode},
        }
        self.register_converters()

    def run(self):
        l = os.listdir(self.input_dir)
        for file_name in l:
            # check if this is a xls file
            n, e = os.path.splitext(file_name)
            if e not in {".xls", ".xlsx"} or not self.check_file_name(n):
                logger.warning("*WARNING*: skipped invalid file name:%s" % file_name)
                continue
            # get the corresponding rule file if any
            file_path = os.path.join(self.input_dir, file_name)
            rule_name = os.path.join(self.rule_dir, n) + ".py"
            rule_module = None
            logger.info(">>>start processing:%s" % file_path)
            if os.path.exists(rule_name):
                rule_module = imp.load_source("plugin", rule_name)
                logger.info("rule file found")
            else:
                logger.info("rule file not found")
            #print self.input_dir + file_name, plugin
            data, column_names = self.parse_table(file_path, rule_module)
            output_file_path = os.path.join(self.output_dir, n) + ".py"

            emitter = getattr(rule_module, "emitter", self.default_emitter)
            targets = emitter(output_file_path, data, column_names)
            for target_file, target_data, target_column_name in targets:
                exporter = PyExporter(target_file, target_data, target_column_name, self.use_comment)
                exporter.write()
                logger.info("<write to target:%s over" % target_file)
            logger.info("<<<finish processing:%s" % file_path)

    def parse_table(self, file_path, rule_module):
        """
        parse a xlsx/xls with the given file_path
        :param file_path: a str
        :return: (dict_containing_table_contents, column_names_tuple2)
        """
        row_mapper = getattr(rule_module, "row_mapper", None)
        col_mapper = getattr(rule_module, "column_mapper", None)

        book = xlrd.open_workbook(file_path)
        sh = book.sheet_by_index(0)
        column_desc = []
        for col in range(sh.ncols):
            cn = sh.cell_value(0, col)
            pn = sh.cell_value(1, col)
            tn = sh.cell_value(2, col)
            column_desc.append(ColumnItem(pn, cn, tn))

        if col_mapper:
            column_names = col_mapper()
        else:
            column_names = [ColumnName(i.program_name, i.column_name) for i in column_desc]

        table = {}

        if row_mapper is None:
            row_mapper = lambda row: (row[0], row)

        for row_num in range(3, sh.nrows):
            raw_row = [
                self.get_cell_value(
                    column_desc[col],
                    unicode(sh.cell_value(row_num, col)),
                    row_num, col)
                for col in xrange(sh.ncols)]
            key, row = row_mapper(raw_row)
            table[key] = row
        return table, column_names

    def get_cell_value(self, column_item, cell_value, row, col):
        type_name = column_item.type_name
        if type_name in self.converters:
            method = self.converters[type_name]
            v = method(cell_value)
            return v
        else:
            tpo = lambda : 1
            if cell_value == u"":
                logger.warning("None value generated for blank cell at %d:%d" % (row, col))
                return None
            v = eval(cell_value)
            struct = self.get_struct(type_name)
            ret = self.check_struct(v, struct)
            if ret is False:
                logger.fatal("error while checking %s at %d:%d" % (cell_value, row, col))
                assert(False)
            return v

    def check_struct(self, v, struct):
        if type(struct) is NodeList:
            if struct.num is not "N" and struct.num != len(v):
                return False
            for i in v:
                iret = self.check_struct(i, struct.etype)
                if iret is False:
                    return False
            return True
        elif type(struct) is NodeTuple:
            if len(struct.etypes) != len(v):
                return False
            for i, j in zip(v, struct.etypes):
                iret = self.check_struct(i, j)
                if iret is False:
                    return False
            return True
        else:
            target_set = self.coercing[struct]
            return type(v) in target_set

    def get_struct(self, type_name):
        if type_name not in self.structs:
            self.structs[type_name] = self.build_struct(type_name)
        return self.structs[type_name]

    def build_struct(self, type_desc):
        def List(e, n):
            return NodeList(e, n)
        def Tuple(*args):
            return NodeTuple([i for i in args])
        Int = type(0)
        Float = type(1.0)
        Str = type(u"")
        N = "N"
        replaced = type_desc.replace("int", "Int").\
            replace("float", "Float").replace("str", "Str").\
            replace("list", "List").replace("tuple", "Tuple")
        struct = eval(replaced, locals(), {})
        return struct

    valid_base_name = re.compile(r"^[a-zA-Z_]\w*$")
    def check_file_name(self, name):
        ret = self.valid_base_name.match(name)
        return ret is not None

    @staticmethod
    def default_emitter(*args):
        return [args]

    @staticmethod
    def model_converter(cell_value):
        return cell_value

    def register_converters(self):
        from plugins.model import fun
        self.converters[u"model"] = fun
        self.converters[u"str"] = lambda x: x
        self.converters[u"comment"] = lambda x: None


class PyExporter(object):
    header_template = """# -*- coding: utf-8 -*-
from wrapper import DataDescription
_reload_all = True

"""

    tail_template = """\nata = DataDescription.DataDict(_Keys, _Data)
"""

    def __init__(self, output_file_path, data_dict, column_names, use_comment):
        self.output_file = open(output_file_path, "wb")
        self.data_dict = data_dict
        self.column_names = column_names
        self.use_comment = use_comment
        self.indent = "\t"
        self.newline = "\n"

    def write(self):
        # header
        self.output_file.write(self.header_template)
        self.write_columns()
        self.write_dict()
        self.write_tail()
        self.output_file.close()

    def write_columns(self):
        fragments = ["_Keys = "]
        d = {}
        for idx, col in enumerate(self.column_names):
            d[col.program_name] = idx
        self.dump(d, 0, fragments)
        self.output_file.write("".join(fragments))

    def write_dict(self):
        fragments = ["\n_Data = "]
        #self.dump(self.data_dict, 0, fragments)
        if self.use_comment:
            cols = self.column_names
        else:
            cols = None
        self.dump_top(self.data_dict, fragments, cols)
        self.output_file.write("".join(fragments))

    def write_tail(self):
        self.output_file.write(self.tail_template)

    def dump(self, data, level, frag):
        if type(data) is dict:
            self.dump_dict(data, level, frag)
        elif type(data) in {list, tuple}:
            self.dump_list(data, level, frag)
        elif type(data) is unicode:
            self.dump_unicode(data, level, frag)
        else:
            self.dump_basic(data, level, frag)

    def dump_list(self, l, level, frag, column_desc=None):
        frag.append(level * self.indent)
        frag.append("(" + self.newline)
        if column_desc:
            for idx, item in enumerate(l):
                self.dump(item, level+1, frag)
                frag.append(", ")
                frag.append("#%s:%s" %
                            (column_desc[idx].program_name.encode("utf-8"),
                             column_desc[idx].column_name.encode("utf-8")))
                frag.append(self.newline)
        else:
            for i in l:
                self.dump(i, level+1, frag)
                frag.append("," + self.newline)
        frag.append(level * self.indent)
        frag.append(")")

    def dump_dict(self, d, level, frag):
        frag.append(level * self.indent)
        frag.append("{" + self.newline)
        for k, v in d.iteritems():
            self.dump(k, level+1, frag)
            frag.append(":" + self.newline)
            self.dump(v, level+2, frag)
            frag.append("," + self.newline)
        frag.append(level * self.indent)
        frag.append("}")

    def dump_basic(self, e, level, frag):
        frag.append(level * self.indent)
        frag.append(e.__repr__())

    def dump_unicode(self, u, level, frag):
        frag.append(level * self.indent)
        frag.append("\"\"\"")
        frag.append(u.encode("utf-8"))
        frag.append("\"\"\"")
        #frag.append(level * self.indent)
        #frag.append(u.__repr__())

    def dump_top(self, data, frag, column_desc):
        frag.append("{" + self.newline)
        for k, v in data.iteritems():
            self.dump(k, 1, frag)
            frag.append(":" + self.newline)
            assert(type(v) in {list, tuple})
            self.dump_list(v, 2, frag, column_desc)
            frag.append("," + self.newline)
        frag.append("}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="python this_script")
    parser.add_argument("-i", help="input directory")
    parser.add_argument("-o", help="output directory")
    parser.add_argument("-r", help="rule directory")
    parser.add_argument("-c", help="whether to use column comment", action="store_true")
    parser.add_argument("-v", help="whether to print trivial processing info", action="store_true")
    ns = parser.parse_args()
    app = App(ns.i, ns.o, ns.r, ns.c, ns.v)
    app.run()


    """
    ex = PyExporter("abcd.py", [], [])

    frag = []
    ex.dump_list([1,2,3,4,[1,2,3]], 0, frag)
    print "".join(frag)

    frag = []
    #ex.dump_dict({1:2, 3:{4:(5,5.5), 6:(7,8)}}, 0, frag)
    d = {
        1: {
            2: (
                "hello",
                "world"
            ),
            3:44
        },
        33: {
        }
    }
    ex.dump_dict(d, 0, frag)
    print "".join(frag)
    """