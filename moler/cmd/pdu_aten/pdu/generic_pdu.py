# -*- coding: utf-8 -*-
"""
PDU generic module for commands in state PDU.
"""

import six
import abc
from moler.cmd.pdu_aten.generic_pdu_aten import GenericPduAten

__author__ = 'Marcin Usielski'
__copyright__ = 'Copyright (C) 2020, Nokia'
__email__ = 'marcin.usielski@nokia.com'


@six.add_metaclass(abc.ABCMeta)
class GenericPdu(GenericPduAten):
    def __init__(self, connection, prompt=None, newline_chars=None, runner=None):
        """
        Base class for Aten PDU commands in state PDU.

        :param connection: connection to device.
        :param prompt: expected prompt sending by device after command execution. Maybe String or compiled re.
        :param newline_chars:  new line chars on device (a list).
        :param runner: runner to run command.
        """

        super(GenericPdu, self).__init__(connection=connection, prompt=prompt, newline_chars=newline_chars,
                                         runner=runner)

        def on_new_line(self, )