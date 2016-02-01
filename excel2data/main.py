# -*- encoding: utf-8 -*-

import logging
import os
from collections import namedtuple
import shutil
import distutils.dir_util as dir_util
import sys

from excel2data.param import param
from excel2data.table import Table
from excel2data import default_rule
from excel2data.export import PyExporter
from excel2data.record import build_record

logger = logging.getLogger(__name__)


class App(object):
    def __init__(self):
        self.rule_module_cache = {}
        self.table_cache = {}
        self.sheet_cache = {}
        self.merged_table_cache = {}
        self.clean_tmp()
        self.process_config_files()
        self.build_package()
        self.copy_to_output()

    def process_config_files(self):
        for file_name, targets in param.configs.items():
            logger.info(">start processing config file: %s" % file_name)
            for target_def in targets:
                self.process_one_target(target_def)
            logger.info("<end processing config file: %s" % file_name)

    def process_one_target(self, target_def):
        target_module_name = target_def[0]
        rule_file = target_def[1]
        source_tuples = target_def[2:]
        tables = []
        for t in source_tuples:
            file_name, sheet_name = t
            real_file_name = self.get_input_path(file_name)
            rt = real_file_name, sheet_name
            logger.info(">begin processing source %s" % repr(rt))
            table_data = self.get_sheet(real_file_name, sheet_name)
            logger.info("<end processing source %s" % repr(rt))
            tables.append(table_data)
        merged_table = self.get_merged_tables(tables)
        if rule_file:
            mapper = self.get_rule_module(rule_file)
        else:
            mapper = default_rule.column_mapper, default_rule.row_mapper, default_rule.matrix_mapper
        mapped_table = self.map_table(merged_table, mapper)
        self.write_table(target_module_name, mapped_table)

    def get_input_path(self, pth):
        pth = os.path.join(param.input_dir, pth)
        return pth

    def clean_tmp(self):
        shutil.rmtree(param.tmp_dir, True)
        os.makedirs(param.tmp_dir)

    def copy_to_output(self):
        for dst in param.output_dirs:
            dir_util.copy_tree(param.tmp_dir, dst)

    def get_merged_tables(self, tables):
        s = frozenset([t.signature for t in tables])
        if s not in self.merged_table_cache:
            merged = Table.merge(tables)
            self.merged_table_cache[s] = merged
        return self.merged_table_cache[s]

    def write_table(self, module_name, table):
        logger.info(">start writing to module %s" % module_name)
        exporter = PyExporter(module_name, table)
        exporter.run()
        logger.info("<end writing to module %s" % module_name)

    def get_sheet(self, file_name, sheet_name):
        sig = file_name, sheet_name
        if sig not in self.sheet_cache:
            logger.info("sheet %s not in cache")
            table = Table()
            table.build_from_sheet(file_name, sheet_name)
            self.sheet_cache[sig] = table
        return self.sheet_cache[sig]

    def get_rule_module(self, path):
        abs_path = os.path.abspath(os.path.join(param.rule_dir, path))
        if abs_path not in self.rule_module_cache:
            d = {}
            safe_path = abs_path.encode(sys.getfilesystemencoding())
            execfile(safe_path, {}, d)
            column_mapper = d.get("column_mapper", default_rule.column_mapper)
            row_mapper = d.get("row_mapper", default_rule.row_mapper)
            matrix_mapper = d.get("matrix_mapper", default_rule.matrix_mapper)
            self.rule_module_cache[abs_path] = (column_mapper, row_mapper, matrix_mapper)
        return self.rule_module_cache[abs_path]

    def map_table(self, merged_table, mapper):
        copied_column = [i.clone() for i in merged_table.columns]
        input_type = namedtuple("input",
                                [c.program_name for c in merged_table.columns])
        kidx, mapped_column = mapper[0](copied_column)
        names = set()
        for mc in mapped_column:
            dup = mc.program_name in names
            if dup:
                logger.fatal("duplicated column names")
                assert(mc.program_name not in names)
            names.add(mc.program_name)
        output_type = build_record([c.program_name for c in mapped_column])
        mapping = self.get_index_mapping(mapped_column, merged_table.columns)
        mapped_table = Table()
        mapped_table.key_column = kidx
        mapped_table.columns = mapped_column
        tmp_matrix = []
        for row in merged_table.matrix:
            input_row = input_type(*row)
            output_list = [None if i is None else row[i] for i in mapping]
            output_row = output_type(output_list)
            preserve = mapper[1](output_row, input_row)
            if preserve:
                #mapped_table.matrix.append(output_row.to_tuple())
                tmp_matrix.append(output_row)
        mapper[2](tmp_matrix)
        for row in tmp_matrix:
            mapped_table.matrix.append(row.to_tuple())
        return mapped_table

    @staticmethod
    def get_index_mapping(output_column, input_column):
        ret = []
        name2column = {}
        for i, c in enumerate(input_column):
            name2column[c.program_name] = i
        for i, c in enumerate(output_column):
            if c.program_name in name2column:
                idx = name2column[c.program_name]
                ret.append(idx)
            else:
                ret.append(None)
        return ret

    def build_package(self):
        ifn = "__init__.py"
        for dir_name, dirs, files in os.walk(param.tmp_dir):
            if ifn not in files:
                self.create_empty_file(os.path.join(dir_name, ifn))

    def create_empty_file(self, path):
        with open(path, "wb") as f:
            pass


def run():
    App()
