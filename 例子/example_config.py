# -*- encoding: utf-8 -*-

targets = [
    ("format_example", None,
        (u"格式例子.xlsx", u"一些例子"),
    ),
    ("instances.i0", None,
        (u"副本/副本0.xlsx", u"Sheet0"),
    ),
    ("instances.i1", None,
        (u"副本/副本1.xlsx", u"Sheet0"),
    ),
    ("instances.i_all", None,
        (u"副本/副本0.xlsx", u"Sheet0"),
        (u"副本/副本1.xlsx", u"Sheet0"),
    ),
    ("character", None,
        (u"人物/人物-fj.xlsx", u"Sheet0"),
        (u"人物/人物-dlx.xlsx", u"Sheet0"),
    ),
    ("modify_example", "example_rule.py",
        (u"人物/人物-fj.xlsx", u"Sheet0"),
    )
]