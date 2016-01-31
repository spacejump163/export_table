# -*- encoding: utf-8 -*-

import argparse
import logging
import sys

logger = logging.getLogger(__name__)


class Param(object):
    def __init__(self):
        self.parse_args()
        self.read_targets()

    def parse_args(self):
        parser = argparse.ArgumentParser(
            description="denglx's 2nd excel to python data exporting tool")
        parser.add_argument("--input", help="input directory")
        parser.add_argument("--output", nargs="*", help="output directory")
        parser.add_argument("--rule", help="rule directory")
        parser.add_argument("--tmp", help="intermediate directory", default="tmp")
        parser.add_argument(
            "--comment",
            help="whether to use column comment", action="store_true")
        parser.add_argument(
            "--verbose",
            help="whether to print trivial processing info",
            action="store_true")
        parser.add_argument("--config", nargs="+", help="config file")

        ns = parser.parse_args()
        self.input_dir = self.get_unicode(ns.input)
        self.output_dirs = [self.get_unicode(i) for i in ns.output]
        self.rule_dir = self.get_unicode(ns.rule)
        self.use_comment = ns.comment
        self.verbose_mode = ns.verbose
        self.config_files = [self.get_unicode(i) for i in ns.config]
        self.tmp_dir = self.get_unicode(ns.tmp)

        if self.verbose_mode:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.WARNING)
        logging.getLogger().addHandler(logging.StreamHandler())

    def read_targets(self):
        self.configs = {}
        if self.config_files is None:
            return
        for config_file in self.config_files:
            d = {}
            logger.info(">start reading config file %s" % config_file)
            execfile(config_file, {}, d)
            logger.info("<finished reading config file %s" % config_file)
            self.configs[config_file]= d["targets"]

    @staticmethod
    def get_unicode(s):
        if type(s) is unicode:
            return s
        try:
            return unicode(s, "u8")
        except UnicodeDecodeError:
            pass
        try:
            return unicode(s, "gbk")
        except UnicodeDecodeError:
            pass
        try:
            return unicode(s, "u16")
        except UnicodeDecodeError:
            pass
        logger.fatal("FUCK, what kind of encoding are you using?")
        assert(False)


param = Param()
