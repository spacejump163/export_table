# -*- encoding: utf-8 -*-

class DataType(object):
    @staticmethod
    def is_comment():
        return False

class CommentType(DataType):
    @staticmethod
    def parse(fragment):
        return None

    @staticmethod
    def to_declaration():
        return "comment"

    @staticmethod
    def is_comment():
        return True


class StringType(DataType):
    @staticmethod
    def parse(fragment):
        return unicode(fragment)

    @staticmethod
    def to_declaration():
        return "str"


class IntType(DataType):
    @staticmethod
    def parse(fragment):
        try:
            return int(fragment)
        except ValueError as e:
            f = float(fragment)
            intf = int(f)
            if f == intf:
                return int(f)
            else:
                raise e

    @staticmethod
    def to_declaration():
        return "int"


class RealType(DataType):
    @staticmethod
    def parse(fragment):
        return float(fragment)

    @staticmethod
    def to_declaration():
        return "float"


class TupleType(DataType):
    def __init__(self, *children):
        for i, c in enumerate(children):
            if type(c) == str:
                self.delimit = c
                self.children = children[:i] + children[i+1:]
                return
        self.delimit = "|"
        self.children = children

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, TupleType):
            return False
        if self.children != other.children:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def parse(self, fragment):
        frags = fragment.split(self.delimit)
        if len(frags) != len(self.children):
            raise ValueError("tuple: number of member doesn't match declaration")
        else:
            return tuple([tp.parse(f) for tp, f in zip(self.children, frags)])

    def to_declaration(self):
        c = ",".join([repr(self.delimit)] + [i.to_declaration() for i in self.children])
        s = "tuple({content})".format(content=c)
        return s


class ListType(DataType):
    def __init__(self, proto, count, delimit=";"):
        self.delimit = delimit
        self.proto = proto
        self.count = count

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, ListType):
            return False
        if self.proto == other.proto:
            return False
        if self.count != other.count:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def parse(self, fragment):
        frags = fragment.split(self.delimit)
        if self.count != -1 and self.count != len(frags):
            raise ValueError("list: number of member doesn't match declaration")
        return tuple([self.proto.parse(f) for f in frags])

    def to_declaration(self):
        c = ",".join([repr(self.delimit), self.proto.to_declaration(), repr(self.count)])
        s = "list({content})".format(content=c)
        return s


exec_global = {
    "StringType": StringType,
    "IntType": IntType,
    "RealType": RealType,
    "TupleType": TupleType,
    "ListType": ListType,
    "comment": CommentType,
    "N": -1,
}

_cache = {}


def get_type(def_str):
    if def_str not in _cache:
        tp = build_type(def_str)
        compact_declaration = tp.to_declaration()
        if compact_declaration in _cache:
            _cache[def_str] = _cache[compact_declaration]
        else:
            _cache[compact_declaration] = _cache[def_str] = tp
    return _cache[def_str]


def build_type(desc):
    src = desc.replace("str", "StringType()").\
    replace("int", "IntType()").replace("float", "RealType()").\
    replace("tuple", "TupleType").replace("list", "ListType")
    type_info = eval(src, exec_global, {})
    return type_info


if __name__ == "__main__":
    t_str = build_type("str")
    r = t_str.parse("hello")
    assert(r == "hello")

    t_tuple = build_type('tuple(",", int, int, float, str)')
    r = t_tuple.parse("1,2,3,444")
    assert(r == (1, 2, 3.0, u"444"))

    t_list_tuple = build_type('list(tuple(",", int, int, float, str), N, "|")')
    r = t_list_tuple.parse(u"1,2,3,好人|2,3,4,死人|2,3,4,坏人人")
    assert(r == (
        (1, 2, 3, u"好人"),
        (2, 3, 4, u"死人"),
        (2, 3, 4, u"坏人人"),
    ))

    t_type0 = get_type('list(tuple(",", int, int, float, str), N, "|")')
    t_type1 = get_type('list(tuple(",", int, int, float, str), N, "|")')
    t_type2 = get_type('list(tuple(",", int, int, float, str), N, "|")')
    assert(t_type1 == t_type1)

    print("all ok")