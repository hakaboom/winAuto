import cv2.cv2
import win32gui
import time
import ctypes
from winAuto.win import Win
from baseImage import IMAGE
from pywinauto import mouse, keyboard
from pywinauto.win32functions import GetSystemMetrics
from pywinauto.application import Application
# a = Win(handle_title='Clash for Windows')
# time.sleep(2)
# a = mouse
# a.press('left', coords=(880, 170))
# time.sleep(10)
# a.release('left', coords=(880, 170))

# print(a.find_window(hwnd_class='Google Chrome'))
app = Application()
app.window(best_match='Chrome')