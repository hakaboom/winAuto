# -*- coding: utf-8 -*-
import pywintypes


class WinBaseError(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return repr(self.message)


class WinConnectError(WinBaseError):
    """ connect hwnd time out """
