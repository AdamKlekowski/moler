# -*- coding: utf-8 -*-
"""
Generic Unix/Linux module
"""
import re

from moler.exceptions import CommandFailure
from moler.textualgeneric import TextualGeneric

__author__ = 'Marcin Usielski'
__copyright__ = 'Copyright (C) 2018, Nokia'
__email__ = 'marcin.usielski@nokia.com'


class GenericUnix(TextualGeneric):
    _re_fail = re.compile(r'command not found|No such file or directory|running it may require superuser privileges')

    def on_new_line(self, line, is_full_line):
        """
        Method to parse command output. Will be called after line with command echo.
        Write your own implementation but don't forget to call on_new_line from base class
        :param line: Line to parse, new lines are trimmed
        :param is_full_line:  False for chunk of line; True on full line (NOTE: new line character removed)
        :return: Nothing
        """
        if is_full_line and self.is_failure_indication(line):
            self.set_exception(CommandFailure(self, "command failed in line '{}'".format(line)))
        return super(GenericUnix, self).on_new_line(line, is_full_line)

    def is_failure_indication(self, line):
        return self._regex_helper.search_compiled(GenericUnix._re_fail, line)
