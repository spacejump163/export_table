# -*- encoding: utf-8 -*-


class RowRecord(object):
    __slots__ = ("_keys", "_data")
    def __init__(self, keys, datas):
        self._keys = keys
        self._data = datas

    def __getitem__(self, key):
        index = self._keys[key]
        return self._data[index]

    def keys(self):
        return self._keys.keys()

    def values(self):
        return self._data

    def get(self, key, default = None):
        if key not in self._keys:
            return default
        return self[key]

    def __getattr__(self, name):
        return self.get(name)

    def __contains__(self, key):
        return key in self._keys

    def data(self):
        data = {}
        for name, index in self._keys.iteritems():
            data[name] = self._data[index]
        return data


class DataDict(object):
    __slots__ = ("_columns", "_index", "_matrix")
    def __init__(self, columns, index, matrix):
        self._columns = columns
        self._index = index
        self._matrix = matrix

    def __getitem__(self, item):
        row_idx = self._index[item]
        data = self._matrix[row_idx]
        return RowRecord(self._columns, data)

    def iteritems(self):
        for k, idx in self._index.iteritems():
            v = self._matrix[idx]
            yield k, v

    def iterkeys(self):
        for k in self._index:
            yield k

    def itervalues(self):
        for k in self._index:
            yield self._matrix[k]

    def __contains__(self, item):
        return item in self._index

    def get(self, key, default=None):
        if key not in self._index:
            return default
        return self[key]

