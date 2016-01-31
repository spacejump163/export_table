# -*- encoding: utf-8 -*-

def build_record(attrs):
    class Record(object):
        __slots__ = attrs

        def __init__(self, data_list):
            for i, e in enumerate(data_list):
                setattr(self, self.__slots__[i], e)

        def to_tuple(self):
            return tuple([getattr(self, field) for field in self.__slots__])

    return Record


if __name__ == "__main__":
    pt_class = build_record(("x", "y"))
    pt0 = pt_class((1,2))
    tup = pt0.to_tuple()
    print(tup)
    pt0.x = 23
    pt0.y = 5
    tup = pt0.to_tuple()
    print(tup)

    real_class = build_record(("i", "j"))
    r0 = real_class((1,-1))
    print(r0.to_tuple())
    print(id(real_class))
    print(id(pt_class))
