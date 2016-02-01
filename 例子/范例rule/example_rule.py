# -*- encoding: utf-8 -*-

def column_mapper(column_definitions):
    from collections import namedtuple
    Column = namedtuple("Column", ("program_name", "design_name"))
    key_index = 0
    added_column = [
        Column("added0", "generate0"),
        Column("added1", "generated1")
    ]
    return key_index, column_definitions[:2] + added_column

def row_mapper(output_row, input_row):
    output_row.added1 = input_row.task
    output_row.name = input_row.name + u"changed"
    return True

def matrix_mapper(matrix):
    for i, row in enumerate(matrix):
        ii = i + 1
        if ii == len(matrix):
            ii = 0
        row.added0 = matrix[ii].name

