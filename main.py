from winAuto.cap_methods.windowsGraphicsCapture import WindowGraphicsCapture
from winAuto.win import Win
from winAuto.utils.window import GetWindowInfo
import win32api
import win32gui
from baseImage import Image
#
# print(Win.get_all_hwnd())


a = Win(handle_title='retire')
a.screenshot().save2path('test.png')
