import cv2.cv2
import win32gui

from winAuto.win import Win
from baseImage import IMAGE

#
# a = Win()
# IMAGE(a.screenshot()).save2path('test.png')
import win32gui
import win32api

# from pymouse import PyMouse
hwnd_title = {}

def get_all_hwnd(hwnd, mouse):
    if (win32gui.IsWindow(hwnd) and
        win32gui.IsWindowEnabled(hwnd) and
        win32gui.IsWindowVisible(hwnd)):
        hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})


win32gui.EnumWindows(get_all_hwnd, 0)

# m = PyMouse()

for h, t in hwnd_title.items():
    if t :
        print(h, t)
        if t == '米格尔':
            left, top, right, bottom = win32gui.GetWindowRect(h)
            print(left,top,right,bottom)