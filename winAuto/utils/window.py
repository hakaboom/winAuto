# -*- coding: utf-8 -*-
import ctypes
from ctypes import wintypes


class windowInfo(ctypes.Structure):
    def __str__(self) -> str:
        return (
            "windowInfo(" + ", ".join([key + ":" + str(getattr(self, key)) for key, value in self._fields_]) + ")"
        )


windowInfo._fields_ = [
    ("cbSize", wintypes.DWORD),
    ("rcWindow", wintypes.RECT),
    ("rcClient", wintypes.RECT),
    ("dwStyle", wintypes.DWORD),
    ("dwExStyle", wintypes.DWORD),
    ("dwWindowStatus", wintypes.DWORD),
    ("cxWindowBorders", wintypes.UINT),
    ("cyWindowBorders", wintypes.UINT),
    ("atomWindowType", wintypes.ATOM),
    ("wCreatorVersion", wintypes.WORD),
]


def GetWindowInfo(hwnd: int):
    pwi = windowInfo()
    ctypes.windll.user32.GetWindowInfo(hwnd, ctypes.byref(pwi))
    return pwi
