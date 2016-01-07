# -*- encoding: utf-8 -*-
import os
cnt = 0
def row_mapper(row):
    global cnt
    cnt += 1
    return cnt, row
	
def emitter(output_file_path, data, column_names):
	n, e = os.path.splitext(output_file_path)
	return [
		(n + "0" + e, data, column_names),
		(n + "1" + e, data, column_names),
	]