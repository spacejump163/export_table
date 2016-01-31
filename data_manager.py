# -*- encoding:utf-8 -*-

import sys
import importlib
import data_description
#from hexm.common import portable


class DataManager(object):
    def __init__(self):
        self.import_root = None
        self.modules = {} # { name: module }

    def __getattr__(self, name):
        return self.get(name)

    def get(self, name):
        if name not in self.modules:
            module = self.load_module(name)
            data_desc = data_description.DataDict(
                module.columns, module.index, module.table)
            self.modules[name] = data_desc
        return self.modules[name]



    def load_module(self, name):
        module = importlib.import_module(name, self.import_root)
        self.modules[name] = module
        return module


if __name__ == "__main__":
    dm = DataManager()
    print(dm.get("tmp.character")["周利"].task)
    print(dm.get("tmp.character")["李新"].name)
    print(dm.get("tmp.instances.i0")[1].position)